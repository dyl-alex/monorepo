export function formatNumber(value: number | null, digits = 1) {
  return value == null ? "—" : value.toFixed(digits);
}

export function formatInteger(value: number | null) {
  return value == null ? "—" : Math.round(value).toString();
}

export function formatPercent(value: number | null) {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

export function formatDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(`${value}T12:00:00Z`));
}
