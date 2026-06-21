"use client";

import {
  useSuspenseQuery,
  type UseSuspenseQueryOptions,
} from "@tanstack/react-query";
import { Award, MapPin } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useTRPC } from "@/trpc/client";
import type { PlayerProfile } from "@/server/player/types";

export function PlayerProfileCard({ playerId }: { playerId: number }) {
  const trpc = useTRPC();
  const options = trpc.player.profile.queryOptions({
    playerId,
  }) as unknown as UseSuspenseQueryOptions<PlayerProfile>;
  const { data } = useSuspenseQuery(options);
  const [imageFailed, setImageFailed] = useState(false);
  const { player, profile } = data;

  const bio = [
    ["Position", profile?.position],
    ["Height", profile?.height],
    ["Weight", profile?.weight_lbs ? `${profile.weight_lbs} lbs` : null],
    ["Age", profile?.age],
    ["Country", profile?.country],
    ["School", profile?.school],
  ];

  return (
    <Card className="h-full">
      <div className="relative mx-4 aspect-[4/3] overflow-hidden rounded-xl bg-muted">
        <Image
          src={
            imageFailed
              ? "/mock/player-placeholder.svg"
              : (player.headshot_url ?? "/mock/player-placeholder.svg")
          }
          alt={`${player.full_name} headshot`}
          fill
          sizes="(min-width: 1024px) 30vw, 100vw"
          className="object-cover"
          onError={() => setImageFailed(true)}
          priority
        />
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-4 pt-12 text-white">
          <div className="flex items-end justify-between gap-3">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-white/70">
                {player.current_team_abbreviation ?? "NBA"}
              </p>
              <h2 className="text-2xl font-semibold tracking-tight">
                {player.full_name}
              </h2>
            </div>
            {profile?.jersey && (
              <Badge className="bg-white text-black">#{profile.jersey}</Badge>
            )}
          </div>
        </div>
      </div>
      <CardHeader>
        <CardTitle>Player bio</CardTitle>
        <CardDescription className="flex items-center gap-1.5">
          <MapPin className="size-3.5" />
          {player.current_team_name ?? "No current team"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
          {bio.map(([label, value]) => (
            <div key={String(label)}>
              <dt className="text-xs text-muted-foreground">{label}</dt>
              <dd className="mt-0.5 font-medium">{value ?? "—"}</dd>
            </div>
          ))}
        </dl>
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-muted/60 p-3 text-xs text-muted-foreground">
          <Award className="mt-0.5 size-4 shrink-0" />
          <span>
            Drafted {profile?.draft_year ?? "—"}, round{" "}
            {profile?.draft_round ?? "—"}, pick {profile?.draft_number ?? "—"}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
