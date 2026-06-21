import type { Database } from "@repo/db-types";

type Tables = Database["public"]["Tables"];

export type PlayerRow = Tables["players"]["Row"];
export type PlayerProfileRow = Tables["player_profiles"]["Row"];
export type PlayerSeasonStatRow = Tables["player_season_stats"]["Row"];
export type PlayerGameStatRow = Tables["player_game_stats"]["Row"];

export type PlayerSearchItem = Pick<
  PlayerRow,
  | "player_id"
  | "full_name"
  | "current_team_abbreviation"
  | "current_team_name"
  | "headshot_url"
>;

export type PlayerProfile = {
  player: PlayerRow;
  profile: PlayerProfileRow | null;
};
