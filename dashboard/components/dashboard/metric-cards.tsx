import { cn } from "@/lib/utils";
import type { MetricCard } from "@/types/dashboard";

export function MetricCards({ metrics }: { metrics: MetricCard[] }) {
  return (
    <section className="border-y border-border">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
        {metrics.map((m, i) => (
          <div
            key={m.id}
            className={cn(
              "flex flex-col gap-0.5 px-3 py-2.5 transition-ui hover:bg-surface",
              i > 0 && "border-l border-border",
              i >= 2 && "border-t border-border sm:border-t-0",
              i >= 3 && "sm:border-t lg:border-t-0",
            )}
          >
            <p className="text-label truncate">{m.label}</p>
            <p
              className={cn(
                "font-mono text-lg font-medium tabular-nums tracking-tight text-ink sm:text-xl",
                m.emphasis === "success" && "text-success",
                m.emphasis === "alert" && "text-warning",
              )}
            >
              {m.value}
            </p>
            {m.delta && (
              <p
                className={cn(
                  "font-mono text-[10px]",
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
