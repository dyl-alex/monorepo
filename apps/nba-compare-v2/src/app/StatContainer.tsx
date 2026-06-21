export default function StatContainer({
  profile,
  stats,
}: {
  profile: React.ReactNode;
  stats: React.ReactNode;
}) {
  return (
    <section
      aria-label="Player statistics"
      className="grid gap-5 lg:grid-cols-3"
    >
      <div className="lg:col-span-1">{profile}</div>
      <div className="min-w-0 lg:col-span-2">{stats}</div>
    </section>
  );
}
