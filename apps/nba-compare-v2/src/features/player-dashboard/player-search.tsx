"use client";

import { useQuery, type UseQueryOptions } from "@tanstack/react-query";
import { Command } from "cmdk";
import { Check, Search, X } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTRPC } from "@/trpc/client";
import type { PlayerSearchItem } from "@/server/player/types";

import { dashboardUrl } from "./dashboard-state";

export function PlayerSearch({
  selectedPlayerId,
}: {
  selectedPlayerId: number | null;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const trpc = useTRPC();
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedQuery(query.trim()), 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  const searchOptions = trpc.player.search.queryOptions({
    query: debouncedQuery,
    limit: 10,
  }) as unknown as UseQueryOptions<PlayerSearchItem[]>;
  const results = useQuery({
    ...searchOptions,
    enabled: debouncedQuery.length >= 2,
  });

  const selectPlayer = (playerId: number) => {
    router.push(
      dashboardUrl(searchParams, { playerId, view: "career", season: null }),
    );
    setOpen(false);
    setQuery("");
  };

  return (
    <div className="relative">
      <Command shouldFilter={false} className="overflow-visible bg-transparent">
        <div className="flex h-11 items-center gap-2 rounded-xl border bg-background px-3 shadow-sm transition-shadow focus-within:ring-3 focus-within:ring-ring/30">
          <Search className="size-4 text-muted-foreground" aria-hidden="true" />
          <Command.Input
            value={query}
            onValueChange={(value) => {
              setQuery(value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            placeholder="Search players by name..."
            aria-label="Search NBA players"
            className="h-full min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          {(query || selectedPlayerId) && (
            <Button
              type="button"
              size="icon-sm"
              variant="ghost"
              aria-label="Clear player selection"
              onClick={() => {
                setQuery("");
                router.push(dashboardUrl(searchParams, { playerId: null }));
              }}
            >
              <X className="size-4" />
            </Button>
          )}
        </div>

        {open && query.trim().length >= 2 && (
          <Command.List className="absolute z-40 mt-2 max-h-80 w-full overflow-y-auto rounded-xl border bg-popover p-1 text-popover-foreground shadow-xl">
            {results.isFetching && (
              <div className="px-3 py-6 text-center text-sm text-muted-foreground">
                Searching players…
              </div>
            )}
            {!results.isFetching && results.data?.length === 0 && (
              <Command.Empty className="px-3 py-6 text-center text-sm text-muted-foreground">
                No players found.
              </Command.Empty>
            )}
            {results.data?.map((player) => (
              <Command.Item
                key={player.player_id}
                value={String(player.player_id)}
                onSelect={() => selectPlayer(player.player_id)}
                className={cn(
                  "flex cursor-pointer items-center justify-between rounded-lg px-3 py-2.5 text-sm outline-none",
                  "data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground",
                )}
              >
                <span>
                  <span className="block font-medium">{player.full_name}</span>
                  <span className="text-xs text-muted-foreground">
                    {player.current_team_abbreviation ?? "Free agent"}
                  </span>
                </span>
                {player.player_id === selectedPlayerId && (
                  <Check className="size-4" />
                )}
              </Command.Item>
            ))}
          </Command.List>
        )}
      </Command>
      <p className="mt-2 text-xs text-muted-foreground">
        Enter at least two characters. Up to ten matches are shown.
      </p>
    </div>
  );
}
