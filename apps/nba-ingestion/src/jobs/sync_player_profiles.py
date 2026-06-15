import logging
import math
import time
from datetime import datetime

from config import get_settings
from db import get_connection
from nba.client import get_common_player_info
from raw_store import jsonb_dumps, store_raw_api_response

logger = logging.getLogger(__name__)


def _to_int(value):
    if value is None or value == "":
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return int(value)


def _parse_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    date_value = str(value).strip()
    if not date_value:
        return None
    if "T" in date_value:
        return datetime.fromisoformat(date_value.replace("Z", "+00:00")).date()
    return datetime.strptime(date_value[:10], "%Y-%m-%d").date()


def _height_inches(value) -> int | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    if "-" not in text:
        return None
    feet, inches = text.split("-", 1)
    return (int(feet) * 12) + int(inches)


def _player_ids_to_sync(only_missing: bool, limit: int | None = None) -> list[int]:
    if only_missing:
        sql = """
        select p.player_id
        from public.players p
        left join public.player_profiles pp on pp.player_id = p.player_id
        where pp.player_id is null
        order by p.player_id
        """
    else:
        sql = "select player_id from public.players order by player_id"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            player_ids = [row[0] for row in cur.fetchall()]

    if limit is not None and limit > 0:
        return player_ids[:limit]
    return player_ids


def sync_player_profiles(only_missing: bool = False, limit: int | None = None) -> None:
    settings = get_settings()
    commit_batch_players = settings.sync_commit_batch_games
    profile_delay_seconds = settings.nba_api_profile_delay_seconds
    player_ids = _player_ids_to_sync(only_missing, limit=limit)
    logger.info(
        "Starting sync_player_profiles players=%s only_missing=%s limit=%s profile_delay_seconds=%s",
        len(player_ids),
        only_missing,
        limit,
        profile_delay_seconds,
    )

    upsert_sql = """
    insert into public.player_profiles (
      player_id,
      birthdate,
      age,
      height,
      height_inches,
      weight_lbs,
      position,
      jersey,
      school,
      country,
      draft_year,
      draft_round,
      draft_number,
      greatest_75_flag,
      raw
    )
    values (
      %(player_id)s,
      %(birthdate)s,
      %(age)s,
      %(height)s,
      %(height_inches)s,
      %(weight_lbs)s,
      %(position)s,
      %(jersey)s,
      %(school)s,
      %(country)s,
      %(draft_year)s,
      %(draft_round)s,
      %(draft_number)s,
      %(greatest_75_flag)s,
      %(raw)s::jsonb
    )
    on conflict (player_id)
    do update set
      birthdate = excluded.birthdate,
      age = excluded.age,
      height = excluded.height,
      height_inches = excluded.height_inches,
      weight_lbs = excluded.weight_lbs,
      position = excluded.position,
      jersey = excluded.jersey,
      school = excluded.school,
      country = excluded.country,
      draft_year = excluded.draft_year,
      draft_round = excluded.draft_round,
      draft_number = excluded.draft_number,
      greatest_75_flag = excluded.greatest_75_flag,
      raw = excluded.raw,
      updated_at = now();
    """

    synced_rows = 0
    missing_rows = 0
    failed_rows = 0
    processed_rows = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for player_id in player_ids:
                processed_rows += 1
                try:
                    response = get_common_player_info(player_id)
                    store_raw_api_response(
                        endpoint_name="commonplayerinfo",
                        endpoint_params={"player_id": player_id},
                        response_json=response,
                        player_id=player_id,
                    )
                    rows = response.get("common_player_info", [])
                    if not rows:
                        missing_rows += 1
                        logger.warning("No CommonPlayerInfo row found player_id=%s", player_id)
                        continue

                    row = rows[0]
                    height = row.get("HEIGHT")
                    cur.execute(
                        upsert_sql,
                        {
                            "player_id": player_id,
                            "birthdate": _parse_date(row.get("BIRTHDATE")),
                            "age": None,
                            "height": height,
                            "height_inches": _height_inches(height),
                            "weight_lbs": _to_int(row.get("WEIGHT")),
                            "position": row.get("POSITION"),
                            "jersey": row.get("JERSEY"),
                            "school": row.get("SCHOOL"),
                            "country": row.get("COUNTRY"),
                            "draft_year": row.get("DRAFT_YEAR"),
                            "draft_round": row.get("DRAFT_ROUND"),
                            "draft_number": row.get("DRAFT_NUMBER"),
                            "greatest_75_flag": None,
                            "raw": jsonb_dumps(response),
                        },
                    )
                    synced_rows += 1
                except Exception as exc:
                    failed_rows += 1
                    logger.warning(
                        "Skipping failed sync_player_profiles player_id=%s error=%s: %s",
                        player_id,
                        type(exc).__name__,
                        str(exc)[:500],
                    )

                if processed_rows % commit_batch_players == 0:
                    conn.commit()
                    logger.info(
                        "Checkpoint commit player profiles: processed_rows=%s synced_rows=%s missing_rows=%s failed_rows=%s",
                        processed_rows,
                        synced_rows,
                        missing_rows,
                        failed_rows,
                    )

                if profile_delay_seconds > 0:
                    time.sleep(profile_delay_seconds)

        conn.commit()

    if player_ids and synced_rows == 0 and failed_rows > 0:
        raise RuntimeError(f"sync_player_profiles failed for all {failed_rows} attempted players")

    logger.info(
        "Completed sync_player_profiles processed_rows=%s synced_rows=%s missing_rows=%s failed_rows=%s",
        processed_rows,
        synced_rows,
        missing_rows,
        failed_rows,
    )
