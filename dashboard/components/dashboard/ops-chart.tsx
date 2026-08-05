/**
 * Primary operations chart — presentation-only series.
 * Replace with API time-series when available; shape is intentional.
 */

const DAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

/** Normalized 0–1 series for the week (leads / pipeline narrative) */
const SERIES = {
  leads: [0.35, 0.42, 0.38, 0.55, 0.62, 0.48, 0.7],
  qualified: [0.2, 0.25, 0.22, 0.35, 0.4, 0.32, 0.45],
  meetings: [0.12, 0.15, 0.18, 0.22, 0.28, 0.2, 0.3],
  pipeline: [0.3, 0.38, 0.45, 0.52, 0.6, 0.55, 0.72],
};

const LEGEND = [
  { key: "pipeline", label: "Pipeline", color: "#05B5DB" },
  { key: "leads", label: "Leads", color: "#A7A7A7" },
  { key: "qualified", label: "Qualificados", color: "#0DA387" },
  { key: "meetings", label: "Reuniões", color: "#9B95FE" },
] as const;

function toPath(values: number[], w: number, h: number, pad = 8): string {
  const step = (w - pad * 2) / (values.length - 1);
  return values
    .map((v, i) => {
      const x = pad + i * step;
      const y = h - pad - v * (h - pad * 2);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function toArea(values: number[], w: number, h: number, pad = 8): string {
  const line = toPath(values, w, h, pad);
  const step = (w - pad * 2) / (values.length - 1);
  const lastX = pad + (values.length - 1) * step;
  return `${line} L${lastX.toFixed(1)},${h - pad} L${pad},${h - pad} Z`;
}

export function OpsChart() {
  const W = 640;
  const H = 200;

  return (
    <section className="border border-border bg-canvas">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-3 py-2">
        <div>
          <h2 className="text-[13px] font-medium text-ink">Evolução operacional</h2>
          <p className="text-[11px] text-ink-soft">Leads · qualificados · reuniões · pipeline</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {LEGEND.map((l) => (
            <span key={l.key} className="flex items-center gap-1.5 text-[11px] text-ink-muted">
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: l.color }} />
              {l.label}
            </span>
          ))}
        </div>
      </div>

      <div className="relative px-2 pb-1 pt-3 sm:px-3">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="h-[180px] w-full sm:h-[200px]"
          role="img"
          aria-label="Gráfico de evolução operacional da semana"
        >
          {[0.25, 0.5, 0.75].map((g) => {
            const y = 8 + (1 - g) * (H - 16);
            return (
              <line
                key={g}
                x1={8}
                x2={W - 8}
                y1={y}
                y2={y}
                stroke="#232323"
                strokeWidth={1}
              />
            );
          })}

          <path
            d={toArea(SERIES.pipeline, W, H)}
            fill="rgba(5,181,219,0.12)"
            stroke="none"
          />
          <path
            d={toPath(SERIES.pipeline, W, H)}
            fill="none"
            stroke="#05B5DB"
            strokeWidth={1.75}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          <path d={toPath(SERIES.leads, W, H)} fill="none" stroke="#A7A7A7" strokeWidth={1.25} strokeLinejoin="round" />
          <path d={toPath(SERIES.qualified, W, H)} fill="none" stroke="#0DA387" strokeWidth={1.25} strokeLinejoin="round" />
          <path d={toPath(SERIES.meetings, W, H)} fill="none" stroke="#9B95FE" strokeWidth={1.25} strokeLinejoin="round" />

          {DAYS.map((d, i) => {
            const step = (W - 16) / (DAYS.length - 1);
            const x = 8 + i * step;
            return (
              <text
                key={d}
                x={x}
                y={H - 2}
                textAnchor="middle"
                className="fill-[#707070]"
                style={{ fontSize: 10, fontFamily: "IBM Plex Mono, monospace" }}
              >
                {d}
              </text>
            );
          })}
        </svg>
      </div>
    </section>
  );
}
