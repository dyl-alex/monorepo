import logging
from datetime import datetime

from config import get_settings
from db import get_connection
from nba.client import get_league_games
from raw_store import jsonb_dumps, store_raw_api_response

logger = logging.getLogger(__name__)


def _parse_season_bounds(season: str) -> tuple[int, int]:
    start_str, end_suffix = season.split("-", 1)
    start_year = int(start_str)
    end_year = int(f"{start_str[:2]}{end_suffix}")
    return start_year, end_year


def _parse_game_date(value: str | None) -> datetime | None:
    if not value:
        return None

    date_value = value.strip()
    if not date_value:
        return None

    if "T" in date_value:
        return datetime.fromisoformat(date_value.replace("Z", "+00:00"))

    return datetime.strptime(date_value, "%Y-%m-%d")


def _parse_matchup(matchup: str | None) -> tuple[str | None, str | None]:
    if not matchup:
        return None, None

    text = matchup.strip()
    if " @ " in text:
        away_abbr, home_abbr = text.split(" @ ", 1)
        return away_abbr.strip(), home_abbr.strip()

    if " vs. " in text:
        home_abbr, away_abbr = text.split(" vs. ", 1)
        return away_abbr.strip(), home_abbr.strip()

    return None, None


def _upsert_season(season: str) -> None:
    start_year, end_year = _parse_season_bounds(season)

    sql = """
    insert into public.seasons (
        season_id,
        season_start_year,
        season_end_year
    )
    values (
        %(season_id)s,
        %(season_start_year)s,
        %(season_end_year)s
    )
    on conflict (season_id)
    do update set
        season_start_year = excluded.season_start_year,
        season_end_year = excluded.season_end_year;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "season_id": season,
                    "season_start_year": start_year,
                    "season_end_year": end_year,
                },
            )
        conn.commit()


def _game_from_rows(game_id: str, rows: list[dict], season: str, season_type: str) -> dict:
    primary_row = rows[0]
    away_abbr_from_matchup, home_abbr_from_matchup = _parse_matchup(primary_row.get("MATCHUP"))

    by_team_abbr = {
        str(row.get("TEAM_ABBREVIATION") or "").strip(): row
        for row in rows
        if str(row.get("TEAM_ABBREVIATION") or "").strip()
    }

    home_row = by_team_abbr.get(home_abbr_from_matchup or "")
    away_row = by_team_abbr.get(away_abbr_from_matchup or "")

    home_team_id = home_row.get("TEAM_ID") if home_row else None
    away_team_id = away_row.get("TEAM_ID") if away_row else None
    home_team_abbreviation = home_row.get("TEAM_ABBREVIATION") if home_row else home_abbr_from_matchup
    away_team_abbreviation = away_row.get("TEAM_ABBREVIATION") if away_row else away_abbr_from_matchup
    home_points = home_row.get("PTS") if home_row else None
    away_points = away_row.get("PTS") if away_row else None

    winning_team_id = None
    if home_row and str(home_row.get("WL") or "").upper() == "W":
        winning_team_id = home_team_id
    elif away_row and str(away_row.get("WL") or "").upper() == "W":
        winning_team_id = away_team_id

    game_date = _parse_game_date(primary_row.get("GAME_DATE"))

    return {
        "game_id": game_id,
        "season_id": season,
        "season_type": season_type,
        "game_date": game_date.date() if game_date else None,
        "game_datetime": game_date,
        "matchup": primary_row.get("MATCHUP"),
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "home_team_abbreviation": home_team_abbreviation,
        "away_team_abbreviation": away_team_abbreviation,
        "home_points": home_points,
        "away_points": away_points,
        "winning_team_id": winning_team_id,
        "game_status": None,
        "game_status_id": None,
        "period": None,
        "game_clock": None,
        "arena": None,
        "city": None,
        "state": None,
        "raw": jsonb_dumps(rows),
    }


def sync_games(season: str, season_type: str | None = None) -> None:
    settings = get_settings()
    season_type = season_type or settings.default_season_type

    logger.info("Starting sync_games season=%s season_type=%s", season, season_type)

    _upsert_season(season)

    rows = get_league_games(season=season, season_type=season_type)
    store_raw_api_response(
        endpoint_name="leaguegamefinder",
        endpoint_params={
            "season": season,
            "season_type": season_type,
        },
        response_json=rows,
        season_id=season,
    )
    games_by_id: dict[str, list[dict]] = {}
    for row in rows:
        game_id = str(row.get("GAME_ID") or "").strip()
        if not game_id:
            continue
        games_by_id.setdefault(game_id, []).append(row)

    sql = """
    insert into public.games (
        game_id,
        season_id,
        season_type,
        game_date,
        game_datetime,
        matchup,
        home_team_id,
        away_team_id,
        home_team_abbreviation,
        away_team_abbreviation,
        home_points,
        away_points,
        winning_team_id,
        game_status,
        game_status_id,
        period,
        game_clock,
        arena,
        city,
        state,
        raw
    )
    values (
        %(game_id)s,
        %(season_id)s,
        %(season_type)s,
        %(game_date)s,
        %(game_datetime)s,
        %(matchup)s,
        %(home_team_id)s,
        %(away_team_id)s,
        %(home_team_abbreviation)s,
        %(away_team_abbreviation)s,
        %(home_points)s,
        %(away_points)s,
        %(winning_team_id)s,
        %(game_status)s,
        %(game_status_id)s,
        %(period)s,
        %(game_clock)s,
        %(arena)s,
        %(city)s,
        %(state)s,
        %(raw)s::jsonb
    )
    on conflict (game_id)
    do update set
        season_id = excluded.season_id,
        season_type = excluded.season_type,
        game_date = excluded.game_date,
        game_datetime = excluded.game_datetime,
        matchup = excluded.matchup,
        home_team_id = excluded.home_team_id,
        away_team_id = excluded.away_team_id,
        home_team_abbreviation = excluded.home_team_abbreviation,
        away_team_abbreviation = excluded.away_team_abbreviation,
        home_points = excluded.home_points,
        away_points = excluded.away_points,
        winning_team_id = excluded.winning_team_id,
        game_status = excluded.game_status,
        game_status_id = excluded.game_status_id,
        period = excluded.period,
        game_clock = excluded.game_clock,
        arena = excluded.arena,
        city = excluded.city,
        state = excluded.state,
        raw = excluded.raw,
        updated_at = now();
    """

    game_rows = [
        _game_from_rows(game_id=game_id, rows=game_rows, season=season, season_type=season_type)
        for game_id, game_rows in games_by_id.items()
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            for game in game_rows:
                cur.execute(sql, game)
        conn.commit()

    logger.info(
        "Synced %s games from %s source rows for season=%s",
        len(game_rows),
        len(rows),
        season,
    )
