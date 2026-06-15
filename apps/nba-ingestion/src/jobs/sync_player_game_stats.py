import logging
import math
import re
import time
from datetime import datetime

from config import get_settings
from db import get_connection
from nba.client import get_league_game_log
from raw_store import jsonb_dumps, store_raw_api_response

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


def _parse_minutes(value) -> float | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    iso_match = re.match(r"^PT(\d+)M(?:(\d+(?:\.\d+)?)S)?$", text)
    if iso_match:
        minutes = float(iso_match.group(1))
        seconds = float(iso_match.group(2) or 0.0)
        return round(minutes + (seconds / 60.0), 3)
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:
            minutes = float(parts[0])
            seconds = float(parts[1])
            return round(minutes + (seconds / 60.0), 3)
    return _to_float(text)


def _parse_matchup(matchup: str | None) -> tuple[bool | None, str | None]:
    if not matchup:
        return None, None
    text = matchup.strip()
    if " vs. " in text:
        _, opp_abbr = text.split(" vs. ", 1)
        return True, opp_abbr.strip()
    if " @ " in text:
        _, opp_abbr = text.split(" @ ", 1)
        return False, opp_abbr.strip()
    return None, None


def _existing_player_stat_keys(season: str, season_type: str) -> set[tuple[str, int, int]]:
    sql = """
    select game_id, player_id, team_id
    from public.player_game_stats
    where season_id = %(season_id)s
      and season_type = %(season_type)s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"season_id": season, "season_type": season_type})
            return {(row[0], row[1], row[2]) for row in cur.fetchall()}


def sync_player_game_stats(season: str, season_type: str | None = None, only_missing: bool = False) -> None:
    settings = get_settings()
    season_type = season_type or settings.default_season_type
    commit_batch_games = settings.sync_commit_batch_games
    commit_interval_seconds = 20

    logger.info("Starting baseline sync_player_game_stats season=%s season_type=%s", season, season_type)

    rows = get_league_game_log(
        season=season,
        season_type=season_type,
        player_or_team_abbreviation="P",
    )
    store_raw_api_response(
        endpoint_name="leaguegamelog",
        endpoint_params={
            "season": season,
            "season_type": season_type,
            "player_or_team_abbreviation": "P",
        },
        response_json=rows,
        season_id=season,
    )

    upsert_sql = """
    insert into public.player_game_stats (
      game_id,
      player_id,
      team_id,
      opponent_team_id,
      season_id,
      season_type,
      game_date,
      team_abbreviation,
      opponent_abbreviation,
      is_home,
      started,
      position,
      minutes,
      points,
      rebounds,
      offensive_rebounds,
      defensive_rebounds,
      assists,
      steals,
      blocks,
      turnovers,
      personal_fouls,
      plus_minus,
      field_goals_made,
      field_goals_attempted,
      field_goal_pct,
      three_pointers_made,
      three_pointers_attempted,
      three_point_pct,
      free_throws_made,
      free_throws_attempted,
      free_throw_pct,
      source_endpoint,
      raw,
      fetched_at
    )
    values (
      %(game_id)s,
      %(player_id)s,
      %(team_id)s,
      %(opponent_team_id)s,
      %(season_id)s,
      %(season_type)s,
      %(game_date)s,
      %(team_abbreviation)s,
      %(opponent_abbreviation)s,
      %(is_home)s,
      %(started)s,
      %(position)s,
      %(minutes)s,
      %(points)s,
      %(rebounds)s,
      %(offensive_rebounds)s,
      %(defensive_rebounds)s,
      %(assists)s,
      %(steals)s,
      %(blocks)s,
      %(turnovers)s,
      %(personal_fouls)s,
      %(plus_minus)s,
      %(field_goals_made)s,
      %(field_goals_attempted)s,
      %(field_goal_pct)s,
      %(three_pointers_made)s,
      %(three_pointers_attempted)s,
      %(three_point_pct)s,
      %(free_throws_made)s,
      %(free_throws_attempted)s,
      %(free_throw_pct)s,
      %(source_endpoint)s,
      %(raw)s::jsonb,
      %(fetched_at)s
    )
    on conflict (game_id, player_id, team_id)
    do update set
      opponent_team_id = excluded.opponent_team_id,
      season_id = excluded.season_id,
      season_type = excluded.season_type,
      game_date = excluded.game_date,
      team_abbreviation = excluded.team_abbreviation,
      opponent_abbreviation = excluded.opponent_abbreviation,
      is_home = excluded.is_home,
      started = excluded.started,
      position = excluded.position,
      minutes = excluded.minutes,
      points = excluded.points,
      rebounds = excluded.rebounds,
      offensive_rebounds = excluded.offensive_rebounds,
      defensive_rebounds = excluded.defensive_rebounds,
      assists = excluded.assists,
      steals = excluded.steals,
      blocks = excluded.blocks,
      turnovers = excluded.turnovers,
      personal_fouls = excluded.personal_fouls,
      plus_minus = excluded.plus_minus,
      field_goals_made = excluded.field_goals_made,
      field_goals_attempted = excluded.field_goals_attempted,
      field_goal_pct = excluded.field_goal_pct,
      three_pointers_made = excluded.three_pointers_made,
      three_pointers_attempted = excluded.three_pointers_attempted,
      three_point_pct = excluded.three_point_pct,
      free_throws_made = excluded.free_throws_made,
      free_throws_attempted = excluded.free_throws_attempted,
      free_throw_pct = excluded.free_throw_pct,
      source_endpoint = excluded.source_endpoint,
      raw = excluded.raw,
      fetched_at = excluded.fetched_at,
      updated_at = now();
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select team_id, abbreviation from public.teams where abbreviation is not null")
            team_rows = cur.fetchall()
        team_id_by_abbr = {abbr: team_id for team_id, abbr in team_rows}

    total_rows = 0
    processed_rows = 0
    duplicate_rows_skipped = 0
    existing_rows_skipped = 0
    last_commit_at = time.monotonic()
    seen_keys: set[tuple[str, int, int]] = set()
    existing_keys = _existing_player_stat_keys(season, season_type) if only_missing else set()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in rows:
                processed_rows += 1
                game_id = str(row.get("GAME_ID") or "").strip()
                player_id = _to_int(row.get("PLAYER_ID"))
                team_id = _to_int(row.get("TEAM_ID"))
                if not game_id or player_id is None or team_id is None:
                    continue

                unique_key = (game_id, player_id, team_id)
                if unique_key in seen_keys:
                    duplicate_rows_skipped += 1
                    continue
                seen_keys.add(unique_key)
                if unique_key in existing_keys:
                    existing_rows_skipped += 1
                    continue

                is_home, opponent_abbreviation = _parse_matchup(row.get("MATCHUP"))
                opponent_team_id = team_id_by_abbr.get(opponent_abbreviation) if opponent_abbreviation else None
                now_utc = datetime.utcnow()

                cur.execute(
                    upsert_sql,
                    {
                        "game_id": game_id,
                        "player_id": player_id,
                        "team_id": team_id,
                        "opponent_team_id": opponent_team_id,
                        "season_id": season,
                        "season_type": season_type,
                        "game_date": row.get("GAME_DATE"),
                        "team_abbreviation": row.get("TEAM_ABBREVIATION"),
                        "opponent_abbreviation": opponent_abbreviation,
                        "is_home": is_home,
                        "started": None,
                        "position": None,
                        "minutes": _parse_minutes(row.get("MIN")),
                        "points": _to_int(row.get("PTS")),
                        "rebounds": _to_int(row.get("REB")),
                        "offensive_rebounds": _to_int(row.get("OREB")),
                        "defensive_rebounds": _to_int(row.get("DREB")),
                        "assists": _to_int(row.get("AST")),
                        "steals": _to_int(row.get("STL")),
                        "blocks": _to_int(row.get("BLK")),
                        "turnovers": _to_int(row.get("TOV")),
                        "personal_fouls": _to_int(row.get("PF")),
                        "plus_minus": _to_float(row.get("PLUS_MINUS")),
                        "field_goals_made": _to_int(row.get("FGM")),
                        "field_goals_attempted": _to_int(row.get("FGA")),
                        "field_goal_pct": _to_float(row.get("FG_PCT")),
                        "three_pointers_made": _to_int(row.get("FG3M")),
                        "three_pointers_attempted": _to_int(row.get("FG3A")),
                        "three_point_pct": _to_float(row.get("FG3_PCT")),
                        "free_throws_made": _to_int(row.get("FTM")),
                        "free_throws_attempted": _to_int(row.get("FTA")),
                        "free_throw_pct": _to_float(row.get("FT_PCT")),
                        "source_endpoint": "leaguegamelog",
                        "raw": jsonb_dumps(row),
                        "fetched_at": now_utc,
                    },
                )
                total_rows += 1

                now_tick = time.monotonic()
                if (processed_rows % commit_batch_games == 0) or ((now_tick - last_commit_at) >= commit_interval_seconds):
                    conn.commit()
                    last_commit_at = now_tick
                    logger.info(
                        "Checkpoint commit baseline player stats: processed_rows=%s total_rows=%s",
                        processed_rows,
                        total_rows,
                    )

        conn.commit()

    logger.info(
        "Completed baseline sync_player_game_stats season=%s processed_rows=%s upserted_rows=%s duplicate_rows_skipped=%s existing_rows_skipped=%s",
        season,
        processed_rows,
        total_rows,
        duplicate_rows_skipped,
        existing_rows_skipped,
    )
