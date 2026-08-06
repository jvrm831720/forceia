import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AgentCard, AgentStatus } from "@/types/dashboard";

const STATUS: Record<
  AgentStatus,
  { label: string; variant: "success" | "muted" | "warning"; tone: string }
> = {
  working: {
    label: "Em operação",
    variant: "success",
    tone: "border-l-brand",
  },
  paused: {
    label: "Pausado",
    variant: "warning",
    tone: "border-l-warning",
  },
  offline: {
    label: "Offline",
    variant: "muted",
    tone: "border-l-border",
  },
};

/**
 * Agent Stage — visual signature of ForceIA.
 * Three AI services as the primary product surface.
 */
export function AgentStage({ agents }: { agents: AgentCard[] }) {
  const active = agents.filter((a) => a.status === "working").length;

  return (
    <section className="border border-border bg-canvas">
      <div className="flex h-9 items-center justify-between border-b border-border px-3">
        <div className="flex items-center gap-2">
          <h2 className="text-section text-ink">Equipe de IA</h2>
          <span className="text-meta text-ink-soft">trabalhando agora</span>
        </div>
        <span className="text-mono text-brand">
          {active}/{agents.length} ativos
        </span>
      </div>

      <div className="grid gap-0 lg:grid-cols-3">
        {agents.map((agent, i) => {
          const st = STATUS[agent.status];
          const isLive = agent.status === "working";

          return (
            <article
              key={agent.id}
              className={cn(
                "relative border-l-2 bg-canvas px-4 py-4 transition-ui duration-fast hover:bg-surface",
                st.tone,
                i > 0 && "border-t border-border lg:border-t-0 lg:border-l-0",
                i > 0 && "lg:border-l-2",
              )}
            >
              <div className="mb-3 flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    {isLive && (
                      <span className="relative flex h-1.5 w-1.5 shrink-0">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-50" />
                        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
                      </span>
                    )}
                    <h3 className="truncate text-body font-medium text-ink">
                      {agent.name}
                    </h3>
                  </div>
                  <p className="mt-0.5 text-meta text-ink-soft">{agent.role}</p>
                </div>
                <Badge variant={st.variant}>{st.label}</Badge>
              </div>

              <div className="mb-3 grid grid-cols-2 gap-3">
                {agent.stats.map((s) => (
                  <div key={s.label}>
                    <p className="text-label">{s.label}</p>
                    <p className="mt-0.5 text-metric-sm text-ink">{s.value}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-mono text-ink-soft">
                    {isLive ? "processando" : "ocioso"}
                  </span>
                  <span className="text-mono text-ink-soft">
                    {isLive ? "live" : "—"}
                  </span>
                </div>
                <div className="h-0.5 w-full overflow-hidden bg-elevated">
                  <div
                    className={cn(
                      "h-full transition-ui",
                      isLive ? "bg-brand" : "bg-ink-soft/40",
                    )}
                    style={{
                      width: isLive
                        ? `${Math.min(92, 48 + (Number(agent.stats[0]?.value) || 8) * 2)}%`
                        : "8%",
                    }}
                  />
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
