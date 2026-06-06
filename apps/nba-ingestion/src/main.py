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
from jobs.backfill_range import backfill_range

logger = logging.getLogger(__name__)


def _execute_command(args: argparse.Namespace) -> None:
    command = args.command
    season = args.season
    season_type = args.season_type

    if command == "sync-teams":
        sync_teams()
        return

    if command == "sync-players":
        sync_players()
        return

    if command == "sync-games":
        sync_games(season, season_type=season_type)
        return

    if command == "sync-player-game-stats":
        sync_player_game_stats(season, season_type=season_type)
        return

    if command == "sync-team-game-stats":
        sync_team_game_stats(season, season_type=season_type)
        return

    if command == "enrich-team-game-advanced":
        enrich_team_game_advanced(season, args.limit)
        return

    if command == "sync-daily":
        sync_teams()
        sync_players()
        sync_games(season, season_type=season_type)
        return

    if command == "backfill":
        sync_teams()
        sync_players()
        sync_games(season, season_type=season_type)
        sync_team_game_stats(season, season_type=season_type)
        sync_player_game_stats(season, season_type=season_type)
        return

    if command == "backfill-range":
        backfill_range(
            from_season=args.from_season,
            to_season=args.to_season,
            season_type=season_type,
            include_steps=args.include,
            oldest_first=args.oldest_first,
            skip_static=args.skip_static,
            stop_on_error=args.stop_on_error,
        )
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
            "backfill-range",
        ],
    )
    parser.add_argument("--season", default=settings.default_season)
    parser.add_argument("--season-type", default=settings.default_season_type)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--from-season", default="1979-80")
    parser.add_argument("--to-season", default=settings.default_season)
    parser.add_argument(
        "--include",
        nargs="+",
        choices=["all", "games", "team-game-stats", "player-game-stats"],
        default=["all"],
    )
    parser.add_argument("--oldest-first", action="store_true")
    parser.add_argument("--skip-static", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")

    args = parser.parse_args()
    run_id = start_ingestion_run(
        job_name=args.command,
        season_id=args.season,
        season_type=args.season_type,
        metadata={
            "command": args.command,
            "season": args.season,
            "season_type": args.season_type,
            "limit": args.limit,
            "from_season": args.from_season,
            "to_season": args.to_season,
            "include": args.include,
            "oldest_first": args.oldest_first,
            "skip_static": args.skip_static,
            "stop_on_error": args.stop_on_error,
        },
    )

    try:
        _execute_command(args)
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
