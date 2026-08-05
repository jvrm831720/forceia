import { cn } from "@/lib/utils";
import type { MetricCard } from "@/types/dashboard";
import { CalendarCheck2, CircleDollarSign, ShieldCheck, UserPlus, Users } from "lucide-react";

const ICONS = { leads: UserPlus, qualified: Users, meetings: CalendarCheck2, pipeline: CircleDollarSign, approval: ShieldCheck } as const;

export function MetricCards({ metrics }: { metrics: MetricCard[] }) {
  return (
    <section>
      <div className="mb-3 flex items-baseline justify-between">
        <h2 className="font-display text-sm font-semibold tracking-tight text-ink">Produtividade</h2>
        <p className="text-label">Hoje</p>
      </div>
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border bg-border lg:grid-cols-5">
        {metrics.map((m) => {
          const Icon = ICONS[m.icon] ?? Users;
          return (
            <div key={m.id} className="flex flex-col gap-3 bg-surface px-4 py-4 transition-ui hover:bg-surface-hover">
              <div className="flex items-center justify-between">
                <Icon className="h-4 w-4 text-ink-soft" strokeWidth={1.75} />
                {m.delta && (
                  <span className={cn("text-[11px] font-medium", m.deltaPositive === false ? "text-warning" : "text-success")}>{m.delta}</span>
                )}
              </div>
              <div>
                <p className="font-display text-2xl font-semibold tracking-tight text-ink tabular-nums">{m.value}</p>
                <p className="mt-0.5 text-xs text-ink-muted">{m.label}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
