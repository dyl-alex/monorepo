import { describe, expect, it } from "vitest";

import {
  mockGameStats,
  mockPlayers,
  mockProfiles,
  mockSeasonStats,
} from "./mock-data";
import { mockPlayerRepository } from "./repository";

describe("mockPlayerRepository", () => {
  it("provides schema-shaped data for at least twelve players", () => {
    expect(mockPlayers).toHaveLength(12);
    expect(mockProfiles).toHaveLength(12);
    expect(mockSeasonStats).toHaveLength(36);
    expect(mockGameStats.length).toBeGreaterThanOrEqual(96);
    expect(
      mockPlayers.every((player) => player.created_at && player.updated_at),
    ).toBe(true);
  });

  it("searches case-insensitively and caps results at ten", async () => {
    await expect(mockPlayerRepository.search("jAmEs", 10)).resolves.toEqual([
      expect.objectContaining({ full_name: "LeBron James" }),
    ]);
    await expect(mockPlayerRepository.search("", 50)).resolves.toHaveLength(10);
  });

  it("returns deterministic career and game records", async () => {
    const playerId = mockPlayers[0]!.player_id;
    const seasons = await mockPlayerRepository.seasonStats(playerId);
    const games = await mockPlayerRepository.gameStats(playerId, "2025-26");

    expect(seasons.map((row) => row.season_id)).toEqual([
      "2025-26",
      "2024-25",
      "2023-24",
    ]);
    expect(games).toHaveLength(8);
    expect(games[0]).toMatchObject({
      player_id: playerId,
      season_id: "2025-26",
    });
  });

  it("uses empty collections for missing data without throwing", async () => {
    await expect(mockPlayerRepository.seasonStats(999999)).resolves.toEqual([]);
    await expect(
      mockPlayerRepository.gameStats(2544, "1999-00"),
    ).resolves.toEqual([]);
    await expect(mockPlayerRepository.profile(999999)).resolves.toBeNull();
  });
});
