from nba_api.stats.static import teams, players


def get_static_teams() -> list[dict]:
    return teams.get_teams()


def get_static_players() -> list[dict]:
    return players.get_players()