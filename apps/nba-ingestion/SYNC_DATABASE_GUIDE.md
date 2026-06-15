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
NBA_API_TIMEOUT_SECONDS=20
NBA_API_MAX_RETRIES=2
NBA_API_PROFILE_DELAY_SECONDS=1.0
NBA_API_BACKFILL_STEP_DELAY_SECONDS=1.0
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

### Player Profiles

```powershell
python -m main sync-player-profiles --only-missing
```

This endpoint makes one request per player. Failed player profile requests are logged and skipped so the job can continue; rerun the same command to fill missed profiles.

For safer profile backfills, run in chunks:

```powershell
python -m main sync-player-profiles --only-missing --limit 100
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

### Team Season Stats

```powershell
python -m main sync-team-season-stats --season 2024-25 --season-type "Regular Season" --only-missing
```

### Player Season Stats

```powershell
python -m main sync-player-season-stats --season 2024-25 --season-type "Regular Season" --only-missing
```

### Daily bundle

```powershell
python -m main sync-daily
```

### Backfill bundle

```powershell
python -m main backfill --season 2024-25
```

### Range Backfill

Backfills an inclusive season range. The default order is newest-to-oldest.

```powershell
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include games
```

Recommended phases for a full historical database:

```powershell
python -m main sync-player-profiles --only-missing
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include games
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include team-game-stats --skip-static
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include player-game-stats --skip-static
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include team-season-stats --skip-static --only-missing
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include player-season-stats --skip-static --only-missing
```

Options:

- `--include games team-game-stats` runs selected phases.
- `--include season-stats` runs team and player season stats.
- `--include all` runs player profiles once, then all season-ranged phases.
- `--skip-static` skips the initial teams and players sync.
- `--oldest-first` runs from oldest season to newest season.
- `--stop-on-error` fails on the first season/step error instead of logging and continuing.
- `--only-missing` skips normalized rows that already exist in Postgres after checking the source endpoint.

## 3.1) Initial Load vs Ongoing Sync

For a fresh local Supabase instance, run the historical load in phases:

```powershell
python -m main sync-player-profiles --only-missing
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include games
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include team-game-stats --skip-static
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include player-game-stats --skip-static
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include team-season-stats --skip-static --only-missing
python -m main backfill-range --from-season 1979-80 --to-season 2024-25 --season-type "Regular Season" --include player-season-stats --skip-static --only-missing
```

After the historical load, switch to incremental current-season syncs:

```powershell
python -m main sync-daily --season 2024-25 --season-type "Regular Season" --only-missing
```

`sync-daily` refreshes teams and players, then checks current-season games, game stats, and season stats. With `--only-missing`, existing normalized rows are not rewritten.

## 4) Suggested Execution Order

Run in this order to satisfy foreign keys and data dependencies:

1. `sync-teams`
2. `sync-players`
3. `sync-games --season <season>`
4. `sync-team-game-stats --season <season>` (fast baseline)
5. `enrich-team-game-advanced --season <season> --limit <n>` (optional slow enrichment)
6. `sync-player-game-stats --season <season>`
7. `sync-team-season-stats --season <season>`
8. `sync-player-season-stats --season <season>`

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

select count(*) as player_profiles_count from public.player_profiles;

select count(*) as team_season_stats_count
from public.team_season_stats
where season_id = '2024-25';

select count(*) as player_season_stats_count
from public.player_season_stats
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

select count(*) as player_profiles_missing_player_fk
from public.player_profiles pp
left join public.players p on p.player_id = pp.player_id
where p.player_id is null;

select count(*) as team_season_stats_missing_fk
from public.team_season_stats tss
left join public.teams t on t.team_id = tss.team_id
left join public.seasons s on s.season_id = tss.season_id
where tss.season_id = '2024-25'
  and (t.team_id is null or s.season_id is null);

select count(*) as player_season_stats_missing_fk
from public.player_season_stats pss
left join public.players p on p.player_id = pss.player_id
left join public.teams t on t.team_id = pss.team_id
left join public.seasons s on s.season_id = pss.season_id
where pss.season_id = '2024-25'
  and (p.player_id is null or t.team_id is null or s.season_id is null);
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
- Use a larger NBA API timeout for season backfills:

```env
NBA_API_TIMEOUT_SECONDS=20
NBA_API_BACKFILL_STEP_DELAY_SECONDS=1.0
```

- If requests are unstable, reduce batch size (for more frequent checkpoint commits), for example:

```env
SYNC_COMMIT_BATCH_GAMES=10
```

### Flaky player profile sync

`sync-player-profiles` calls `CommonPlayerInfo` once per player, so intermittent NBA API failures are expected on large historical runs.

- Rerun with `--only-missing`; already inserted profiles are skipped.
- Increase timeout and request spacing if failures are frequent:

```env
NBA_API_TIMEOUT_SECONDS=20
NBA_API_PROFILE_DELAY_SECONDS=1.0
```

Then run in chunks:

```powershell
python -m main sync-player-profiles --only-missing --limit 100
```
