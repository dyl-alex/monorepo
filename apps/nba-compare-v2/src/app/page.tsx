import { dehydrate, HydrationBoundary } from "@tanstack/react-query";

import { HomeDashboard } from "@/features/player-dashboard/home-dashboard";
import type { StatsView } from "@/features/player-dashboard/dashboard-state";
import { getQueryClient, trpc } from "@/trpc/server";

const DEFAULT_SEASON = "2025-26";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const playerIdValue = Array.isArray(params.playerId)
    ? params.playerId[0]
    : params.playerId;
  const parsedPlayerId = playerIdValue ? Number(playerIdValue) : null;
  const playerId =
    parsedPlayerId && Number.isInteger(parsedPlayerId) && parsedPlayerId > 0
      ? parsedPlayerId
      : null;
  const view: StatsView = params.view === "games" ? "games" : "career";
  const seasonValue = Array.isArray(params.season)
    ? params.season[0]
    : params.season;
  const season = /^\d{4}-\d{2}$/.test(seasonValue ?? "")
    ? seasonValue!
    : DEFAULT_SEASON;
  const queryClient = getQueryClient();

  void queryClient.prefetchQuery(
    trpc.player.search.queryOptions({ query: "", limit: 10 }),
  );

  if (playerId != null) {
    void queryClient.prefetchQuery(
      trpc.player.profile.queryOptions({ playerId }),
    );
    void queryClient.prefetchQuery(
      trpc.player.seasonStats.queryOptions({ playerId }),
    );
    if (view === "games") {
      void queryClient.prefetchQuery(
        trpc.player.gameStats.queryOptions({ playerId, seasonId: season }),
      );
    }
  }

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <HomeDashboard playerId={playerId} view={view} season={season} />
    </HydrationBoundary>
  );
}
