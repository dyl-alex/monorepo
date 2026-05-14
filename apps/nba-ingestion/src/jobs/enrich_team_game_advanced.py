import logging
import math
import time
from datetime import datetime

from config import get_settings
from db import get_connection
from nba.client import get_boxscore_advanced

logger = logging.getLogger(__name__)


def _to_int(value):
    if value is None or value == "":
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return int(value)


def _to_float(value):
    if value is None or value == "":
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return float(value)


def enrich_team_game_advanced(season: str, limit: int | None = None) -> None:
    settings = get_settings()
    commit_batch_games = settings.sync_commit_batch_games
    commit_interval_seconds = 20

    logger.info("Starting enrich_team_game_advanced season=%s limit=%s", season, limit)

    limit_clause = ""
    params: dict[str, object] = {"season_id": season}
    if limit is not None and limit > 0:
        limit_clause = "limit %(limit)s"
        params["limit"] = limit

    games_sql = f"""
    select distinct tgs.game_id
    from public.team_game_stats tgs
    where tgs.season_id = %(season_id)s
      and (
        tgs.advanced_sync_status is null
        or tgs.advanced_sync_status <> 'success'
        or tgs.advanced_synced_at is null
      )
    order by tgs.game_id
    {limit_clause}
    """

    update_success_sql = """
    update public.team_game_stats
    set
      possessions = %(possessions)s,
      pace = %(pace)s,
      offensive_rating = %(offensive_rating)s,
      defensive_rating = %(defensive_rating)s,
      net_rating = %(net_rating)s,
      assist_pct = %(assist_pct)s,
      rebound_pct = %(rebound_pct)s,
      true_shooting_pct = %(true_shooting_pct)s,
      effective_field_goal_pct = %(effective_field_goal_pct)s,
      turnover_pct = %(turnover_pct)s,
      pie = %(pie)s,
      source_endpoint = %(source_endpoint)s,
      advanced_synced_at = %(advanced_synced_at)s,
      advanced_sync_status = %(advanced_sync_status)s,
      advanced_sync_error = %(advanced_sync_error)s,
      updated_at = now()
    where game_id = %(game_id)s
      and team_id = %(team_id)s
    """

    update_error_sql = """
    update public.team_game_stats
    set
      advanced_synced_at = %(advanced_synced_at)s,
      advanced_sync_status = %(advanced_sync_status)s,
      advanced_sync_error = %(advanced_sync_error)s,
      updated_at = now()
    where game_id = %(game_id)s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(games_sql, params)
            game_ids = [row[0] for row in cur.fetchall()]

    processed_games = 0
    success_games = 0
    failed_games = 0
    updated_rows = 0
    last_commit_at = time.monotonic()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for game_id in game_ids:
                processed_games += 1
                logger.info("Enriching advanced team stats game_id=%s (%s/%s)", game_id, processed_games, len(game_ids))
                try:
                    advanced = get_boxscore_advanced(game_id)
                    now_utc = datetime.utcnow()
                    for row in advanced.get("team_stats", []):
                        team_id = _to_int(row.get("TEAM_ID"))
                        if team_id is None:
                            continue
                        cur.execute(
                            update_success_sql,
                            {
                                "game_id": game_id,
                                "team_id": team_id,
                                "possessions": _to_float(row.get("POSS")),
                                "pace": _to_float(row.get("PACE")),
                                "offensive_rating": _to_float(row.get("OFF_RATING")),
                                "defensive_rating": _to_float(row.get("DEF_RATING")),
                                "net_rating": _to_float(row.get("NET_RATING")),
                                "assist_pct": _to_float(row.get("AST_PCT")),
                                "rebound_pct": _to_float(row.get("REB_PCT")),
                                "true_shooting_pct": _to_float(row.get("TS_PCT")),
                                "effective_field_goal_pct": _to_float(row.get("EFG_PCT")),
                                "turnover_pct": _to_float(row.get("TM_TOV_PCT")),
                                "pie": _to_float(row.get("PIE")),
                                "source_endpoint": "boxscoreadvancedv2",
                                "advanced_synced_at": now_utc,
                                "advanced_sync_status": "success",
                                "advanced_sync_error": None,
                            },
                        )
                        updated_rows += 1
                    success_games += 1
                except Exception as exc:
                    failed_games += 1
                    error_message = f"{type(exc).__name__}: {exc}"
                    logger.warning("Advanced enrichment failed game_id=%s error=%s", game_id, error_message)
                    cur.execute(
                        update_error_sql,
                        {
                            "game_id": game_id,
                            "advanced_synced_at": datetime.utcnow(),
                            "advanced_sync_status": "error",
                            "advanced_sync_error": error_message[:500],
                        },
                    )

                now_tick = time.monotonic()
                if (processed_games % commit_batch_games == 0) or ((now_tick - last_commit_at) >= commit_interval_seconds):
                    conn.commit()
                    last_commit_at = now_tick
                    logger.info(
                        "Checkpoint commit advanced enrichment: processed_games=%s success_games=%s failed_games=%s updated_rows=%s",
                        processed_games,
                        success_games,
                        failed_games,
                        updated_rows,
                    )

        conn.commit()

    logger.info(
        "Completed enrich_team_game_advanced season=%s processed_games=%s success_games=%s failed_games=%s updated_rows=%s",
        season,
        processed_games,
        success_games,
        failed_games,
        updated_rows,
    )
