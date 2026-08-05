import { Badge } from "@/components/ui/badge";
import type { AgendaItem } from "@/types/dashboard";

const STATUS_VARIANT = { confirmed: "success" as const, pending: "warning" as const, completed: "muted" as const };
const STATUS_LABEL = { confirmed: "Confirmada", pending: "Pendente", completed: "Concluída" };

export function AgendaToday({ items }: { items: AgendaItem[] }) {
  return (
    <section className="rounded-lg border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="font-display text-sm font-semibold tracking-tight text-ink">Agenda de hoje</h2>
        <span className="text-label">{items.length} reuniões</span>
      </div>
      {items.length === 0 ? (
        <p className="px-4 py-8 text-center text-sm text-ink-soft">Nenhuma reunião agendada</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-label">
                <th className="px-4 py-2 font-medium">Horário</th>
                <th className="px-4 py-2 font-medium">Empresa</th>
                <th className="hidden px-4 py-2 font-medium sm:table-cell">Contato</th>
                <th className="hidden px-4 py-2 font-medium md:table-cell">Responsável</th>
                <th className="px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {items.map((item) => (
                <tr key={item.id} className="transition-ui hover:bg-surface-hover">
                  <td className="px-4 py-3 font-mono text-xs tabular-nums text-ink">{item.time}</td>
                  <td className="px-4 py-3 font-medium text-ink">{item.company}</td>
                  <td className="hidden px-4 py-3 text-ink-muted sm:table-cell">{item.contact ?? "—"}</td>
                  <td className="hidden px-4 py-3 text-ink-muted md:table-cell">{item.owner}</td>
                  <td className="px-4 py-3"><Badge variant={STATUS_VARIANT[item.status]}>{STATUS_LABEL[item.status]}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
