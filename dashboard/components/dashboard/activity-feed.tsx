import { Panel, PanelHeader, PanelBody } from "@/components/ui/panel";
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

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <Panel className="h-full">
      <PanelHeader title="Timeline operacional" meta={<span className="text-label !normal-case tracking-normal">Live</span>} />
      <PanelBody>
        <ul className="divide-y divide-border">
          {items.map((item) => (
            <li key={item.id}>
              <div className="flex items-start gap-2.5 px-3 py-2 transition-ui duration-fast hover:bg-surface">
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
                <time className="shrink-0 text-mono text-ink-soft">{item.time}</time>
              </div>
            </li>
          ))}
        </ul>
      </PanelBody>
    </Panel>
  );
}
