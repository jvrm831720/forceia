import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AgentCard, AgentStatus } from "@/types/dashboard";

const STATUS: Record<AgentStatus, { label: string; variant: "success" | "muted" | "warning"; dot: string }> = {
  working: { label: "Trabalhando", variant: "success", dot: "bg-success" },
  paused: { label: "Pausado", variant: "warning", dot: "bg-warning" },
  offline: { label: "Offline", variant: "muted", dot: "bg-ink-soft" },
};

export function TeamSection({ agents }: { agents: AgentCard[] }) {
  return (
    <section>
      <div className="mb-3 flex items-baseline justify-between">
        <h2 className="font-display text-sm font-semibold tracking-tight text-ink">Equipe de IA</h2>
        <p className="text-xs text-ink-soft">{agents.length} agentes</p>
      </div>
      <div className="overflow-hidden rounded-lg border border-border">
        <div className="grid grid-cols-12 gap-4 border-b border-border bg-surface-hover/50 px-4 py-2 text-label">
          <div className="col-span-4">Agente</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-6 hidden sm:block">Métricas</div>
        </div>
        <div className="divide-y divide-border">
          {agents.map((agent) => {
            const st = STATUS[agent.status];
            return (
              <div key={agent.id} className="grid grid-cols-12 items-center gap-4 px-4 py-3 transition-ui hover:bg-surface-hover">
                <div className="col-span-4 min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{agent.name}</p>
                  <p className="truncate text-xs text-ink-soft">{agent.role}</p>
                </div>
                <div className="col-span-2">
                  <Badge variant={st.variant}><span className={cn("h-1.5 w-1.5 rounded-full", st.dot)} />{st.label}</Badge>
                </div>
                <div className="col-span-6 hidden gap-4 sm:flex">
                  {agent.stats.map((s) => (
                    <div key={s.label} className="min-w-0">
                      <p className="text-[11px] text-ink-soft">{s.label}</p>
                      <p className="text-sm font-semibold tabular-nums text-ink">{s.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
