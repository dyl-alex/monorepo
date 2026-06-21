"use client";

import {
  useSuspenseQuery,
  type UseSuspenseQueryOptions,
} from "@tanstack/react-query";
import { BarChart3, LineChart as LineChartIcon } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTRPC } from "@/trpc/client";
import type {
  PlayerGameStatRow,
  PlayerSeasonStatRow,
} from "@/server/player/types";

import type { StatsView } from "./dashboard-state";

const metrics = {
  points: { label: "Points", percent: false },
  rebounds: { label: "Rebounds", percent: false },
  assists: { label: "Assists", percent: false },
  steals: { label: "Steals", percent: false },
  blocks: { label: "Blocks", percent: false },
  field_goals_made: { label: "Field goals made", percent: false },
  field_goals_attempted: { label: "Field goals attempted", percent: false },
  field_goal_pct: { label: "Field goal %", percent: true },
  three_pointers_made: { label: "Three-pointers made", percent: false },
  three_point_pct: { label: "Three-point %", percent: true },
  free_throw_pct: { label: "Free throw %", percent: true },
  plus_minus: { label: "Plus / minus", percent: false },
  true_shooting_pct: { label: "True shooting %", percent: true },
  usage_pct: { label: "Usage %", percent: true },
  offensive_rating: { label: "Offensive rating", percent: false },
  defensive_rating: { label: "Defensive rating", percent: false },
} as const;

type Metric = keyof typeof metrics;
type ChartType = "line" | "bar";

export function StatsChart({
  playerId,
  view,
  season,
}: {
  playerId: number;
  view: StatsView;
  season: string;
}) {
  return view === "career" ? (
    <CareerStatsChart playerId={playerId} />
  ) : (
    <GameStatsChart playerId={playerId} season={season} />
  );
}

function CareerStatsChart({ playerId }: { playerId: number }) {
  const trpc = useTRPC();
  const seasonOptions = trpc.player.seasonStats.queryOptions({
    playerId,
  }) as unknown as UseSuspenseQueryOptions<PlayerSeasonStatRow[]>;
  const rows = useSuspenseQuery(seasonOptions).data;

  return <StatsChartCard rows={rows} view="career" season="" />;
}

function GameStatsChart({
  playerId,
  season,
}: {
  playerId: number;
  season: string;
}) {
  const trpc = useTRPC();
  const gameOptions = trpc.player.gameStats.queryOptions({
    playerId,
    seasonId: season,
  }) as unknown as UseSuspenseQueryOptions<PlayerGameStatRow[]>;
  const rows = useSuspenseQuery(gameOptions).data;

  return <StatsChartCard rows={rows} view="games" season={season} />;
}

function StatsChartCard({
  rows,
  view,
  season,
}: {
  rows: PlayerSeasonStatRow[] | PlayerGameStatRow[];
  view: StatsView;
  season: string;
}) {
  const [metric, setMetric] = useState<Metric>("points");
  const [chartType, setChartType] = useState<ChartType>("line");
  const metricConfig = metrics[metric];
  const data =
    view === "career"
      ? (rows as PlayerSeasonStatRow[]).map((row) => ({
          label: row.season_id,
          value:
            row[metric] == null
              ? null
              : metricConfig.percent
                ? row[metric] * 100
                : row[metric],
        }))
      : [...(rows as PlayerGameStatRow[])].reverse().map((row) => ({
          label: row.game_date?.slice(5) ?? "Game",
          value:
            row[metric] == null
              ? null
              : metricConfig.percent
                ? row[metric] * 100
                : row[metric],
        }));
  const hasData = data.some((item) => item.value != null);

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {view === "career" ? "Career trend" : `${season} game trend`}
        </CardTitle>
        <CardDescription>Explore performance over time.</CardDescription>
        <CardAction className="flex flex-wrap justify-end gap-2">
          <div className="flex rounded-lg border bg-muted/30 p-0.5">
            <Button
              size="icon-sm"
              variant={chartType === "line" ? "secondary" : "ghost"}
              aria-label="Line chart"
              onClick={() => setChartType("line")}
            >
              <LineChartIcon />
            </Button>
            <Button
              size="icon-sm"
              variant={chartType === "bar" ? "secondary" : "ghost"}
              aria-label="Bar chart"
              onClick={() => setChartType("bar")}
            >
              <BarChart3 />
            </Button>
          </div>
          <Select
            value={metric}
            onValueChange={(value) => setMetric(value as Metric)}
          >
            <SelectTrigger aria-label="Chart metric" className="w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(metrics).map(([key, item]) => (
                <SelectItem key={key} value={key}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent>
        {!hasData ? (
          <div className="flex h-72 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
            No chart data is available for this metric.
          </div>
        ) : (
          <ChartContainer
            config={{
              value: {
                label: metricConfig.label,
                color: "var(--color-primary)",
              },
            }}
            className="h-72 w-full aspect-auto"
          >
            {chartType === "line" ? (
              <LineChart data={data} margin={{ left: 0, right: 12 }}>
                <CartesianGrid vertical={false} />
                <XAxis
                  dataKey="label"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis tickLine={false} axisLine={false} width={36} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line
                  dataKey="value"
                  type="monotone"
                  stroke="var(--color-value)"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                  connectNulls={false}
                />
              </LineChart>
            ) : (
              <BarChart data={data} margin={{ left: 0, right: 12 }}>
                <CartesianGrid vertical={false} />
                <XAxis
                  dataKey="label"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis tickLine={false} axisLine={false} width={36} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar
                  dataKey="value"
                  fill="var(--color-value)"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            )}
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  );
}
