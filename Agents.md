# NBA Analytics App — Agent Context

## Current Project Stage

1. Create repo folder structure (X)
2. Start local Supabase (X)
3. Add migrations for core schema (X)
4. Generate DB types (X)
5. Create Python ingestion app (X)
6. Implement teams sync (X)
7. Implement players sync (X)
8. Implement games sync (X)
9. Add raw response storage — IN PROGRESS
   - Team/player game stat syncs are running
   - `BoxScoreAdvancedV2` has intermittent malformed responses
   - Jobs were hardened to skip/log malformed responses
   - Needs DB verification for normalized rows + raw rows
10. Containerize ingestion app
11. Add local Docker Compose commands
12. Add cron command
13. Add tRPC queries
14. Build graph metadata
15. Build dashboard UI
16. Add advanced endpoints over time

---

# Commands

## Start local Supabase

Run from monorepo root:

```bash
supabase start
```

---

## Generate DB types

Run from monorepo root:

```bash
supabase gen types typescript --local > packages/db-types/src/database.types.ts
```

IMPORTANT:
- Review `packages/db-types/src/database.types.ts`
- This is the source of truth for DB structure/types

---

## Python ingestion setup

Run from:

```txt
apps/nba-ingestion
```

Create venv:

```bash
python -m venv .venv
```

Activate venv:

### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Bash/macOS/Linux

```bash
source .venv/bin/activate
```

Install deps:

```bash
pip install -r requirements.txt
```

Create env file:

### PowerShell

```powershell
Copy-Item .env.example .env
```

### Bash

```bash
cp .env.example .env
```

---

## Run ingestion commands

Run from:

```txt
apps/nba-ingestion/src
```

### Teams

```bash
python -m main sync-teams
```

### Players

```bash
python -m main sync-players
```

### Games

```bash
python -m main sync-games --season 2024-25
```

### Team game stats

```bash
python -m main sync-team-game-stats --season 2024-25
```

### Player game stats

```bash
python -m main sync-player-game-stats --season 2024-25
```

### Daily sync

```bash
python -m main sync-daily
```

### Backfill

```bash
python -m main backfill --season 2024-25
```

---

# Architecture

```txt
nba_api
  ↓
Python ingestion app
  ↓
Supabase/Postgres
  ↓
tRPC
  ↓
Next.js frontend (nba-compare-v2)
  -react query
  -shadcn
  -shadcn charts
```

---

# Tech Stack

## Monorepo

- Turborepo
- pnpm
- Multiple Next.js apps
- `nba-compare-v2` is the NBA frontend

## Database

- Supabase local
- Postgres
- Supabase migrations
- Generated TypeScript DB types

## Ingestion

- Python app: `apps/nba-ingestion`
- `swar/nba_api`
- `psycopg`
- `.env`
- Future: Docker + cron

## Frontend/API

- Next.js
- tRPC
- React Query
- Dynamic graphing/chart UI

---

# Core Tables

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

---

# Rules

- Use NBA IDs as natural keys
- Use idempotent jobs
- Use upserts:
  ```sql
  INSERT ... ON CONFLICT DO UPDATE
  ```
- Store raw endpoint responses
- Do NOT call `nba_api` from frontend
- Python talks directly to Postgres
- Prefer small incremental changes
- Add logging to every ingestion job
- Avoid redesigning architecture unless explicitly asked

---

# Expected Structure

```txt
apps/nba-ingestion/
  requirements.txt
  .env.example
  README.md
  src/
    main.py
    config.py
    db.py
    logger.py
    jobs/
    nba/
```

---

# Near-Term Tasks

- Verify DB types
- Verify `sync_teams`
- Verify `sync_players`
- Add ingestion run logging
- Finish raw response storage helper
- Verify game sync rows
- Verify raw response rows
- Continue hardening malformed response handling

---

# Future Enhancements

- Dockerize ingestion app
- Add Docker Compose ingestion service
- Add cron-based sync
- Add tRPC routes
- Add graph metadata registry
- Add dashboard UI
- Add shot chart support
- Add play-by-play support
- Add lineup/split endpoints