import logging
import math
from datetime import datetime

from db import get_connection
from jobs.sync_games import _upsert_season
from nba.client import get_league_dash_team_stats
from raw_store import jsonb_dumps, store_raw_api_response

logger = logging.getLogger(__name__)

STAT_MODE = "PerGame"


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


def _rank_json(row: dict) -> str:
    return jsonb_dumps({key: value for key, value in row.items() if str(key).endswith("_RANK")})


def _existing_keys(season: str, season_type: str, stat_mode: str) -> set[tuple[int, str, str, str]]:
    sql = """
    select team_id, season_id, season_type, stat_mode
    from public.team_season_stats
    where season_id = %(season_id)s
      and season_type = %(season_type)s
      and stat_mode = %(stat_mode)s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"season_id": season, "season_type": season_type, "stat_mode": stat_mode})
            return {(row[0], row[1], row[2], row[3]) for row in cur.fetchall()}


def _team_abbreviations() -> dict[int, str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select team_id, abbreviation from public.teams where abbreviation is not null")
            return {row[0]: row[1] for row in cur.fetchall()}


def sync_team_season_stats(season: str, season_type: str, only_missing: bool = False) -> None:
    _upsert_season(season)
    rows = get_league_dash_team_stats(season=season, season_type=season_type, stat_mode=STAT_MODE)
    store_raw_api_response(
        endpoint_name="leaguedashteamstats",
        endpoint_params={"season": season, "season_type": season_type, "stat_mode": STAT_MODE},
        response_json=rows,
        season_id=season,
    )

    existing_keys = _existing_keys(season, season_type, STAT_MODE) if only_missing else set()
    team_abbreviation_by_id = _team_abbreviations()
    logger.info(
        "Starting sync_team_season_stats season=%s season_type=%s rows=%s only_missing=%s",
        season,
        season_type,
        len(rows),
        only_missing,
    )

    upsert_sql = """
    insert into public.team_season_stats (
      team_id,
      season_id,
      season_type,
      stat_mode,
      team_abbreviation,
      games_played,
      wins,
      losses,
      win_pct,
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
      field_goals_made,
      field_goals_attempted,
      field_goal_pct,
      three_pointers_made,
      three_pointers_attempted,
      three_point_pct,
      free_throws_made,
      free_throws_attempted,
      free_throw_pct,
      plus_minus,
      nba_rank,
      source_endpoint,
      raw,
      fetched_at
    )
    values (
      %(team_id)s,
      %(season_id)s,
      %(season_type)s,
      %(stat_mode)s,
      %(team_abbreviation)s,
      %(games_played)s,
      %(wins)s,
      %(losses)s,
      %(win_pct)s,
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
      %(field_goals_made)s,
      %(field_goals_attempted)s,
      %(field_goal_pct)s,
      %(three_pointers_made)s,
      %(three_pointers_attempted)s,
      %(three_point_pct)s,
      %(free_throws_made)s,
      %(free_throws_attempted)s,
      %(free_throw_pct)s,
      %(plus_minus)s,
      %(nba_rank)s::jsonb,
      %(source_endpoint)s,
      %(raw)s::jsonb,
      %(fetched_at)s
    )
    on conflict (team_id, season_id, season_type, stat_mode)
    do update set
      team_abbreviation = excluded.team_abbreviation,
      games_played = excluded.games_played,
      wins = excluded.wins,
      losses = excluded.losses,
      win_pct = excluded.win_pct,
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
      field_goals_made = excluded.field_goals_made,
      field_goals_attempted = excluded.field_goals_attempted,
      field_goal_pct = excluded.field_goal_pct,
      three_pointers_made = excluded.three_pointers_made,
      three_pointers_attempted = excluded.three_pointers_attempted,
      three_point_pct = excluded.three_point_pct,
      free_throws_made = excluded.free_throws_made,
      free_throws_attempted = excluded.free_throws_attempted,
      free_throw_pct = excluded.free_throw_pct,
      plus_minus = excluded.plus_minus,
      nba_rank = excluded.nba_rank,
      source_endpoint = excluded.source_endpoint,
      raw = excluded.raw,
      fetched_at = excluded.fetched_at,
      updated_at = now();
    """

    synced_rows = 0
    existing_rows_skipped = 0
    invalid_rows_skipped = 0
    missing_fk_rows_skipped = 0
    now_utc = datetime.utcnow()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in rows:
                team_id = _to_int(row.get("TEAM_ID"))
                if team_id is None:
                    invalid_rows_skipped += 1
                    continue
                if team_id not in team_abbreviation_by_id:
                    missing_fk_rows_skipped += 1
                    continue

                key = (team_id, season, season_type, STAT_MODE)
                if key in existing_keys:
                    existing_rows_skipped += 1
                    continue

                cur.execute(
                    upsert_sql,
                    {
                        "team_id": team_id,
                        "season_id": season,
                        "season_type": season_type,
                        "stat_mode": STAT_MODE,
                        "team_abbreviation": team_abbreviation_by_id.get(team_id),
                        "games_played": _to_int(row.get("GP")),
                        "wins": _to_int(row.get("W")),
                        "losses": _to_int(row.get("L")),
                        "win_pct": _to_float(row.get("W_PCT")),
                        "minutes": _to_float(row.get("MIN")),
                        "points": _to_float(row.get("PTS")),
                        "rebounds": _to_float(row.get("REB")),
                        "offensive_rebounds": _to_float(row.get("OREB")),
                        "defensive_rebounds": _to_float(row.get("DREB")),
                        "assists": _to_float(row.get("AST")),
                        "steals": _to_float(row.get("STL")),
                        "blocks": _to_float(row.get("BLK")),
                        "turnovers": _to_float(row.get("TOV")),
                        "personal_fouls": _to_float(row.get("PF")),
                        "field_goals_made": _to_float(row.get("FGM")),
                        "field_goals_attempted": _to_float(row.get("FGA")),
                        "field_goal_pct": _to_float(row.get("FG_PCT")),
                        "three_pointers_made": _to_float(row.get("FG3M")),
                        "three_pointers_attempted": _to_float(row.get("FG3A")),
                        "three_point_pct": _to_float(row.get("FG3_PCT")),
                        "free_throws_made": _to_float(row.get("FTM")),
                        "free_throws_attempted": _to_float(row.get("FTA")),
                        "free_throw_pct": _to_float(row.get("FT_PCT")),
                        "plus_minus": _to_float(row.get("PLUS_MINUS")),
                        "nba_rank": _rank_json(row),
                        "source_endpoint": "leaguedashteamstats",
                        "raw": jsonb_dumps(row),
                        "fetched_at": now_utc,
                    },
                )
                synced_rows += 1

        conn.commit()

    logger.info(
        "Completed sync_team_season_stats season=%s synced_rows=%s existing_rows_skipped=%s invalid_rows_skipped=%s missing_fk_rows_skipped=%s",
        season,
        synced_rows,
        existing_rows_skipped,
        invalid_rows_skipped,
        missing_fk_rows_skipped,
    )
