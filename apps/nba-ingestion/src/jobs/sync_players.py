import logging
import json
from db import get_connection
from nba.client import get_static_players
from nba.transforms import player_headshot_url

logger = logging.getLogger(__name__)


def split_name(full_name: str) -> tuple[str | None, str | None]:
    parts = full_name.split(" ", 1)
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]


def sync_players() -> None:
    players = get_static_players()

    sql = """
    insert into public.players (
        player_id,
        first_name,
        last_name,
        full_name,
        is_active,
        headshot_url,
        raw
    )
    values (
        %(player_id)s,
        %(first_name)s,
        %(last_name)s,
        %(full_name)s,
        %(is_active)s,
        %(headshot_url)s,
        %(raw)s::jsonb
    )
    on conflict (player_id)
    do update set
        first_name = excluded.first_name,
        last_name = excluded.last_name,
        full_name = excluded.full_name,
        is_active = excluded.is_active,
        headshot_url = excluded.headshot_url,
        raw = excluded.raw,
        updated_at = now();
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            for player in players:
                player_id = player["id"]
                full_name = player["full_name"]
                first_name, last_name = split_name(full_name)

                cur.execute(
                    sql,
                    {
                        "player_id": player_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": full_name,
                        "is_active": player.get("is_active"),
                        "headshot_url": player_headshot_url(player_id),
                        "raw": json.dumps(player),
                    },
                )

        conn.commit()

    logger.info("Synced %s players", len(players))