import { createTRPCRouter } from "../init";
import { playerRouter } from "./player";

export const appRouter = createTRPCRouter({
  player: playerRouter,
});

export type AppRouter = typeof appRouter;
