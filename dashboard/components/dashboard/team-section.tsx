import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AgentCard } from "@/types/dashboard";
import { Bot, Handshake, RefreshCw } from "lucide-react";

const ROLE_ICON = {
  sdr: Bot,
  closer: Handshake,
  followup: RefreshCw,
} as const;

function statusLabel(status: AgentCard["status"]) {
  if (status === "working") return "Trabalhando";
  if (status === "paused") return "Pausado";
  return "Offline";
}

export function TeamSection({ agents }: { agents: AgentCard[] }) {
  return (
    <section>
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold tracking-tight text-ink">
            Sua Equipe IA
          </h2>
          <p className="mt-1 text-sm text-ink-muted">
            Especialistas digitais operando a jornada comercial por você.
          </p>
        </div>
        <Badge variant="ai">3 agentes ativos</Badge>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {agents.map((agent) => {
          const Icon =
            ROLE_ICON[agent.id as keyof typeof ROLE_ICON] ?? Bot;
          const working = agent.status === "working";

          return (
            <Card key={agent.id} className="overflow-hidden">
              <div className="h-1 w-full bg-gradient-to-r from-ai/80 via-brand/50 to-transparent" />
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-ai-soft text-ai">
                    <Icon className="h-5 w-5" strokeWidth={1.75} />
                  </div>
                  <div>
                    <CardTitle className="text-base">{agent.name}</CardTitle>
                    <p className="text-xs text-ink-soft">{agent.role}</p>
                  </div>
                </div>
                <Badge variant={working ? "success" : "muted"}>
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full",
                      working ? "bg-success" : "bg-ink-soft"
                    )}
                  />
                  {statusLabel(agent.status)}
                </Badge>
              </CardHeader>
              <CardContent>
                <p className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink-soft">
                  Hoje
                </p>
                <ul className="space-y-2">
                  {agent.stats.map((s) => (
                    <li
                      key={s.label}
                      className="flex items-center justify-between rounded-xl bg-surface px-3 py-2.5"
                    >
                      <span className="text-sm text-ink-muted">{s.label}</span>
                      <span className="font-display text-lg font-semibold text-ink">
                        {s.value}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
