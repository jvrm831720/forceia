import { Badge } from "@/components/ui/badge";
import { Panel, PanelHeader, PanelBody } from "@/components/ui/panel";
import type { AgendaItem } from "@/types/dashboard";

const STATUS_VARIANT = {
  confirmed: "success" as const,
  pending: "warning" as const,
  completed: "muted" as const,
};
const STATUS_LABEL = {
  confirmed: "OK",
  pending: "PEND",
  completed: "DONE",
};

export function AgendaToday({ items }: { items: AgendaItem[] }) {
  return (
    <Panel>
      <PanelHeader
        title="Agenda"
        meta={<span className="text-mono">{items.length} hoje</span>}
      />
      <PanelBody>
        {items.length === 0 ? (
          <p className="px-3 py-8 text-center text-body-muted text-ink-soft">
            Nenhuma reunião agendada
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((item) => (
              <li
                key={item.id}
                className="flex items-stretch transition-ui duration-fast hover:bg-surface"
              >
                <div className="flex w-14 shrink-0 flex-col items-center justify-center border-r border-border bg-background/40 py-2">
                  <span className="text-mono font-medium text-ink">{item.time}</span>
                </div>
                <div className="flex min-w-0 flex-1 items-center justify-between gap-3 px-3 py-2">
                  <div className="min-w-0">
                    <p className="truncate text-body font-medium text-ink">
                      {item.company}
                    </p>
                    <p className="truncate text-meta text-ink-soft">
                      {[item.contact, item.owner].filter(Boolean).join(" · ")}
                    </p>
                  </div>
                  <Badge variant={STATUS_VARIANT[item.status]}>
                    {STATUS_LABEL[item.status]}
                  </Badge>
                </div>
              </li>
            ))}
          </ul>
        )}
      </PanelBody>
    </Panel>
  );
}
