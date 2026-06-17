# NBA Ingestion Deployment Commands

Run these commands from `apps/nba-ingestion` on the home server.

Set these environment variables in the server shell or script before parsing commands:

```bash
NBA_BACKFILL_FROM_SEASON=1979-80
NBA_BACKFILL_TO_SEASON=2024-25
NBA_SEASON_STATS_FROM_SEASON=1995-96
NBA_CURRENT_SEASON=2024-25
```

## On Load

Use this block once for a fresh database. It loads static data, player profiles, regular season game-level data, playoff game-level data, and endpoint-backed season summaries where the NBA endpoint provides them.

<!-- ON_LOAD_COMMANDS_START -->
```bash
docker compose run --rm nba-ingestion sync-teams
docker compose run --rm nba-ingestion sync-players
docker compose run --rm nba-ingestion sync-player-profiles --only-missing

docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Regular Season" --include games --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Playoffs" --include games --skip-static --only-missing

docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Regular Season" --include team-game-stats --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Playoffs" --include team-game-stats --skip-static --only-missing

docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Regular Season" --include player-game-stats --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_BACKFILL_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Playoffs" --include player-game-stats --skip-static --only-missing

docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_SEASON_STATS_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Regular Season" --include team-season-stats --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_SEASON_STATS_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Playoffs" --include team-season-stats --skip-static --only-missing

docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_SEASON_STATS_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Regular Season" --include player-season-stats --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_SEASON_STATS_FROM_SEASON} --to-season ${NBA_BACKFILL_TO_SEASON} --season-type "Playoffs" --include player-season-stats --skip-static --only-missing
```
<!-- ON_LOAD_COMMANDS_END -->

## Upkeep

Daily commands keep the current regular season and playoff tables moving. Playoff commands are safe before playoffs exist because they are idempotent.

<!-- DAILY_COMMANDS_START -->
```bash
docker compose run --rm nba-ingestion sync-daily --season ${NBA_CURRENT_SEASON} --season-type "Regular Season" --only-missing
docker compose run --rm nba-ingestion sync-daily --season ${NBA_CURRENT_SEASON} --season-type "Playoffs" --only-missing
```
<!-- DAILY_COMMANDS_END -->

Weekly commands repair slow/flaky endpoints and refresh season summary tables.

<!-- WEEKLY_COMMANDS_START -->
```bash
docker compose run --rm nba-ingestion sync-player-profiles --only-missing
docker compose run --rm nba-ingestion sync-team-season-stats --season ${NBA_CURRENT_SEASON} --season-type "Regular Season" --only-missing
docker compose run --rm nba-ingestion sync-team-season-stats --season ${NBA_CURRENT_SEASON} --season-type "Playoffs" --only-missing
docker compose run --rm nba-ingestion sync-player-season-stats --season ${NBA_CURRENT_SEASON} --season-type "Regular Season" --only-missing
docker compose run --rm nba-ingestion sync-player-season-stats --season ${NBA_CURRENT_SEASON} --season-type "Playoffs" --only-missing
```
<!-- WEEKLY_COMMANDS_END -->

Yearly commands finalize a completed season. Set `NBA_FINAL_SEASON` to the season that just ended before running.

<!-- YEARLY_COMMANDS_START -->
```bash
docker compose run --rm nba-ingestion sync-teams
docker compose run --rm nba-ingestion sync-players
docker compose run --rm nba-ingestion sync-player-profiles --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_FINAL_SEASON} --to-season ${NBA_FINAL_SEASON} --season-type "Regular Season" --include all --skip-static --only-missing
docker compose run --rm nba-ingestion backfill-range --from-season ${NBA_FINAL_SEASON} --to-season ${NBA_FINAL_SEASON} --season-type "Playoffs" --include all --skip-static --only-missing
```
<!-- YEARLY_COMMANDS_END -->
