import { Badge } from "@/components/ui/badge";
import type { AttentionItem, Priority } from "@/types/dashboard";
import Link from "next/link";

const PRIORITY: Record<Priority, "danger" | "warning" | "muted"> = { high: "danger", medium: "warning", low: "muted" };

export function AttentionList({ items }: { items: AttentionItem[] }) {
  return (
    <section className="rounded-lg border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="font-display text-sm font-semibold tracking-tight text-ink">Precisa da sua atenção</h2>
        <span className="text-label">{items.length}</span>
      </div>
      <ul className="divide-y divide-border">
        {items.map((item) => (
          <li key={item.id}>
            <Link href={`/conversas?c=${item.conversationId}`} className="flex items-start gap-3 px-4 py-3 transition-ui hover:bg-surface-hover">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-medium text-ink">{item.name}</p>
                  <Badge variant={PRIORITY[item.priority]}>{item.priority}</Badge>
                </div>
                <p className="truncate text-xs text-ink-soft">{item.company}</p>
                <p className="mt-1 text-xs text-ink-muted">{item.reason}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
