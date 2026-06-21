"use client";

import { Activity, Search } from "lucide-react";

import StatContainer from "@/app/StatContainer";
import StatTable from "@/app/StatTable";
import { QueryPanel } from "@/components/query-panel";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type { StatsView } from "./dashboard-state";
import {
  ChartSkeleton,
  ProfileSkeleton,
  StatsSkeleton,
} from "./dashboard-skeletons";
import { PlayerProfileCard } from "./player-profile-card";
import { PlayerSearch } from "./player-search";
import { StatsChart } from "./stats-chart";

export function HomeDashboard({
  playerId,
  view,
  season,
}: {
  playerId: number | null;
  view: StatsView;
  season: string;
}) {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
      <Card className="relative overflow-visible bg-gradient-to-br from-card via-card to-muted/40">
        <div className="pointer-events-none absolute right-8 top-4 hidden size-32 rounded-full bg-primary/5 blur-3xl sm:block" />
        <CardHeader className="max-w-3xl">
          <div className="mb-2 flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <Activity className="size-5" />
          </div>
          <CardTitle className="text-2xl sm:text-3xl">
            Explore NBA performance
          </CardTitle>
          <CardDescription className="text-base">
            Search for a player to explore career trends, season game logs, and
            advanced metrics.
          </CardDescription>
        </CardHeader>
        <CardContent className="max-w-2xl">
          <PlayerSearch selectedPlayerId={playerId} />
        </CardContent>
      </Card>

      {playerId == null ? (
        <Card className="border-dashed bg-muted/20">
          <CardContent className="flex min-h-56 flex-col items-center justify-center gap-3 text-center">
            <div className="flex size-11 items-center justify-center rounded-full bg-muted">
              <Search className="size-5 text-muted-foreground" />
            </div>
            <div>
              <p className="font-medium">Select a player to get started</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Statistics and charts will appear here.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <StatContainer
            profile={
              <QueryPanel
                fallback={<ProfileSkeleton />}
                errorMessage="Error getting player profile."
              >
                <PlayerProfileCard playerId={playerId} />
              </QueryPanel>
            }
            stats={
              <QueryPanel
                fallback={<StatsSkeleton />}
                errorMessage={
                  view === "games"
                    ? "Error getting game stats."
                    : "Error getting season stats."
                }
              >
                <StatTable playerId={playerId} view={view} season={season} />
              </QueryPanel>
            }
          />
          <QueryPanel
            fallback={<ChartSkeleton />}
            errorMessage={
              view === "games"
                ? "Error getting game chart data."
                : "Error getting season chart data."
            }
          >
            <StatsChart playerId={playerId} view={view} season={season} />
          </QueryPanel>
        </>
      )}
    </div>
  );
}
