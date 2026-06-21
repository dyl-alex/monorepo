import {
  mockGameStats,
  mockPlayers,
  mockProfiles,
  mockSeasonStats,
} from "./mock-data";
import type {
  PlayerGameStatRow,
  PlayerProfile,
  PlayerSearchItem,
  PlayerSeasonStatRow,
} from "./types";

export interface PlayerRepository {
  search(query: string, limit: number): Promise<PlayerSearchItem[]>;
  profile(playerId: number): Promise<PlayerProfile | null>;
  seasonStats(playerId: number): Promise<PlayerSeasonStatRow[]>;
  gameStats(playerId: number, seasonId: string): Promise<PlayerGameStatRow[]>;
}

export const mockPlayerRepository: PlayerRepository = {
  async search(query, limit) {
    const normalized = query.trim().toLocaleLowerCase();
    return mockPlayers
      .filter((player) =>
        normalized
          ? player.full_name.toLocaleLowerCase().includes(normalized)
          : true,
      )
      .slice(0, Math.min(limit, 10))
      .map((player) => ({
        player_id: player.player_id,
        full_name: player.full_name,
        current_team_abbreviation: player.current_team_abbreviation,
        current_team_name: player.current_team_name,
        headshot_url: player.headshot_url,
      }));
  },
  async profile(playerId) {
    const player = mockPlayers.find((item) => item.player_id === playerId);
    if (!player) return null;
    return {
      player,
      profile: mockProfiles.find((item) => item.player_id === playerId) ?? null,
    };
  },
  async seasonStats(playerId) {
    return mockSeasonStats
      .filter((item) => item.player_id === playerId)
      .sort((a, b) => b.season_id.localeCompare(a.season_id));
  },
  async gameStats(playerId, seasonId) {
    return mockGameStats
      .filter(
        (item) => item.player_id === playerId && item.season_id === seasonId,
      )
      .sort((a, b) => (b.game_date ?? "").localeCompare(a.game_date ?? ""));
  },
};
