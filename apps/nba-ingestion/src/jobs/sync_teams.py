import logging
import json
from db import get_connection
from nba.client import get_static_teams
from nba.transforms import team_logo_url

logger = logging.getLogger(__name__)


def sync_teams() -> None:
    teams = get_static_teams()

    sql = """
    insert into public.teams (
        team_id,
        full_name,
        abbreviation,
        nickname,
        city,
        state,
        year_founded,
        logo_url,
        raw
    )
    values (
        %(team_id)s,
        %(full_name)s,
        %(abbreviation)s,
        %(nickname)s,
        %(city)s,
        %(state)s,
        %(year_founded)s,
        %(logo_url)s,
        %(raw)s::jsonb
    )
    on conflict (team_id)
    do update set
        full_name = excluded.full_name,
        abbreviation = excluded.abbreviation,
        nickname = excluded.nickname,
        city = excluded.city,
        state = excluded.state,
        year_founded = excluded.year_founded,
        logo_url = excluded.logo_url,
        raw = excluded.raw,
        updated_at = now();
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            for team in teams:
                team_id = team["id"]

                cur.execute(
                    sql,
                    {
                        "team_id": team_id,
                        "full_name": team.get("full_name"),
                        "abbreviation": team.get("abbreviation"),
                        "nickname": team.get("nickname"),
                        "city": team.get("city"),
                        "state": team.get("state"),
                        "year_founded": team.get("year_founded"),
                        "logo_url": team_logo_url(team_id),
                        "raw": json.dumps(team),
                    },
                )

        conn.commit()

    logger.info("Synced %s teams", len(teams))