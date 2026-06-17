# NBA Ingestion Next Gameplan

Assumption: validation SQL and idempotency checks in `SYNC_DATABASE_GUIDE.md` sections 5 and 6 are passing.

## 1. Stabilize Home Server Database

- Deploy Supabase/Postgres on the home server with persistent storage.
- Apply all migrations and confirm generated DB types still match the live schema.
- Point `apps/nba-ingestion/.env` at the home server database.
- Run the `DEPLOYMENT_COMMANDS.md` on-load block.

## 2. Operationalize Ingestion

- Build and run ingestion through Docker Compose.
- Create home server scripts that parse `DEPLOYMENT_COMMANDS.md` markers:
  - `DAILY_COMMANDS_START` / `DAILY_COMMANDS_END`
  - `WEEKLY_COMMANDS_START` / `WEEKLY_COMMANDS_END`
  - `YEARLY_COMMANDS_START` / `YEARLY_COMMANDS_END`
- Schedule those scripts with cron/systemd timers.
- Log command output to timestamped files for later troubleshooting.

## 3. Fill Derived Season Gaps

- Current endpoint-backed `player_season_stats` can return zero rows for older seasons.
- Add derived aggregate jobs later if we want season summaries before endpoint coverage:
  - `player_game_stats` → `player_season_stats`
  - `team_game_stats` → `team_season_stats`
- Keep game-level regular season and playoff stats as the source of truth.

## 4. Start Backend/API Work

- Add tRPC routes in `nba-compare-v2` after the home server DB is stable.
- First read APIs:
  - teams and players
  - player profiles
  - games by season and season type
  - player/team game stats
  - player/team season stats
- Keep `season_type` as the backend delimiter for regular season vs playoffs.

## 5. Build Dashboard Views

- Start with season-level comparison charts.
- Add player profile pages next.
- Add game-level drilldowns after the core charts are stable.
