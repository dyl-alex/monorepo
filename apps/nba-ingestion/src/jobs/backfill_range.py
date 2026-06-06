import logging

from jobs.sync_games import sync_games
from jobs.sync_players import sync_players
from jobs.sync_player_game_stats import sync_player_game_stats
from jobs.sync_teams import sync_teams
from jobs.sync_team_game_stats import sync_team_game_stats

logger = logging.getLogger(__name__)

BACKFILL_STEPS = ("games", "team-game-stats", "player-game-stats")


def _season_start_year(season: str) -> int:
    return int(season.split("-", 1)[0])


def _format_season(start_year: int) -> str:
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def build_season_range(from_season: str, to_season: str, oldest_first: bool = False) -> list[str]:
    from_year = _season_start_year(from_season)
    to_year = _season_start_year(to_season)
    low_year = min(from_year, to_year)
    high_year = max(from_year, to_year)

    years = range(low_year, high_year + 1)
    seasons = [_format_season(year) for year in years]
    if oldest_first:
        return seasons
    return list(reversed(seasons))


def _normalize_steps(include_steps: list[str]) -> list[str]:
    if "all" in include_steps:
        return list(BACKFILL_STEPS)

    normalized_steps = []
    for step in BACKFILL_STEPS:
        if step in include_steps:
            normalized_steps.append(step)
    return normalized_steps


def backfill_range(
    from_season: str,
    to_season: str,
    season_type: str,
    include_steps: list[str],
    oldest_first: bool = False,
    skip_static: bool = False,
    stop_on_error: bool = False,
) -> None:
    seasons = build_season_range(
        from_season=from_season,
        to_season=to_season,
        oldest_first=oldest_first,
    )
    steps = _normalize_steps(include_steps)
    failures: list[tuple[str, str, str]] = []

    logger.info(
        "Starting backfill_range from_season=%s to_season=%s season_type=%s seasons=%s steps=%s oldest_first=%s",
        from_season,
        to_season,
        season_type,
        len(seasons),
        steps,
        oldest_first,
    )

    if not skip_static:
        logger.info("Syncing static teams and players before range backfill")
        sync_teams()
        sync_players()

    for season in seasons:
        logger.info("Starting backfill season=%s season_type=%s", season, season_type)

        for step in steps:
            try:
                if step == "games":
                    sync_games(season=season, season_type=season_type)
                elif step == "team-game-stats":
                    sync_team_game_stats(season=season, season_type=season_type)
                elif step == "player-game-stats":
                    sync_player_game_stats(season=season, season_type=season_type)
                else:
                    raise ValueError(f"Unsupported backfill step: {step}")
            except Exception as exc:
                failures.append((season, step, f"{type(exc).__name__}: {exc}"))
                logger.exception("Backfill step failed season=%s step=%s", season, step)
                if stop_on_error:
                    raise

        logger.info("Completed backfill season=%s season_type=%s", season, season_type)

    if failures:
        logger.warning("Completed backfill_range with %s failed steps", len(failures))
        for season, step, error in failures:
            logger.warning("Failed backfill step season=%s step=%s error=%s", season, step, error)
        raise RuntimeError(f"Backfill range completed with {len(failures)} failed steps")

    logger.info("Completed backfill_range successfully seasons=%s steps=%s", len(seasons), steps)
