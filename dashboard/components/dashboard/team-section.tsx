import { Badge } from "@/components/ui/badge";
import { Panel, PanelHeader, PanelBody } from "@/components/ui/panel";
import { cn } from "@/lib/utils";
import type { AgentCard, AgentStatus } from "@/types/dashboard";

const STATUS: Record<
  AgentStatus,
  { label: string; variant: "success" | "muted" | "warning"; dot: string }
> = {
  working: { label: "Running", variant: "success", dot: "bg-success" },
  paused: { label: "Paused", variant: "warning", dot: "bg-warning" },
  offline: { label: "Offline", variant: "muted", dot: "bg-ink-soft" },
};

export function TeamSection({ agents }: { agents: AgentCard[] }) {
  const active = agents.filter((a) => a.status === "working").length;

  return (
    <Panel>
      <PanelHeader
        title="Serviços de IA"
        meta={
          <span className="text-mono">
            {active}/{agents.length} active
          </span>
        }
      />
      <PanelBody>
        <div className="grid gap-0 sm:grid-cols-3">
          {agents.map((agent, i) => {
            const st = STATUS[agent.status];
            return (
              <div
                key={agent.id}
                className={cn(
                  "flex flex-col gap-2 px-3 py-3 transition-ui duration-fast hover:bg-surface",
                  i > 0 && "border-t border-border sm:border-t-0 sm:border-l",
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate text-body font-medium text-ink">
                      {agent.name}
                    </p>
                    <p className="truncate text-meta text-ink-soft">{agent.role}</p>
                  </div>
                  <Badge variant={st.variant}>
                    <span className={cn("h-1 w-1 rounded-full", st.dot)} />
                    {st.label}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {agent.stats.map((s) => (
                    <div key={s.label}>
                      <p className="text-label">{s.label}</p>
                      <p className="text-metric-sm text-ink">{s.value}</p>
                    </div>
                  ))}
                </div>
                <div className="h-0.5 w-full overflow-hidden rounded-full bg-elevated">
                  <div
                    className={cn(
                      "h-full rounded-full transition-ui",
                      agent.status === "working" ? "bg-ai" : "bg-ink-soft",
                    )}
                    style={{
                      width:
                        agent.status === "working"
                          ? `${Math.min(100, 40 + (Number(agent.stats[0]?.value) || 10) * 2)}%`
                          : "12%",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </PanelBody>
    </Panel>
  );
}
