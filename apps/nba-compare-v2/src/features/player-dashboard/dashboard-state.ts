export type StatsView = "career" | "games";

export function dashboardUrl(
  current: URLSearchParams,
  updates: {
    playerId?: number | null;
    view?: StatsView;
    season?: string | null;
  },
) {
  const params = new URLSearchParams(current);
  if (updates.playerId === null) params.delete("playerId");
  else if (updates.playerId !== undefined)
    params.set("playerId", String(updates.playerId));

  if (updates.view) params.set("view", updates.view);
  if (updates.season === null) params.delete("season");
  else if (updates.season !== undefined) params.set("season", updates.season);

  if (updates.playerId === null) {
    params.delete("view");
    params.delete("season");
  }
  const query = params.toString();
  return query ? `/?${query}` : "/";
}
