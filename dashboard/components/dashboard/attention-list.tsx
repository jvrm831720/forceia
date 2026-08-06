import { Badge } from "@/components/ui/badge";
import type { AttentionItem, Priority } from "@/types/dashboard";
import Link from "next/link";

const PRIORITY: Record<Priority, "danger" | "warning" | "muted"> = {
  high: "danger",
  medium: "warning",
  low: "muted",
};

/**
 * Human interrupt lane — what the AI cannot finish alone.
 */
export function AttentionList({ items }: { items: AttentionItem[] }) {
  const hasItems = items.length > 0;

  return (
    <section
      className={`border bg-canvas ${
        hasItems ? "border-warning/40" : "border-border"
      }`}
    >
      <div className="flex h-9 items-center justify-between border-b border-border px-3">
        <div className="flex items-center gap-2">
          {hasItems && (
            <span className="h-1.5 w-1.5 rounded-full bg-warning" aria-hidden />
          )}
          <h2 className="text-section text-ink">Precisa de você</h2>
        </div>
        <span
          className={`text-mono ${hasItems ? "text-warning" : "text-ink-soft"}`}
        >
          {items.length}
        </span>
      </div>

      <ul className="divide-y divide-border">
        {!hasItems ? (
          <li className="px-3 py-6 text-center text-body-muted text-ink-soft">
            Nenhum handoff. A equipe de IA está cobrindo o fluxo.
          </li>
        ) : (
          items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/conversas?c=${item.conversationId}`}
                className="flex items-start gap-3 px-3 py-2.5 transition-ui duration-fast hover:bg-surface focus-visible:bg-surface"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <p className="truncate text-body font-medium text-ink">
                      {item.name}
                    </p>
                    <Badge variant={PRIORITY[item.priority]}>
                      {item.priority}
                    </Badge>
                  </div>
                  <p className="truncate text-meta text-ink-soft">
                    {item.company}
                  </p>
                  <p className="mt-0.5 text-meta text-ink-muted">{item.reason}</p>
                </div>
                <span className="shrink-0 text-mono text-brand">abrir →</span>
              </Link>
            </li>
          ))
        )}
      </ul>
    </section>
  );
}
