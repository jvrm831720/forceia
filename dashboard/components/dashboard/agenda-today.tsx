import { Badge } from "@/components/ui/badge";
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
        <span className="font-mono text-[11px] text-ink-soft">{items.length}</span>
      </div>
      {items.length === 0 ? (
        <p className="px-3 py-6 text-center text-xs text-ink-soft">Sem reuniões</p>
      ) : (
        <table className="w-full text-left text-[13px]">
          <thead>
            <tr className="border-b border-border text-label">
              <th className="px-3 py-1.5 font-medium">Hora</th>
              <th className="px-3 py-1.5 font-medium">Empresa</th>
              <th className="hidden px-3 py-1.5 font-medium sm:table-cell">Contato</th>
              <th className="hidden px-3 py-1.5 font-medium md:table-cell">Owner</th>
              <th className="px-3 py-1.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {items.map((item) => (
              <tr key={item.id} className="transition-ui hover:bg-surface">
                <td className="px-3 py-2 font-mono text-xs tabular-nums text-ink">{item.time}</td>
                <td className="px-3 py-2 font-medium text-ink">{item.company}</td>
                <td className="hidden px-3 py-2 text-ink-muted sm:table-cell">
                  {item.contact ?? "—"}
                </td>
                <td className="hidden px-3 py-2 text-ink-muted md:table-cell">{item.owner}</td>
                <td className="px-3 py-2">
                  <Badge variant={STATUS_VARIANT[item.status]}>
                    {STATUS_LABEL[item.status]}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
