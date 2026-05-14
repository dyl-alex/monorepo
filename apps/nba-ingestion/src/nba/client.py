import logging

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import get_settings
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder, leaguegamelog, boxscoretraditionalv2, boxscoreadvancedv2

logger = logging.getLogger(__name__)


def get_static_teams() -> list[dict]:
    return teams.get_teams()


def get_static_players() -> list[dict]:
    return players.get_players()


def _timeout() -> int:
    return get_settings().nba_api_timeout_seconds


def _retry_attempts() -> int:
    return get_settings().nba_api_max_retries


def _response_preview(endpoint) -> str | None:
    nba_response = getattr(endpoint, "nba_response", None)
    if nba_response is None:
        return None

    response = getattr(nba_response, "response", None)
    if response is None:
        return None

    # requests.Response.text
    text = getattr(response, "text", None)
    if text:
        return str(text)[:500]

    # Fallback for unexpected response types.
    return str(response)[:500]


def _log_endpoint_failure(endpoint_name: str, endpoint, game_id: str | None = None) -> None:
    preview = _response_preview(endpoint)
    if game_id:
        logger.warning(
            "nba_api endpoint failure endpoint=%s game_id=%s response_preview=%s",
            endpoint_name,
            game_id,
            preview if preview is not None else "<none>",
        )
        return

    logger.warning(
        "nba_api endpoint failure endpoint=%s response_preview=%s",
        endpoint_name,
        preview if preview is not None else "<none>",
    )


@retry(
    reraise=True,
    stop=lambda retry_state: stop_after_attempt(_retry_attempts())(retry_state),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(Exception),
)
def get_league_games(season: str, season_type: str) -> list[dict]:
    finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        season_type_nullable=season_type,
        timeout=_timeout(),
        get_request=False,
    )
    try:
        finder.get_request()
    except Exception:
        _log_endpoint_failure("LeagueGameFinder", finder)
        raise
    frames = finder.get_data_frames()
    if not frames:
        return []
    return frames[0].to_dict("records")


@retry(
    reraise=True,
    stop=lambda retry_state: stop_after_attempt(_retry_attempts())(retry_state),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(Exception),
)
def get_league_game_log(season: str, season_type: str, player_or_team_abbreviation: str = "T") -> list[dict]:
    endpoint = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star=season_type,
        player_or_team_abbreviation=player_or_team_abbreviation,
        timeout=_timeout(),
        get_request=False,
    )
    try:
        endpoint.get_request()
    except Exception:
        _log_endpoint_failure("LeagueGameLog", endpoint)
        raise
    frames = endpoint.get_data_frames()
    if not frames:
        return []
    return frames[0].to_dict("records")


def _records_from_frame_list(frames: list, index: int) -> list[dict]:
    if len(frames) <= index:
        return []
    return frames[index].to_dict("records")


@retry(
    reraise=True,
    stop=lambda retry_state: stop_after_attempt(_retry_attempts())(retry_state),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(Exception),
)
def get_boxscore_traditional(game_id: str) -> dict[str, list[dict]]:
    endpoint = boxscoretraditionalv2.BoxScoreTraditionalV2(
        game_id=game_id,
        timeout=_timeout(),
        get_request=False,
    )
    try:
        endpoint.get_request()
    except Exception:
        _log_endpoint_failure("BoxScoreTraditionalV2", endpoint, game_id=game_id)
        raise
    frames = endpoint.get_data_frames()
    return {
        "player_stats": _records_from_frame_list(frames, 0),
        "team_stats": _records_from_frame_list(frames, 1),
    }


@retry(
    reraise=True,
    stop=lambda retry_state: stop_after_attempt(_retry_attempts())(retry_state),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(Exception),
)
def get_boxscore_advanced(game_id: str) -> dict[str, list[dict]]:
    endpoint = boxscoreadvancedv2.BoxScoreAdvancedV2(
        game_id=game_id,
        timeout=_timeout(),
        get_request=False,
    )
    try:
        endpoint.get_request()
    except Exception:
        _log_endpoint_failure("BoxScoreAdvancedV2", endpoint, game_id=game_id)
        raise
    frames = endpoint.get_data_frames()
    return {
        "player_stats": _records_from_frame_list(frames, 0),
        "team_stats": _records_from_frame_list(frames, 1),
    }
