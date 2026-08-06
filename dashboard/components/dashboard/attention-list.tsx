import { Badge } from "@/components/ui/badge";
import { Panel, PanelHeader, PanelBody } from "@/components/ui/panel";
import type { AttentionItem, Priority } from "@/types/dashboard";
import Link from "next/link";

const PRIORITY: Record<Priority, "danger" | "warning" | "muted"> = {
  high: "danger",
  medium: "warning",
  low: "muted",
};

export function AttentionList({ items }: { items: AttentionItem[] }) {
  return (
    <Panel className="h-full">
      <PanelHeader
        title="Handoffs"
        meta={<span className="text-mono text-warning">{items.length}</span>}
      />
      <PanelBody>
        <ul className="divide-y divide-border">
          {items.length === 0 ? (
            <li className="px-3 py-8 text-center text-body-muted text-ink-soft">
              Nenhum handoff pendente
            </li>
          ) : (
            items.map((item) => (
              <li key={item.id}>
                <Link
                  href={`/conversas?c=${item.conversationId}`}
                  className="flex items-start gap-2 px-3 py-2 transition-ui duration-fast hover:bg-surface focus-visible:bg-surface"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <p className="truncate text-body font-medium text-ink">
                        {item.name}
                      </p>
                      <Badge variant={PRIORITY[item.priority]}>{item.priority}</Badge>
                    </div>
                    <p className="truncate text-meta text-ink-soft">{item.company}</p>
                    <p className="mt-0.5 text-meta text-ink-muted">{item.reason}</p>
                  </div>
                </Link>
              </li>
            ))
          )}
        </ul>
      </PanelBody>
    </Panel>
  );
}
