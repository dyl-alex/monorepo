from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder


def get_static_teams() -> list[dict]:
    return teams.get_teams()


def get_static_players() -> list[dict]:
    return players.get_players()


def get_league_games(season: str, season_type: str) -> list[dict]:
    finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        season_type_nullable=season_type,
    )
    frames = finder.get_data_frames()
    if not frames:
        return []
    return frames[0].to_dict("records")
