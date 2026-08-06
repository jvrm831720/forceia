import { cn } from "@/lib/utils";
import type { MetricCard } from "@/types/dashboard";

function Spark({
  values,
  positive,
}: {
  values: number[];
  positive?: boolean;
}) {
  const w = 48;
  const h = 14;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const pts = values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * w;
      const y = h - ((v - min) / range) * (h - 2) - 1;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg width={w} height={h} className="opacity-70" aria-hidden>
      <polyline
        points={pts}
        fill="none"
        stroke={positive === false ? "#DD6539" : "#0DA387"}
        strokeWidth={1.25}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

const SPARKS: Record<string, number[]> = {
  leads: [18, 22, 20, 28, 31, 26, 35],
  qualified: [4, 5, 6, 8, 9, 7, 12],
  meetings: [2, 3, 3, 4, 5, 4, 7],
  pipeline: [180, 220, 260, 310, 360, 380, 420],
  approval: [3, 2, 2, 1, 2, 2, 2],
};

export function MetricCards({ metrics }: { metrics: MetricCard[] }) {
  return (
    <section className="border-y border-border" aria-label="Indicadores-chave">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
        {metrics.map((m, i) => (
          <div
            key={m.id}
            className={cn(
              "flex flex-col gap-1 px-3 py-2 transition-ui duration-fast hover:bg-surface",
              i > 0 && "border-l border-border",
              i >= 2 && "border-t border-border sm:border-t-0",
              i >= 3 && "sm:border-t lg:border-t-0",
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-label truncate">{m.label}</p>
              {SPARKS[m.id] && (
                <Spark values={SPARKS[m.id]} positive={m.deltaPositive} />
              )}
            </div>
            <p
              className={cn(
                "text-metric text-ink",
                m.emphasis === "success" && "text-success",
                m.emphasis === "alert" && "text-warning",
              )}
            >
              {m.value}
            </p>
            {m.delta && (
              <p
                className={cn(
                  "text-mono",
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
