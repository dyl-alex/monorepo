alter table public.team_game_stats
  add column if not exists base_synced_at timestamptz,
  add column if not exists advanced_synced_at timestamptz,
  add column if not exists advanced_sync_status text,
  add column if not exists advanced_sync_error text;

create index if not exists idx_team_game_stats_advanced_sync_status
  on public.team_game_stats(advanced_sync_status);

create index if not exists idx_team_game_stats_advanced_synced_at
  on public.team_game_stats(advanced_synced_at);
