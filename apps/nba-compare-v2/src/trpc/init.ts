import { initTRPC } from "@trpc/server";
import { cache } from "react";

import { mockPlayerRepository } from "@/server/player/repository";

export const createTRPCContext = cache(async () => ({
  playerRepository: mockPlayerRepository,
}));

const t = initTRPC
  .context<Awaited<ReturnType<typeof createTRPCContext>>>()
  .create();

export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;
