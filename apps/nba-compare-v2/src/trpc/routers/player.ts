import { TRPCError } from "@trpc/server";
import { z } from "zod";

import { createTRPCRouter, publicProcedure } from "../init";

export const playerRouter = createTRPCRouter({
  search: publicProcedure
    .input(
      z.object({
        query: z.string().trim().max(80).default(""),
        limit: z.number().int().min(1).max(10).default(10),
      }),
    )
    .query(({ ctx, input }) =>
      ctx.playerRepository.search(input.query, input.limit),
    ),
  profile: publicProcedure
    .input(z.object({ playerId: z.number().int().positive() }))
    .query(async ({ ctx, input }) => {
      const profile = await ctx.playerRepository.profile(input.playerId);
      if (!profile) {
        throw new TRPCError({ code: "NOT_FOUND", message: "Player not found" });
      }
      return profile;
    }),
  seasonStats: publicProcedure
    .input(z.object({ playerId: z.number().int().positive() }))
    .query(({ ctx, input }) =>
      ctx.playerRepository.seasonStats(input.playerId),
    ),
  gameStats: publicProcedure
    .input(
      z.object({
        playerId: z.number().int().positive(),
        seasonId: z.string().regex(/^\d{4}-\d{2}$/),
      }),
    )
    .query(({ ctx, input }) =>
      ctx.playerRepository.gameStats(input.playerId, input.seasonId),
    ),
});
