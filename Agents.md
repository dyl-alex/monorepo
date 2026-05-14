# NBA Analytics App — Agent Context

## Project Summary

This project is a personal NBA analytics application built inside a Turborepo. The goal is to ingest historical and advanced NBA statistics from `swar/nba_api`, store them in a local Supabase/Postgres database, and expose the data to a Next.js dashboard through a typed tRPC layer.

The app prioritizes free access to deep NBA stats over production-grade API reliability. `nba_api` is unofficial and may have rate limits/timeouts, so ingestion should be resilient, idempotent, and cache/store data locally.

## Current Project Stage

Current progress:

- Repo folder structure exists.
- Local Supabase has been started.
- Core schema migration has been created.
- DB types need to be generated or verified.
- Python ingestion app shell exists.
- Currently implementing `sync_teams`.

Implementation checklist:

1. Create repo folder structure (X)
2. Start local Supabase (X)
3. Add migrations for core schema (X)
4. Generate DB types (X)
5. Create Python ingestion app (X)
6. Implement teams sync
7. Implement players sync
8. Implement games sync
9. Implement player/team game stats sync
10. Add raw response storage
11. Containerize ingestion app
12. Add local Docker Compose commands
13. Add cron command
14. Add tRPC queries
15. Build graph metadata
16. Build dashboard UI
17. Add advanced endpoints over time

## Technology Stack

### Monorepo

- Turborepo
- pnpm
- Multiple Next.js apps
- nba-compare-v2 will be the NBA analytics frontend

### Database

- Supabase local instance
- Postgres
- Supabase migrations
- Generated TypeScript DB types

### Ingestion

- Python app located at `apps/nba-ingestion`
- Uses `swar/nba_api`
- Uses `psycopg` to connect directly to Postgres
- Uses `.env` for database config
- Future plan: run through Docker and cron

### Frontend/API

- Next.js
- tRPC endpoint layer
- React Query/TanStack Query for fetching
- Dynamic charting/graphing UI

## Database Schema Scope

Core tables:

- `teams`
- `players`
- `player_profiles`
- `seasons`
- `games`
- `player_game_stats`
- `team_game_stats`
- `player_season_stats`
- `team_season_stats`
- `raw_api_responses`
- `ingestion_runs`

Important design rules:

- Use NBA IDs as natural keys where possible.
  - `players.player_id` = NBA `PERSON_ID`
  - `teams.team_id` = NBA `TEAM_ID`
  - `games.game_id` = NBA `GAME_ID`
- Keep normalized stat tables for querying/graphing.
- Store raw endpoint responses in `raw_api_responses`.
- All ingestion jobs must be idempotent.
- Use `INSERT ... ON CONFLICT DO UPDATE` for upserts.
- Do not call `nba_api` directly from the frontend.

## Data Mapping Plan
- IMPORTANT - review packages\db-types\src\database.types.ts for database structure, types, ect. 


Implementation Guidelines For Agents: 
- Prefer small, incremental changes.
- Do not redesign the architecture unless explicitly asked.
- Keep Python ingestion isolated from Next.js apps.
- Use direct Postgres access from Python, not Supabase REST.
- Use typed tRPC endpoints for frontend access.
- Keep jobs idempotent.
- Add raw response storage before implementing large historical syncs.
- Add logging to every ingestion job.
- Avoid committing local .env, .venv, logs, or generated cache files.
- When adding new sync jobs, include:
-   source endpoint
-   transform function
-   upsert SQL
-   logging
-   raw response storage if applicable

Near-Term Tasks:
- Verify generated DB types exist.
- Finish sync_teams.
- Run sync_teams locally.
- Verify records in Supabase Studio.
- Implement sync_players.
- Add ingestion run logging.
- Add raw response storage helper.
- Implement games sync.
- Future Enhancements
- Dockerize apps/nba-ingestion.
- Add Docker Compose command for ingestion.
- Add cron-based sync.
- Add tRPC routes for players, teams, games, and chart data.
- Add graph metadata registry.
- Add player dashboard UI.
- Add team dashboard UI.
- Add game detail page.
- Add shot chart support.
- Add play-by-play support.
- Add lineup and advanced split endpoints.