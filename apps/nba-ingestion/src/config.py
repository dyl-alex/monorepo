import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    log_level: str = "INFO"
    default_season: str = "2024-25"
    default_season_type: str = "Regular Season"
    sync_commit_batch_games: int = 25
    nba_api_timeout_seconds: int = 8
    nba_api_max_retries: int = 2


def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    return Settings(
        database_url=database_url,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_season=os.getenv("NBA_SEASON", "2024-25"),
        default_season_type=os.getenv("NBA_SEASON_TYPE", "Regular Season"),
        sync_commit_batch_games=max(1, int(os.getenv("SYNC_COMMIT_BATCH_GAMES", "25"))),
        nba_api_timeout_seconds=max(1, int(os.getenv("NBA_API_TIMEOUT_SECONDS", "8"))),
        nba_api_max_retries=max(1, int(os.getenv("NBA_API_MAX_RETRIES", "2"))),
    )
