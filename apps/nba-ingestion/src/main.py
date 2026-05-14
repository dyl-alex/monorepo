import argparse
import logging

from config import get_settings
from logger import configure_logging

from jobs.sync_teams import sync_teams
from jobs.sync_players import sync_players
from jobs.sync_games import sync_games
from jobs.sync_player_game_stats import sync_player_game_stats
from jobs.sync_team_game_stats import sync_team_game_stats
from jobs.enrich_team_game_advanced import enrich_team_game_advanced

logger = logging.getLogger(__name__)


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

    if args.command == "sync-teams":
        sync_teams()

    elif args.command == "sync-players":
        sync_players()

    elif args.command == "sync-games":
        sync_games(args.season)

    elif args.command == "sync-player-game-stats":
        sync_player_game_stats(args.season)

    elif args.command == "sync-team-game-stats":
        sync_team_game_stats(args.season)

    elif args.command == "enrich-team-game-advanced":
        enrich_team_game_advanced(args.season, args.limit)

    elif args.command == "sync-daily":
        sync_teams()
        sync_players()
        sync_games(args.season)

    elif args.command == "backfill":
        sync_teams()
        sync_players()
        sync_games(args.season)
        sync_team_game_stats(args.season)
        sync_player_game_stats(args.season)

    logger.info("Completed command: %s", args.command)


if __name__ == "__main__":
    main()
