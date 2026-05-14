# NBA Ingestion Database Sync Guide

This guide documents how to run and validate all ingestion sync commands against the local Supabase/Postgres database.

## 1) Prerequisites

From the monorepo root:

1. Local Supabase database is running.
2. Python virtual environment exists in `apps/nba-ingestion/.venv`.
3. Dependencies are installed from `requirements.txt`.
4. `apps/nba-ingestion/.env` exists and has a valid `DATABASE_URL`.

Required `.env` values:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
LOG_LEVEL=INFO
NBA_SEASON=2024-25
NBA_SEASON_TYPE=Regular Season
SYNC_COMMIT_BATCH_GAMES=25
```

## 2) Shell Setup

From monorepo root:

```powershell
cd apps/nba-ingestion
.venv\Scripts\Activate.ps1
cd src
```

All commands below assume you are in `apps/nba-ingestion/src`.

## 3) Core Sync Commands

### Teams

```powershell
python -m main sync-teams
```

### Players

```powershell
python -m main sync-players
```

### Games

```powershell
python -m main sync-games --season 2024-25
```

### Team Game Stats

```powershell
python -m main sync-team-game-stats --season 2024-25
```

### Enrich Team Game Advanced

```powershell
python -m main enrich-team-game-advanced --season 2024-25 --limit 50
```

### Player Game Stats

```powershell
python -m main sync-player-game-stats --season 2024-25
```

### Daily bundle

```powershell
python -m main sync-daily
```

### Backfill bundle

```powershell
python -m main backfill --season 2024-25
```

## 4) Suggested Execution Order

Run in this order to satisfy foreign keys and data dependencies:

1. `sync-teams`
2. `sync-players`
3. `sync-games --season <season>`
4. `sync-team-game-stats --season <season>` (fast baseline)
5. `enrich-team-game-advanced --season <season> --limit <n>` (optional slow enrichment)
6. `sync-player-game-stats --season <season>`

## 5) Validation SQL

Run in Supabase Studio SQL editor or any Postgres client:

```sql
select count(*) as teams_count from public.teams;
select count(*) as players_count from public.players;
select count(*) as games_count from public.games where season_id = '2024-25';
select count(distinct game_id) as distinct_games_count from public.games where season_id = '2024-25';

select count(*) as team_game_stats_count
from public.team_game_stats
where season_id = '2024-25';

select count(*) as player_game_stats_count
from public.player_game_stats
where season_id = '2024-25';
```

Foreign-key sanity checks:

```sql
select count(*) as games_missing_team_fk
from public.games g
left join public.teams ht on ht.team_id = g.home_team_id
left join public.teams at on at.team_id = g.away_team_id
where g.season_id = '2024-25'
  and (ht.team_id is null or at.team_id is null);

select count(*) as team_stats_missing_game_fk
from public.team_game_stats tgs
left join public.games g on g.game_id = tgs.game_id
where tgs.season_id = '2024-25'
  and g.game_id is null;

select count(*) as player_stats_missing_game_fk
from public.player_game_stats pgs
left join public.games g on g.game_id = pgs.game_id
where pgs.season_id = '2024-25'
  and g.game_id is null;
```

## 6) Idempotency Checks

Run the same command twice, then verify row counts are stable:

```powershell
python -m main sync-games --season 2024-25
python -m main sync-games --season 2024-25
```

```sql
select count(*) from public.games where season_id = '2024-25';
select count(distinct game_id) from public.games where season_id = '2024-25';
```

Repeat similarly for `team_game_stats` and `player_game_stats`.

## 7) Operational Notes for Step 9 (Game Stats Sync)

- `sync-team-game-stats` now uses `LeagueGameLog` only and writes baseline fields quickly.
- `enrich-team-game-advanced` is optional and fills advanced metrics in a second pass.
- `sync-player-game-stats` now uses `LeagueGameLog` with player rows (no per-game boxscore calls).
- `nba_api` endpoint failures/timeouts can still happen and are expected intermittently.
- Full season runs can be long and may require reruns.
- Reruns are safe because upserts use `ON CONFLICT ... DO UPDATE`.
- Checkpoint commits are enabled for stats sync jobs and commit every `SYNC_COMMIT_BATCH_GAMES` processed games.

## 8) Troubleshooting

### `ModuleNotFoundError` (e.g. dotenv)

Use the project venv Python:

```powershell
..\.venv\Scripts\python.exe -m main sync-teams
```

(Or activate venv first and use `python`.)

### Database connection timeout

- Verify Supabase/local Postgres is running.
- Verify `DATABASE_URL` in `.env`.
- Test connection quickly:

```powershell
python -c "import psycopg; psycopg.connect('postgresql://postgres:postgres@127.0.0.1:54322/postgres').close(); print('ok')"
```

### Slow or flaky box score sync

- Re-run the same season command; sync is idempotent.
- Keep `LOG_LEVEL=INFO` (or set to `WARNING`) to reduce log noise.
- If requests are unstable, reduce batch size (for more frequent checkpoint commits), for example:

```env
SYNC_COMMIT_BATCH_GAMES=10
```
