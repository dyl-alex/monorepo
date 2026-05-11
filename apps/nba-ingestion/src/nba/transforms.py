def team_logo_url(team_id: int) -> str:
    return f"https://cdn.nba.com/logos/nba/{team_id}/primary/L/logo.svg"


def player_headshot_url(player_id: int) -> str:
    return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"