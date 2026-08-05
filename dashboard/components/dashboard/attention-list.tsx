import { Badge } from "@/components/ui/badge";
import type { AttentionItem, Priority } from "@/types/dashboard";
import Link from "next/link";

const PRIORITY: Record<Priority, "danger" | "warning" | "muted"> = {
  high: "danger",
  medium: "warning",
  low: "muted",
};

export function AttentionList({ items }: { items: AttentionItem[] }) {
  return (
    <section className="flex h-full flex-col border border-border bg-canvas">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <h2 className="text-[13px] font-medium text-ink">Handoffs</h2>
        <span className="font-mono text-[11px] text-warning">{items.length}</span>
      </div>
      <ul className="min-h-0 flex-1 divide-y divide-border overflow-auto">
        {items.length === 0 ? (
          <li className="px-3 py-8 text-center text-[12px] text-ink-soft">
            Nenhum handoff pendente
          </li>
        ) : (
          items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/conversas?c=${item.conversationId}`}
                className="flex items-start gap-2 px-3 py-2 transition-ui hover:bg-surface"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <p className="truncate text-[13px] font-medium text-ink">
                      {item.name}
                    </p>
                    <Badge variant={PRIORITY[item.priority]}>{item.priority}</Badge>
                  </div>
                  <p className="truncate text-[11px] text-ink-soft">{item.company}</p>
                  <p className="mt-0.5 text-[11px] text-ink-muted">{item.reason}</p>
                </div>
              </Link>
            </li>
          ))
        )}
      </ul>
    </section>
  );
}
