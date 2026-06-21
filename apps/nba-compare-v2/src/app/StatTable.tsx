"use client";

import {
  useSuspenseQuery,
  type UseSuspenseQueryOptions,
} from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTRPC } from "@/trpc/client";
import type {
  PlayerGameStatRow,
  PlayerSeasonStatRow,
} from "@/server/player/types";

import {
  dashboardUrl,
  type StatsView,
} from "@/features/player-dashboard/dashboard-state";
import {
  formatDate,
  formatInteger,
  formatNumber,
  formatPercent,
} from "@/features/player-dashboard/format";

type StatGroup = "basic" | "advanced";

export default function StatTable({
  playerId,
  view,
  season,
}: {
  playerId: number;
  view: StatsView;
  season: string;
}) {
  const trpc = useTRPC();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [group, setGroup] = useState<StatGroup>("basic");
  const seasonOptions = trpc.player.seasonStats.queryOptions({
    playerId,
  }) as unknown as UseSuspenseQueryOptions<PlayerSeasonStatRow[]>;
  const seasons = useSuspenseQuery(seasonOptions).data;

  const changeView = (next: string) => {
    const nextView = next as StatsView;
    router.push(
      dashboardUrl(searchParams, {
        view: nextView,
        season: nextView === "games" ? season : null,
      }),
    );
  };

  return (
    <Card className="h-full">
      <CardHeader className="border-b sm:grid-cols-[1fr_auto]">
        <div>
          <CardTitle>Performance</CardTitle>
          <CardDescription>
            Traditional and advanced NBA statistics.
          </CardDescription>
        </div>
        <div className="flex flex-wrap items-center gap-2 pt-2 sm:pt-0">
          {view === "games" && (
            <Select
              value={season}
              onValueChange={(value) =>
                router.push(
                  dashboardUrl(searchParams, { view: "games", season: value }),
                )
              }
            >
              <SelectTrigger aria-label="Season" className="w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {seasons.map((row) => (
                  <SelectItem key={row.season_id} value={row.season_id}>
                    {row.season_id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Tabs value={view} onValueChange={changeView}>
            <TabsList>
              <TabsTrigger value="career">Career</TabsTrigger>
              <TabsTrigger value="games">Game Log</TabsTrigger>
            </TabsList>
          </Tabs>
          <Tabs
            value={group}
            onValueChange={(value) => setGroup(value as StatGroup)}
          >
            <TabsList variant="line">
              <TabsTrigger value="basic">Basic</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {view === "career" ? (
          seasons.length ? (
            <CareerTable rows={seasons} group={group} />
          ) : (
            <Empty label="No season data available." />
          )
        ) : (
          <GameDataTable playerId={playerId} season={season} group={group} />
        )}
      </CardContent>
    </Card>
  );
}

function GameDataTable({
  playerId,
  season,
  group,
}: {
  playerId: number;
  season: string;
  group: StatGroup;
}) {
  const trpc = useTRPC();
  const gameOptions = trpc.player.gameStats.queryOptions({
    playerId,
    seasonId: season,
  }) as unknown as UseSuspenseQueryOptions<PlayerGameStatRow[]>;
  const games = useSuspenseQuery(gameOptions).data;

  return games.length ? (
    <GameTable rows={games} group={group} />
  ) : (
    <Empty label="No games available for this season." />
  );
}

function CareerTable({
  rows,
  group,
}: {
  rows: PlayerSeasonStatRow[];
  group: StatGroup;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {(group === "basic"
            ? [
                "Season",
                "Team",
                "GP",
                "GS",
                "MIN",
                "PTS",
                "REB",
                "AST",
                "STL",
                "BLK",
                "TOV",
                "PF",
                "FG%",
                "3P%",
                "FT%",
                "+/-",
              ]
            : [
                "Season",
                "TS%",
                "eFG%",
                "USG%",
                "ORtg",
                "DRtg",
                "Net",
                "AST%",
                "REB%",
                "TOV%",
                "Pace",
                "PIE",
              ]
          ).map((label) => (
            <TableHead key={label}>{label}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) =>
          group === "basic" ? (
            <TableRow key={row.id}>
              <TableCell className="font-medium">{row.season_id}</TableCell>
              <TableCell>{row.team_abbreviation ?? "—"}</TableCell>
              <TableCell>{formatInteger(row.games_played)}</TableCell>
              <TableCell>{formatInteger(row.games_started)}</TableCell>
              <TableCell>{formatNumber(row.minutes)}</TableCell>
              <TableCell>{formatNumber(row.points)}</TableCell>
              <TableCell>{formatNumber(row.rebounds)}</TableCell>
              <TableCell>{formatNumber(row.assists)}</TableCell>
              <TableCell>{formatNumber(row.steals)}</TableCell>
              <TableCell>{formatNumber(row.blocks)}</TableCell>
              <TableCell>{formatNumber(row.turnovers)}</TableCell>
              <TableCell>{formatNumber(row.personal_fouls)}</TableCell>
              <TableCell>{formatPercent(row.field_goal_pct)}</TableCell>
              <TableCell>{formatPercent(row.three_point_pct)}</TableCell>
              <TableCell>{formatPercent(row.free_throw_pct)}</TableCell>
              <TableCell>{formatNumber(row.plus_minus)}</TableCell>
            </TableRow>
          ) : (
            <TableRow key={row.id}>
              <TableCell className="font-medium">{row.season_id}</TableCell>
              <TableCell>{formatPercent(row.true_shooting_pct)}</TableCell>
              <TableCell>
                {formatPercent(row.effective_field_goal_pct)}
              </TableCell>
              <TableCell>{formatPercent(row.usage_pct)}</TableCell>
              <TableCell>{formatNumber(row.offensive_rating)}</TableCell>
              <TableCell>{formatNumber(row.defensive_rating)}</TableCell>
              <TableCell>{formatNumber(row.net_rating)}</TableCell>
              <TableCell>{formatPercent(row.assist_pct)}</TableCell>
              <TableCell>{formatPercent(row.rebound_pct)}</TableCell>
              <TableCell>{formatPercent(row.turnover_pct)}</TableCell>
              <TableCell>{formatNumber(row.pace)}</TableCell>
              <TableCell>{formatNumber(row.pie, 3)}</TableCell>
            </TableRow>
          ),
        )}
      </TableBody>
    </Table>
  );
}

function GameTable({
  rows,
  group,
}: {
  rows: PlayerGameStatRow[];
  group: StatGroup;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {(group === "basic"
            ? [
                "Date",
                "Matchup",
                "MIN",
                "PTS",
                "REB",
                "AST",
                "STL",
                "BLK",
                "TOV",
                "PF",
                "FG",
                "3PT",
                "FT",
                "+/-",
              ]
            : [
                "Date",
                "TS%",
                "eFG%",
                "USG%",
                "ORtg",
                "DRtg",
                "Net",
                "AST%",
                "REB%",
                "TOV%",
                "Pace",
                "PIE",
              ]
          ).map((label) => (
            <TableHead key={label}>{label}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) =>
          group === "basic" ? (
            <TableRow key={row.id}>
              <TableCell className="font-medium">
                {formatDate(row.game_date)}
              </TableCell>
              <TableCell>
                {row.is_home ? "vs." : "@"} {row.opponent_abbreviation ?? "—"}
              </TableCell>
              <TableCell>{formatNumber(row.minutes)}</TableCell>
              <TableCell>{formatInteger(row.points)}</TableCell>
              <TableCell>{formatInteger(row.rebounds)}</TableCell>
              <TableCell>{formatInteger(row.assists)}</TableCell>
              <TableCell>{formatInteger(row.steals)}</TableCell>
              <TableCell>{formatInteger(row.blocks)}</TableCell>
              <TableCell>{formatInteger(row.turnovers)}</TableCell>
              <TableCell>{formatInteger(row.personal_fouls)}</TableCell>
              <TableCell>
                {formatInteger(row.field_goals_made)}-
                {formatInteger(row.field_goals_attempted)}
              </TableCell>
              <TableCell>
                {formatInteger(row.three_pointers_made)}-
                {formatInteger(row.three_pointers_attempted)}
              </TableCell>
              <TableCell>
                {formatInteger(row.free_throws_made)}-
                {formatInteger(row.free_throws_attempted)}
              </TableCell>
              <TableCell>{formatNumber(row.plus_minus)}</TableCell>
            </TableRow>
          ) : (
            <TableRow key={row.id}>
              <TableCell className="font-medium">
                {formatDate(row.game_date)}
              </TableCell>
              <TableCell>{formatPercent(row.true_shooting_pct)}</TableCell>
              <TableCell>
                {formatPercent(row.effective_field_goal_pct)}
              </TableCell>
              <TableCell>{formatPercent(row.usage_pct)}</TableCell>
              <TableCell>{formatNumber(row.offensive_rating)}</TableCell>
              <TableCell>{formatNumber(row.defensive_rating)}</TableCell>
              <TableCell>{formatNumber(row.net_rating)}</TableCell>
              <TableCell>{formatPercent(row.assist_pct)}</TableCell>
              <TableCell>{formatPercent(row.rebound_pct)}</TableCell>
              <TableCell>{formatPercent(row.turnover_pct)}</TableCell>
              <TableCell>{formatNumber(row.pace)}</TableCell>
              <TableCell>{formatNumber(row.pie, 3)}</TableCell>
            </TableRow>
          ),
        )}
      </TableBody>
    </Table>
  );
}

function Empty({ label }: { label: string }) {
  return (
    <div className="flex min-h-52 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
      {label}
    </div>
  );
}
