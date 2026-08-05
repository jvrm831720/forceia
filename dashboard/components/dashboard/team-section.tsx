import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AgentCard, AgentStatus } from "@/types/dashboard";

const STATUS: Record<
  AgentStatus,
  { label: string; variant: "success" | "muted" | "warning"; dot: string }
> = {
  working: { label: "Ativo", variant: "success", dot: "bg-success" },
  paused: { label: "Pausado", variant: "warning", dot: "bg-warning" },
  offline: { label: "Offline", variant: "muted", dot: "bg-ink-soft" },
};

export function TeamSection({ agents }: { agents: AgentCard[] }) {
  return (
    <section className="border border-border bg-canvas">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <h2 className="text-[13px] font-medium text-ink">Agentes</h2>
        <span className="text-[11px] text-ink-soft">{agents.length} online</span>
      </div>
      <div className="divide-y divide-border">
        {agents.map((agent) => {
          const st = STATUS[agent.status];
          return (
            <div
              key={agent.id}
              className="grid grid-cols-12 items-center gap-2 px-3 py-2 transition-ui hover:bg-surface"
            >
              <div className="col-span-5 min-w-0 sm:col-span-4">
                <p className="truncate text-[13px] font-medium text-ink">{agent.name}</p>
                <p className="truncate text-[11px] text-ink-soft">{agent.role}</p>
              </div>
              <div className="col-span-3 sm:col-span-2">
                <Badge variant={st.variant}>
                  <span className={cn("h-1 w-1 rounded-full", st.dot)} />
                  {st.label}
                </Badge>
              </div>
              <div className="col-span-4 flex gap-4 sm:col-span-6">
                {agent.stats.map((s) => (
                  <div key={s.label} className="min-w-0">
                    <p className="text-[10px] uppercase tracking-wide text-ink-soft">{s.label}</p>
                    <p className="font-mono text-[13px] font-medium tabular-nums text-ink">
                      {s.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
