import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AttentionItem, Priority } from "@/types/dashboard";
import { ArrowUpRight } from "lucide-react";
import Link from "next/link";

function priorityVariant(p: Priority): "alert" | "highlight" | "muted" {
  if (p === "high") return "alert";
  if (p === "medium") return "highlight";
  return "muted";
}

function priorityLabel(p: Priority) {
  if (p === "high") return "Alta";
  if (p === "medium") return "Média";
  return "Baixa";
}

export function AttentionList({ items }: { items: AttentionItem[] }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div>
          <CardTitle>Conversas que precisam da sua atenção</CardTitle>
          <p className="mt-1 text-sm text-ink-muted">
            Apenas onde a IA pediu intervenção humana.
          </p>
        </div>
        {items.length > 0 && (
          <Badge variant="alert">{items.length} pendentes</Badge>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border bg-surface px-4 py-8 text-center">
            <p className="text-sm font-medium text-ink">Tudo sob controle</p>
            <p className="mt-1 text-sm text-ink-muted">
              Nenhuma conversa aguardando você no momento.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 transition hover:border-border hover:shadow-card sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold text-ink">{item.name}</p>
                  <Badge variant={priorityVariant(item.priority)}>
                    {priorityLabel(item.priority)}
                  </Badge>
                </div>
                <p className="mt-0.5 text-[13px] text-ink-muted">{item.company}</p>
                <p className="mt-2 text-sm text-ink">{item.reason}</p>
              </div>
              <Button asChild variant="secondary" size="sm" className="shrink-0">
                <Link href={`/conversas/${item.conversationId}`}>
                  Abrir conversa
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </Link>
              </Button>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
