/**
 * Primary operations chart — multi-series, legend beyond color.
 * Series is presentation-only until API provides time-series.
 */

const DAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

const SERIES = {
  leads: [0.35, 0.42, 0.38, 0.55, 0.62, 0.48, 0.7],
  qualified: [0.2, 0.25, 0.22, 0.35, 0.4, 0.32, 0.45],
  meetings: [0.12, 0.15, 0.18, 0.22, 0.28, 0.2, 0.3],
  pipeline: [0.3, 0.38, 0.45, 0.52, 0.6, 0.55, 0.72],
};

const LEGEND = [
  { key: "pipeline", label: "Pipeline", color: "#05B5DB", style: "solid" as const },
  { key: "leads", label: "Leads", color: "#A7A7A7", style: "solid" as const },
  { key: "qualified", label: "Qualificados", color: "#0DA387", style: "solid" as const },
  { key: "meetings", label: "Reuniões", color: "#9B95FE", style: "dashed" as const },
] as const;

function toPath(values: number[], w: number, h: number, pad = 12): string {
  const step = (w - pad * 2) / (values.length - 1);
  return values
    .map((v, i) => {
      const x = pad + i * step;
      const y = h - pad - v * (h - pad * 2 - 14);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function toArea(values: number[], w: number, h: number, pad = 12): string {
  const line = toPath(values, w, h, pad);
  const step = (w - pad * 2) / (values.length - 1);
  const lastX = pad + (values.length - 1) * step;
  const base = h - pad;
  return `${line} L${lastX.toFixed(1)},${base} L${pad},${base} Z`;
}

export function OpsChart() {
  const W = 720;
  const H = 200;
  const pad = 12;
  const activeIdx = 6;

  return (
    <section className="border border-border bg-canvas">
      <div className="flex h-9 flex-wrap items-center justify-between gap-2 border-b border-border px-3">
        <div className="flex items-baseline gap-2">
          <h2 className="text-section text-ink">Evolução operacional</h2>
          <span className="text-meta text-ink-soft">7 dias</span>
        </div>
        <ul className="flex flex-wrap items-center gap-x-3 gap-y-1" aria-label="Legenda do gráfico">
          {LEGEND.map((l) => (
            <li key={l.key} className="flex items-center gap-1.5 text-meta text-ink-muted">
              <span
                className="inline-block h-0.5 w-3"
                style={{
                  background:
                    l.style === "dashed"
                      ? `repeating-linear-gradient(90deg, ${l.color} 0 3px, transparent 3px 5px)`
                      : l.color,
                }}
                aria-hidden
              />
              <span>{l.label}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="relative px-2 pb-2 pt-2 sm:px-3">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="h-[168px] w-full sm:h-[184px]"
          role="img"
          aria-label="Gráfico de evolução: pipeline em área, leads e qualificados em linha, reuniões em linha tracejada"
        >
          {[0.25, 0.5, 0.75].map((g) => {
            const y = pad + (1 - g) * (H - pad * 2 - 14);
            return (
              <line key={g} x1={pad} x2={W - pad} y1={y} y2={y} stroke="#232323" strokeWidth={1} />
            );
          })}

          {(() => {
            const step = (W - pad * 2) / (DAYS.length - 1);
            const x = pad + activeIdx * step;
            return (
              <line x1={x} x2={x} y1={pad} y2={H - pad - 4} stroke="#2B2B2B" strokeWidth={1} strokeDasharray="3 3" />
            );
          })()}

          <path d={toArea(SERIES.pipeline, W, H, pad)} fill="rgba(5,181,219,0.10)" />
          <path d={toPath(SERIES.pipeline, W, H, pad)} fill="none" stroke="#05B5DB" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
          <path d={toPath(SERIES.leads, W, H, pad)} fill="none" stroke="#A7A7A7" strokeWidth={1.25} strokeLinejoin="round" />
          <path d={toPath(SERIES.qualified, W, H, pad)} fill="none" stroke="#0DA387" strokeWidth={1.25} strokeLinejoin="round" />
          <path d={toPath(SERIES.meetings, W, H, pad)} fill="none" stroke="#9B95FE" strokeWidth={1.25} strokeDasharray="4 3" strokeLinejoin="round" />

          {([
            ["pipeline", SERIES.pipeline, "#05B5DB"],
            ["leads", SERIES.leads, "#A7A7A7"],
            ["qualified", SERIES.qualified, "#0DA387"],
            ["meetings", SERIES.meetings, "#9B95FE"],
          ] as const).map(([key, vals, color]) => {
            const step = (W - pad * 2) / (vals.length - 1);
            const x = pad + (vals.length - 1) * step;
            const y = H - pad - vals[vals.length - 1] * (H - pad * 2 - 14);
            return <circle key={key} cx={x} cy={y} r={2.5} fill={color} />;
          })}

          {DAYS.map((d, i) => {
            const step = (W - pad * 2) / (DAYS.length - 1);
            const x = pad + i * step;
            const isActive = i === activeIdx;
            return (
              <text
                key={d}
                x={x}
                y={H - 2}
                textAnchor="middle"
                fill={isActive ? "#F5F5F5" : "#707070"}
                style={{
                  fontSize: 10,
                  fontFamily: "IBM Plex Mono, monospace",
                  fontWeight: isActive ? 500 : 400,
                }}
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
