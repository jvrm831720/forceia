import type { ActivityItem, ActivityKind } from "@/types/dashboard";
import { ArrowRightLeft, Calendar, MessageCircle, RefreshCw, TrendingUp, UserCheck } from "lucide-react";

const KIND: Record<ActivityKind, { icon: typeof UserCheck; color: string }> = {
  qualified: { icon: UserCheck, color: "text-success" },
  meeting: { icon: Calendar, color: "text-brand" },
  followup: { icon: RefreshCw, color: "text-ai" },
  handoff: { icon: ArrowRightLeft, color: "text-warning" },
  reply: { icon: MessageCircle, color: "text-ink-muted" },
  pipeline: { icon: TrendingUp, color: "text-success" },
};

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <section className="rounded-lg border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="font-display text-sm font-semibold tracking-tight text-ink">Atividade ao vivo</h2>
        <span className="text-label">Tempo real</span>
      </div>
      <ul className="divide-y divide-border">
        {items.map((item) => {
          const meta = KIND[item.kind] ?? KIND.reply;
          const Icon = meta.icon;
          return (
            <li key={item.id} className="flex gap-3 px-4 py-3 transition-ui hover:bg-surface-hover">
              <div className={`mt-0.5 shrink-0 ${meta.color}`}><Icon className="h-4 w-4" strokeWidth={1.75} /></div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-ink">{item.title}</p>
                {item.description && <p className="mt-0.5 text-xs text-ink-muted line-clamp-2">{item.description}</p>}
              </div>
              <time className="shrink-0 text-[11px] tabular-nums text-ink-soft">{item.time}</time>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
