# NBA Ingestion App

Python ingestion worker for syncing NBA data from `nba_api` into the local Supabase/Postgres database.

This app is responsible for:

- syncing NBA teams
- syncing NBA players
- syncing games
- syncing player game stats
- syncing team game stats
- eventually syncing advanced stats, season stats, shot charts, and play-by-play data

The Next.js app should read from the database through tRPC. It should not call `nba_api` directly.

---

## Folder Structure

```txt
apps/nba-ingestion/
  requirements.txt
  .env.example
  .gitignore
  README.md
  src/
    main.py
    config.py
    db.py
    logger.py
    jobs/
      __init__.py
      sync_teams.py
      sync_players.py
      sync_games.py
      sync_player_game_stats.py
      sync_team_game_stats.py
    nba/
      __init__.py
      client.py
      transforms.py