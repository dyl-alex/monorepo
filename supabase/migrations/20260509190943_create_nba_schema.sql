-- NBA analytics schema for Supabase/Postgres
-- Source target: swar/nba_api / stats.nba.com-style IDs and response payloads

create extension if not exists pgcrypto;

-- ------------------------------------------------------------
-- Shared timestamp helper
-- ------------------------------------------------------------

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ------------------------------------------------------------
-- Reference tables
-- ------------------------------------------------------------

create table public.teams (
  team_id integer primary key, -- NBA TEAM_ID, ex: 1610612738
  full_name text not null,
  abbreviation text,
  nickname text,
  city text,
  state text,
  year_founded integer,

  logo_url text,

  raw jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger set_teams_updated_at
before update on public.teams
for each row execute function public.set_updated_at();


create table public.players (
  player_id integer primary key, -- NBA PERSON_ID
  first_name text,
  last_name text,
  full_name text not null,

  player_slug text,
  player_code text,

  is_active boolean,
  roster_status text,

  from_year integer,
  to_year integer,

  current_team_id integer references public.teams(team_id),
  current_team_abbreviation text,
  current_team_city text,
  current_team_name text,

  headshot_url text,

  raw jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_players_full_name on public.players using gin (to_tsvector('english', full_name));
create index idx_players_current_team_id on public.players(current_team_id);

create trigger set_players_updated_at
before update on public.players
for each row execute function public.set_updated_at();


create table public.player_profiles (
  player_id integer primary key references public.players(player_id) on delete cascade,

  birthdate date,
  age integer,

  height text,              -- ex: '6-8'
  height_inches integer,
  weight_lbs integer,

  position text,
  jersey text,

  school text,
  country text,

  draft_year text,
  draft_round text,
  draft_number text,

  greatest_75_flag boolean,

  raw jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger set_player_profiles_updated_at
before update on public.player_profiles
for each row execute function public.set_updated_at();


create table public.seasons (
  season_id text primary key, -- ex: '2024-25'
  season_start_year integer not null,
  season_end_year integer not null,
  is_current boolean not null default false,

  created_at timestamptz not null default now()
);

-- ------------------------------------------------------------
-- Games
-- ------------------------------------------------------------

create table public.games (
  game_id text primary key, -- NBA GAME_ID, ex: '0022300001'

  season_id text references public.seasons(season_id),
  season_type text not null default 'Regular Season',

  game_date date,
  game_datetime timestamptz,

  matchup text, -- ex: 'LAL vs. DEN'

  home_team_id integer references public.teams(team_id),
  away_team_id integer references public.teams(team_id),

  home_team_abbreviation text,
  away_team_abbreviation text,

  home_points integer,
  away_points integer,

  winning_team_id integer references public.teams(team_id),

  game_status text,
  game_status_id integer,
  period integer,
  game_clock text,

  arena text,
  city text,
  state text,

  raw jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_games_season_id on public.games(season_id);
create index idx_games_game_date on public.games(game_date);
create index idx_games_home_team_id on public.games(home_team_id);
create index idx_games_away_team_id on public.games(away_team_id);

create trigger set_games_updated_at
before update on public.games
for each row execute function public.set_updated_at();

-- ------------------------------------------------------------
-- Player game stats
-- One row per player/team/game.
-- Supports traditional + advanced box score fields.
-- ------------------------------------------------------------

create table public.player_game_stats (
  id bigserial primary key,

  game_id text not null references public.games(game_id) on delete cascade,
  player_id integer not null references public.players(player_id),
  team_id integer not null references public.teams(team_id),
  opponent_team_id integer references public.teams(team_id),

  season_id text references public.seasons(season_id),
  season_type text,
  game_date date,

  team_abbreviation text,
  opponent_abbreviation text,

  is_home boolean,
  started boolean,
  position text,

  comment text,
  minutes numeric(8,3),

  -- traditional box score
  points integer,
  rebounds integer,
  offensive_rebounds integer,
  defensive_rebounds integer,
  assists integer,
  steals integer,
  blocks integer,
  turnovers integer,
  personal_fouls integer,
  plus_minus numeric(8,3),

  field_goals_made integer,
  field_goals_attempted integer,
  field_goal_pct numeric(8,4),

  three_pointers_made integer,
  three_pointers_attempted integer,
  three_point_pct numeric(8,4),

  free_throws_made integer,
  free_throws_attempted integer,
  free_throw_pct numeric(8,4),

  -- advanced box score
  true_shooting_pct numeric(8,4),
  effective_field_goal_pct numeric(8,4),
  usage_pct numeric(8,4),
  pace numeric(10,4),

  offensive_rating numeric(10,4),
  defensive_rating numeric(10,4),
  net_rating numeric(10,4),

  assist_pct numeric(8,4),
  assist_to_turnover_ratio numeric(10,4),
  assist_ratio numeric(10,4),

  offensive_rebound_pct numeric(8,4),
  defensive_rebound_pct numeric(8,4),
  rebound_pct numeric(8,4),

  turnover_pct numeric(8,4),
  pie numeric(8,4),

  -- derived app fields
  fantasy_points numeric(10,3),
  double_double boolean,
  triple_double boolean,

  source_endpoint text,
  raw jsonb,

  fetched_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint uq_player_game_stats unique (game_id, player_id, team_id)
);

create index idx_player_game_stats_player_season on public.player_game_stats(player_id, season_id);
create index idx_player_game_stats_game_id on public.player_game_stats(game_id);
create index idx_player_game_stats_team_id on public.player_game_stats(team_id);
create index idx_player_game_stats_game_date on public.player_game_stats(game_date);

create trigger set_player_game_stats_updated_at
before update on public.player_game_stats
for each row execute function public.set_updated_at();

-- ------------------------------------------------------------
-- Team game stats
-- One row per team/game.
-- ------------------------------------------------------------

create table public.team_game_stats (
  id bigserial primary key,

  game_id text not null references public.games(game_id) on delete cascade,
  team_id integer not null references public.teams(team_id),
  opponent_team_id integer references public.teams(team_id),

  season_id text references public.seasons(season_id),
  season_type text,
  game_date date,

  team_abbreviation text,
  opponent_abbreviation text,

  is_home boolean,
  won boolean,

  points integer,
  rebounds integer,
  offensive_rebounds integer,
  defensive_rebounds integer,
  assists integer,
  steals integer,
  blocks integer,
  turnovers integer,
  personal_fouls integer,
  plus_minus numeric(8,3),

  field_goals_made integer,
  field_goals_attempted integer,
  field_goal_pct numeric(8,4),

  three_pointers_made integer,
  three_pointers_attempted integer,
  three_point_pct numeric(8,4),

  free_throws_made integer,
  free_throws_attempted integer,
  free_throw_pct numeric(8,4),

  possessions numeric(10,4),
  pace numeric(10,4),
  offensive_rating numeric(10,4),
  defensive_rating numeric(10,4),
  net_rating numeric(10,4),

  assist_pct numeric(8,4),
  assist_to_turnover_ratio numeric(10,4),
  assist_ratio numeric(10,4),

  offensive_rebound_pct numeric(8,4),
  defensive_rebound_pct numeric(8,4),
  rebound_pct numeric(8,4),

  true_shooting_pct numeric(8,4),
  effective_field_goal_pct numeric(8,4),
  turnover_pct numeric(8,4),
  pie numeric(8,4),

  source_endpoint text,
  raw jsonb,

  fetched_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint uq_team_game_stats unique (game_id, team_id)
);

create index idx_team_game_stats_team_season on public.team_game_stats(team_id, season_id);
create index idx_team_game_stats_game_id on public.team_game_stats(game_id);
create index idx_team_game_stats_game_date on public.team_game_stats(game_date);

create trigger set_team_game_stats_updated_at
before update on public.team_game_stats
for each row execute function public.set_updated_at();

-- ------------------------------------------------------------
-- Player season stats
-- One row per player/team/season/stat mode.
-- stat_mode supports PerGame, Totals, Per36, Per100Possessions, Advanced, etc.
-- ------------------------------------------------------------

create table public.player_season_stats (
  id bigserial primary key,

  player_id integer not null references public.players(player_id),
  team_id integer references public.teams(team_id),

  season_id text not null references public.seasons(season_id),
  season_type text not null default 'Regular Season',
  stat_mode text not null default 'PerGame',

  team_abbreviation text,
  age numeric(5,2),

  games_played integer,
  games_started integer,

  minutes numeric(12,4),

  points numeric(12,4),
  rebounds numeric(12,4),
  offensive_rebounds numeric(12,4),
  defensive_rebounds numeric(12,4),
  assists numeric(12,4),
  steals numeric(12,4),
  blocks numeric(12,4),
  turnovers numeric(12,4),
  personal_fouls numeric(12,4),

  field_goals_made numeric(12,4),
  field_goals_attempted numeric(12,4),
  field_goal_pct numeric(8,4),

  three_pointers_made numeric(12,4),
  three_pointers_attempted numeric(12,4),
  three_point_pct numeric(8,4),

  free_throws_made numeric(12,4),
  free_throws_attempted numeric(12,4),
  free_throw_pct numeric(8,4),

  plus_minus numeric(12,4),

  true_shooting_pct numeric(8,4),
  effective_field_goal_pct numeric(8,4),
  usage_pct numeric(8,4),
  pace numeric(10,4),

  offensive_rating numeric(10,4),
  defensive_rating numeric(10,4),
  net_rating numeric(10,4),

  assist_pct numeric(8,4),
  assist_to_turnover_ratio numeric(10,4),
  assist_ratio numeric(10,4),

  offensive_rebound_pct numeric(8,4),
  defensive_rebound_pct numeric(8,4),
  rebound_pct numeric(8,4),

  turnover_pct numeric(8,4),
  pie numeric(8,4),

  nba_rank jsonb,
  source_endpoint text,
  raw jsonb,

  fetched_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint uq_player_season_stats unique (
    player_id,
    team_id,
    season_id,
    season_type,
    stat_mode
  )
);

create index idx_player_season_stats_player_id on public.player_season_stats(player_id);
create index idx_player_season_stats_season_id on public.player_season_stats(season_id);
create index idx_player_season_stats_team_id on public.player_season_stats(team_id);

create trigger set_player_season_stats_updated_at
before update on public.player_season_stats
for each row execute function public.set_updated_at();

-- ------------------------------------------------------------
-- Team season stats
-- ------------------------------------------------------------

create table public.team_season_stats (
  id bigserial primary key,

  team_id integer not null references public.teams(team_id),

  season_id text not null references public.seasons(season_id),
  season_type text not null default 'Regular Season',
  stat_mode text not null default 'PerGame',

  team_abbreviation text,

  games_played integer,
  wins integer,
  losses integer,
  win_pct numeric(8,4),

  minutes numeric(12,4),

  points numeric(12,4),
  rebounds numeric(12,4),
  offensive_rebounds numeric(12,4),
  defensive_rebounds numeric(12,4),
  assists numeric(12,4),
  steals numeric(12,4),
  blocks numeric(12,4),
  turnovers numeric(12,4),
  personal_fouls numeric(12,4),

  field_goals_made numeric(12,4),
  field_goals_attempted numeric(12,4),
  field_goal_pct numeric(8,4),

  three_pointers_made numeric(12,4),
  three_pointers_attempted numeric(12,4),
  three_point_pct numeric(8,4),

  free_throws_made numeric(12,4),
  free_throws_attempted numeric(12,4),
  free_throw_pct numeric(8,4),

  plus_minus numeric(12,4),

  possessions numeric(12,4),
  pace numeric(10,4),
  offensive_rating numeric(10,4),
  defensive_rating numeric(10,4),
  net_rating numeric(10,4),

  assist_pct numeric(8,4),
  assist_to_turnover_ratio numeric(10,4),
  assist_ratio numeric(10,4),

  offensive_rebound_pct numeric(8,4),
  defensive_rebound_pct numeric(8,4),
  rebound_pct numeric(8,4),

  true_shooting_pct numeric(8,4),
  effective_field_goal_pct numeric(8,4),
  turnover_pct numeric(8,4),
  pie numeric(8,4),

  nba_rank jsonb,
  source_endpoint text,
  raw jsonb,

  fetched_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint uq_team_season_stats unique (
    team_id,
    season_id,
    season_type,
    stat_mode
  )
);

create index idx_team_season_stats_team_id on public.team_season_stats(team_id);
create index idx_team_season_stats_season_id on public.team_season_stats(season_id);

create trigger set_team_season_stats_updated_at
before update on public.team_season_stats
for each row execute function public.set_updated_at();

-- ------------------------------------------------------------
-- Raw endpoint storage
-- ------------------------------------------------------------

create table public.raw_api_responses (
  id bigserial primary key,

  endpoint_name text not null,
  endpoint_params jsonb not null default '{}'::jsonb,
  response_json jsonb not null,

  response_hash text,

  season_id text,
  game_id text,
  player_id integer,
  team_id integer,

  fetched_at timestamptz not null default now(),

  constraint uq_raw_api_response_hash unique (endpoint_name, response_hash)
);

create index idx_raw_api_endpoint on public.raw_api_responses(endpoint_name);
create index idx_raw_api_season_id on public.raw_api_responses(season_id);
create index idx_raw_api_game_id on public.raw_api_responses(game_id);
create index idx_raw_api_player_id on public.raw_api_responses(player_id);
create index idx_raw_api_team_id on public.raw_api_responses(team_id);
create index idx_raw_api_response_json_gin on public.raw_api_responses using gin (response_json);

-- ------------------------------------------------------------
-- Ingestion run log
-- ------------------------------------------------------------

create table public.ingestion_runs (
  id bigserial primary key,

  job_name text not null,
  status text not null check (status in ('started', 'success', 'failed', 'partial')),

  season_id text,
  season_type text,
  target_date date,

  started_at timestamptz not null default now(),
  finished_at timestamptz,

  rows_inserted integer not null default 0,
  rows_updated integer not null default 0,
  rows_failed integer not null default 0,

  error_message text,
  metadata jsonb not null default '{}'::jsonb
);

create index idx_ingestion_runs_job_name on public.ingestion_runs(job_name);
create index idx_ingestion_runs_status on public.ingestion_runs(status);
create index idx_ingestion_runs_started_at on public.ingestion_runs(started_at);