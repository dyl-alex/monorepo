import argparse
import logging

from config import get_settings
from ingestion_runs import finish_ingestion_run, start_ingestion_run
from logger import configure_logging

from jobs.sync_teams import sync_teams
from jobs.sync_players import sync_players
from jobs.sync_games import sync_games
from jobs.sync_player_game_stats import sync_player_game_stats
from jobs.sync_team_game_stats import sync_team_game_stats
from jobs.enrich_team_game_advanced import enrich_team_game_advanced

logger = logging.getLogger(__name__)


def _execute_command(command: str, season: str, limit: int | None) -> None:
    if command == "sync-teams":
        sync_teams()
        return

    if command == "sync-players":
        sync_players()
        return

    if command == "sync-games":
        sync_games(season)
        return

    if command == "sync-player-game-stats":
        sync_player_game_stats(season)
        return

    if command == "sync-team-game-stats":
        sync_team_game_stats(season)
        return

    if command == "enrich-team-game-advanced":
        enrich_team_game_advanced(season, limit)
        return

    if command == "sync-daily":
        sync_teams()
        sync_players()
        sync_games(season)
        return

    if command == "backfill":
        sync_teams()
        sync_players()
        sync_games(season)
        sync_team_game_stats(season)
        sync_player_game_stats(season)
        return

    raise ValueError(f"Unsupported command: {command}")


def main() -> None:
    configure_logging()
    settings = get_settings()

    parser = argparse.ArgumentParser(description="NBA ingestion worker")
    parser.add_argument(
        "command",
        choices=[
            "sync-teams",
            "sync-players",
            "sync-games",
            "sync-player-game-stats",
            "sync-team-game-stats",
            "enrich-team-game-advanced",
            "sync-daily",
            "backfill",
        ],
    )
    parser.add_argument("--season", default=settings.default_season)
    parser.add_argument("--limit", type=int, default=None)

    args = parser.parse_args()
    run_id = start_ingestion_run(
        job_name=args.command,
        season_id=args.season,
        season_type=settings.default_season_type,
        metadata={
            "command": args.command,
            "season": args.season,
            "limit": args.limit,
        },
    )

    try:
        _execute_command(args.command, args.season, args.limit)
        finish_ingestion_run(run_id=run_id, status="success")
        logger.info("Completed command: %s run_id=%s", args.command, run_id)
    except Exception as exc:
        finish_ingestion_run(
            run_id=run_id,
            status="failed",
            rows_failed=1,
            error_message=f"{type(exc).__name__}: {exc}"[:2000],
        )
        logger.exception("Command failed: %s run_id=%s", args.command, run_id)
        raise


if __name__ == "__main__":
    main()
