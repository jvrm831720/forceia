import { cn } from "@/lib/utils";
import type { MetricCard } from "@/types/dashboard";

export function MetricCards({ metrics }: { metrics: MetricCard[] }) {
  return (
    <section>
      <div className="grid grid-cols-2 border border-border lg:grid-cols-5">
        {metrics.map((m, i) => (
          <div
            key={m.id}
            className={cn(
              "flex flex-col gap-1 bg-canvas px-3 py-3 transition-ui hover:bg-surface",
              i > 0 && "border-l border-border",
              i >= 2 && "border-t border-border lg:border-t-0",
            )}
          >
            <p className="text-label">{m.label}</p>
            <p
              className={cn(
                "font-mono text-xl font-medium tracking-tight tabular-nums text-ink sm:text-2xl",
                m.emphasis === "success" && "text-success",
                m.emphasis === "alert" && "text-warning",
              )}
            >
              {m.value}
            </p>
            {m.delta && (
              <p
                className={cn(
                  "text-[11px] font-medium",
                  m.deltaPositive === false ? "text-warning" : "text-success",
                )}
              >
                {m.delta}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
