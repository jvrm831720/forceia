import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
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
    <section className="border border-border bg-canvas">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <h2 className="text-[13px] font-medium text-ink">Agenda</h2>
        <span className="font-mono text-[11px] text-ink-soft">{items.length} hoje</span>
      </div>
      {items.length === 0 ? (
        <p className="px-3 py-8 text-center text-[12px] text-ink-soft">
          Nenhuma reunião agendada
        </p>
      ) : (
        <ul className="divide-y divide-border">
          {items.map((item) => (
            <li
              key={item.id}
              className="flex items-stretch gap-0 transition-ui hover:bg-surface"
            >
              <div className="flex w-14 shrink-0 flex-col items-center justify-center border-r border-border bg-background/50 py-2.5">
                <span className="font-mono text-[12px] font-medium tabular-nums text-ink">
                  {item.time}
                </span>
              </div>
              <div className="flex min-w-0 flex-1 items-center justify-between gap-3 px-3 py-2.5">
                <div className="min-w-0">
                  <p className="truncate text-[13px] font-medium text-ink">
                    {item.company}
                  </p>
                  <p className="truncate text-[11px] text-ink-soft">
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
    </section>
  );
}
