import type { ActivityItem, ActivityKind } from "@/types/dashboard";

const KIND_LABEL: Record<ActivityKind, string> = {
  qualified: "QUAL",
  meeting: "MTG",
  followup: "FUP",
  handoff: "HO",
  reply: "MSG",
  pipeline: "PIPE",
};

const KIND_COLOR: Record<ActivityKind, string> = {
  qualified: "text-success",
  meeting: "text-brand",
  followup: "text-ai",
  handoff: "text-warning",
  reply: "text-ink-muted",
  pipeline: "text-success",
};

/**
 * Ops log — chronological proof of AI work.
 */
export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <section className="flex h-full flex-col border border-border bg-canvas">
      <div className="flex h-9 items-center justify-between border-b border-border px-3">
        <h2 className="text-section text-ink">O que a IA fez</h2>
        <span className="text-label">Live</span>
      </div>
      <ul className="min-h-0 flex-1 divide-y divide-border overflow-auto">
        {items.map((item) => (
          <li key={item.id}>
            <div className="flex items-start gap-2.5 px-3 py-2 transition-ui duration-fast hover:bg-surface">
              <time className="mt-0.5 w-10 shrink-0 text-mono text-ink-soft">
                {item.time}
              </time>
              <span
                className={`mt-0.5 w-9 shrink-0 text-mono font-medium ${KIND_COLOR[item.kind] ?? "text-ink-muted"}`}
              >
                {KIND_LABEL[item.kind] ?? "EVT"}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-body text-ink">{item.title}</p>
                {item.description && (
                  <p className="mt-0.5 line-clamp-1 text-meta text-ink-soft">
                    {item.description}
                  </p>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
