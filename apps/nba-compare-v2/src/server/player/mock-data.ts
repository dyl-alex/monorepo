import type {
  PlayerGameStatRow,
  PlayerProfileRow,
  PlayerRow,
  PlayerSeasonStatRow,
} from "./types";

const timestamp = "2026-06-01T00:00:00.000Z";

const playerSeeds = [
  [2544, "LeBron", "James", "LAL", "Lakers", 1610612747, "F", "23"],
  [203999, "Nikola", "Jokic", "DEN", "Nuggets", 1610612743, "C", "15"],
  [1628369, "Jayson", "Tatum", "BOS", "Celtics", 1610612738, "F", "0"],
  [1629029, "Luka", "Doncic", "LAL", "Lakers", 1610612747, "G", "77"],
  [
    1628983,
    "Shai",
    "Gilgeous-Alexander",
    "OKC",
    "Thunder",
    1610612760,
    "G",
    "2",
  ],
  [203507, "Giannis", "Antetokounmpo", "MIL", "Bucks", 1610612749, "F", "34"],
  [201939, "Stephen", "Curry", "GSW", "Warriors", 1610612744, "G", "30"],
  [1629027, "Trae", "Young", "ATL", "Hawks", 1610612737, "G", "11"],
  [1630162, "Anthony", "Edwards", "MIN", "Timberwolves", 1610612750, "G", "5"],
  [1631094, "Paolo", "Banchero", "ORL", "Magic", 1610612753, "F", "5"],
  [1627783, "Pascal", "Siakam", "IND", "Pacers", 1610612754, "F", "43"],
  [1627759, "Jaylen", "Brown", "BOS", "Celtics", 1610612738, "G-F", "7"],
] as const;

export const mockPlayers: PlayerRow[] = playerSeeds.map(
  ([playerId, firstName, lastName, abbreviation, teamName, teamId]) => ({
    player_id: playerId,
    first_name: firstName,
    last_name: lastName,
    full_name: `${firstName} ${lastName}`,
    player_slug: `${firstName}-${lastName}`.toLowerCase(),
    player_code: `${firstName[0]}${lastName}`.toLowerCase(),
    is_active: true,
    roster_status: "Active",
    from_year: 2018,
    to_year: 2026,
    current_team_id: teamId,
    current_team_abbreviation: abbreviation,
    current_team_city: null,
    current_team_name: teamName,
    headshot_url: "/mock/player-placeholder.svg",
    raw: null,
    created_at: timestamp,
    updated_at: timestamp,
  }),
);

export const mockProfiles: PlayerProfileRow[] = playerSeeds.map(
  ([playerId, , , , , , position, jersey], index) => ({
    player_id: playerId,
    birthdate: `19${84 + (index % 12)}-01-01`,
    age: 27 + (index % 8),
    height:
      position === "C" ? "6-11" : position.startsWith("G") ? "6-5" : "6-8",
    height_inches: position === "C" ? 83 : position.startsWith("G") ? 77 : 80,
    weight_lbs: 205 + index * 4,
    position,
    jersey,
    school: index % 3 === 0 ? null : "Mock University",
    country: index % 4 === 0 ? "International" : "USA",
    draft_year: String(2003 + index),
    draft_round: "1",
    draft_number: String(index + 1),
    greatest_75_flag: index === 0 || index === 6,
    raw: null,
    created_at: timestamp,
    updated_at: timestamp,
  }),
);

const seasons = ["2023-24", "2024-25", "2025-26"] as const;

function seasonStat(
  player: PlayerRow,
  season: string,
  seasonIndex: number,
  playerIndex: number,
): PlayerSeasonStatRow {
  const points = 20 + playerIndex * 0.7 + seasonIndex * 1.2;
  const assists = 4 + (playerIndex % 5) + seasonIndex * 0.2;
  const rebounds = 5 + (playerIndex % 6) + seasonIndex * 0.3;
  return {
    id: playerIndex * 10 + seasonIndex + 1,
    player_id: player.player_id,
    team_id: player.current_team_id,
    season_id: season,
    season_type: "Regular Season",
    stat_mode: "PerGame",
    team_abbreviation: player.current_team_abbreviation,
    age: 25 + playerIndex + seasonIndex,
    games_played: 72 - playerIndex,
    games_started: 68 - (playerIndex % 4),
    minutes: 32.4 + seasonIndex,
    points,
    rebounds,
    offensive_rebounds: 1.1 + playerIndex * 0.08,
    defensive_rebounds: rebounds - 1.1,
    assists,
    steals: 0.9 + (playerIndex % 4) * 0.2,
    blocks: 0.5 + (playerIndex % 3) * 0.3,
    turnovers: 2.1 + (playerIndex % 4) * 0.3,
    personal_fouls: 1.8 + (playerIndex % 3) * 0.2,
    field_goals_made: 7.8 + playerIndex * 0.25,
    field_goals_attempted: 15.1 + playerIndex * 0.35,
    field_goal_pct: 0.486 + playerIndex * 0.003,
    three_pointers_made: 1.8 + (playerIndex % 5) * 0.25,
    three_pointers_attempted: 5.1 + (playerIndex % 5) * 0.4,
    three_point_pct: 0.351 + (playerIndex % 6) * 0.006,
    free_throws_made: 4.1 + playerIndex * 0.13,
    free_throws_attempted: 5.2 + playerIndex * 0.14,
    free_throw_pct: playerIndex === 9 ? null : 0.77 + (playerIndex % 7) * 0.018,
    plus_minus: 2.3 + seasonIndex + playerIndex * 0.2,
    true_shooting_pct: 0.57 + playerIndex * 0.004,
    effective_field_goal_pct: 0.53 + playerIndex * 0.003,
    usage_pct: 0.24 + playerIndex * 0.006,
    pace: 98.2 + playerIndex * 0.3,
    offensive_rating: 112.4 + playerIndex * 0.8,
    defensive_rating: 110.1 + playerIndex * 0.5,
    net_rating: 2.3 + playerIndex * 0.3,
    assist_pct: 0.18 + playerIndex * 0.01,
    assist_to_turnover_ratio: assists / 2.4,
    assist_ratio: 18 + playerIndex * 0.7,
    offensive_rebound_pct: 0.04 + playerIndex * 0.002,
    defensive_rebound_pct: 0.14 + playerIndex * 0.005,
    rebound_pct: 0.09 + playerIndex * 0.003,
    turnover_pct: 0.1 + playerIndex * 0.002,
    pie: 0.12 + playerIndex * 0.004,
    nba_rank: null,
    source_endpoint: "mock/playerdashboardbyyearoveryear",
    raw: null,
    fetched_at: timestamp,
    created_at: timestamp,
    updated_at: timestamp,
  };
}

export const mockSeasonStats = mockPlayers.flatMap((player, playerIndex) =>
  seasons.map((season, seasonIndex) =>
    seasonStat(player, season, seasonIndex, playerIndex),
  ),
);

function gameStat(
  player: PlayerRow,
  gameIndex: number,
  playerIndex: number,
): PlayerGameStatRow {
  const points = 18 + ((gameIndex * 4 + playerIndex) % 19);
  const rebounds = 4 + ((gameIndex + playerIndex) % 10);
  const assists = 3 + ((gameIndex * 2 + playerIndex) % 9);
  const made = 6 + ((gameIndex + playerIndex) % 6);
  const attempted = made + 7 + (gameIndex % 3);
  return {
    id: playerIndex * 100 + gameIndex + 1,
    game_id: `00225${String(playerIndex).padStart(2, "0")}${String(gameIndex).padStart(3, "0")}`,
    player_id: player.player_id,
    team_id: player.current_team_id ?? 0,
    opponent_team_id: 1610612700 + gameIndex,
    season_id: "2025-26",
    season_type: "Regular Season",
    game_date: `2026-0${(gameIndex % 3) + 1}-${String(5 + gameIndex).padStart(2, "0")}`,
    team_abbreviation: player.current_team_abbreviation,
    opponent_abbreviation: [
      "NYK",
      "MIA",
      "PHX",
      "DAL",
      "CLE",
      "SAC",
      "CHI",
      "TOR",
    ][gameIndex],
    is_home: gameIndex % 2 === 0,
    started: true,
    position: mockProfiles[playerIndex]?.position ?? null,
    comment: null,
    minutes: 30 + (gameIndex % 7),
    points,
    rebounds,
    offensive_rebounds: 1 + (gameIndex % 3),
    defensive_rebounds: rebounds - 1,
    assists,
    steals: gameIndex % 4,
    blocks: gameIndex % 3,
    turnovers: 1 + (gameIndex % 5),
    personal_fouls: 1 + (gameIndex % 4),
    plus_minus: -4 + gameIndex * 2,
    field_goals_made: made,
    field_goals_attempted: attempted,
    field_goal_pct: made / attempted,
    three_pointers_made: 1 + (gameIndex % 4),
    three_pointers_attempted: 4 + (gameIndex % 5),
    three_point_pct: (1 + (gameIndex % 4)) / (4 + (gameIndex % 5)),
    free_throws_made: 3 + (gameIndex % 4),
    free_throws_attempted: 4 + (gameIndex % 4),
    free_throw_pct: (3 + (gameIndex % 4)) / (4 + (gameIndex % 4)),
    true_shooting_pct: 0.54 + gameIndex * 0.012,
    effective_field_goal_pct: 0.51 + gameIndex * 0.01,
    usage_pct: 0.23 + gameIndex * 0.008,
    pace: 97 + gameIndex * 0.7,
    offensive_rating: 108 + gameIndex * 1.5,
    defensive_rating: 112 - gameIndex * 0.7,
    net_rating: -4 + gameIndex * 2.2,
    assist_pct: 0.17 + gameIndex * 0.012,
    assist_to_turnover_ratio: assists / (1 + (gameIndex % 5)),
    assist_ratio: 17 + gameIndex,
    offensive_rebound_pct: 0.04 + gameIndex * 0.002,
    defensive_rebound_pct: 0.13 + gameIndex * 0.006,
    rebound_pct: 0.09 + gameIndex * 0.004,
    turnover_pct: 0.09 + gameIndex * 0.004,
    pie: 0.1 + gameIndex * 0.009,
    fantasy_points: points + rebounds * 1.2 + assists * 1.5,
    double_double:
      [points, rebounds, assists].filter((value) => value >= 10).length >= 2,
    triple_double: false,
    source_endpoint: "mock/playergamelog",
    raw: null,
    fetched_at: timestamp,
    created_at: timestamp,
    updated_at: timestamp,
  };
}

export const mockGameStats = mockPlayers.flatMap((player, playerIndex) =>
  Array.from({ length: 8 }, (_, gameIndex) =>
    gameStat(player, gameIndex, playerIndex),
  ),
);
