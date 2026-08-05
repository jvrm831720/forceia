import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgendaItem } from "@/types/dashboard";

function statusVariant(
  status: AgendaItem["status"]
): "success" | "highlight" | "muted" {
  if (status === "confirmed") return "success";
  if (status === "pending") return "highlight";
  return "muted";
}

function statusLabel(status: AgendaItem["status"]) {
  if (status === "confirmed") return "Confirmada";
  if (status === "pending") return "Pendente";
  return "Concluída";
}

export function AgendaToday({ items }: { items: AgendaItem[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Agenda de hoje</CardTitle>
          <p className="mt-1 text-sm text-ink-muted">
            Próximas reuniões da operação comercial.
          </p>
        </div>
        <Badge variant="default">{items.length} reuniões</Badge>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] border-collapse text-left">
            <thead>
              <tr className="border-b border-border text-[11px] font-semibold uppercase tracking-wider text-ink-soft">
                <th className="pb-3 pr-4 font-semibold">Horário</th>
                <th className="pb-3 pr-4 font-semibold">Empresa</th>
                <th className="pb-3 pr-4 font-semibold">Responsável</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr
                  key={item.id}
                  className="border-b border-border-soft last:border-0"
                >
                  <td className="py-3.5 pr-4">
                    <span className="font-mono text-sm font-semibold text-ink">
                      {item.time}
                    </span>
                  </td>
                  <td className="py-3.5 pr-4">
                    <p className="text-sm font-semibold text-ink">
                      {item.company}
                    </p>
                    {item.contact && (
                      <p className="text-[12px] text-ink-muted">{item.contact}</p>
                    )}
                  </td>
                  <td className="py-3.5 pr-4 text-sm text-ink-muted">
                    {item.owner}
                  </td>
                  <td className="py-3.5">
                    <Badge variant={statusVariant(item.status)}>
                      {statusLabel(item.status)}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
