import { describe, expect, it } from "vitest";

import { mockPlayerRepository } from "@/server/player/repository";

import { playerRouter } from "./player";

const caller = playerRouter.createCaller({
  playerRepository: mockPlayerRepository,
});

describe("playerRouter", () => {
  it("validates and serves player queries", async () => {
    const results = await caller.search({ query: "jay", limit: 10 });
    expect(results.map((player) => player.full_name)).toEqual([
      "Jayson Tatum",
      "Jaylen Brown",
    ]);
  });

  it("throws NOT_FOUND for an unknown profile", async () => {
    await expect(caller.profile({ playerId: 999999 })).rejects.toMatchObject({
      code: "NOT_FOUND",
    });
  });

  it("rejects malformed season identifiers", async () => {
    await expect(
      caller.gameStats({ playerId: 2544, seasonId: "2026" }),
    ).rejects.toBeTruthy();
  });
});
