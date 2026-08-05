/**
 * Product visualization for auth — no marketing copy.
 * Abstract composition of the ForceIA operations surface.
 */
export function AuthBrandPanel() {
  return (
    <div className="relative flex h-full min-h-screen flex-col">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 30% 20%, rgba(5,181,219,0.06) 0%, transparent 55%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(155,149,254,0.05) 0%, transparent 50%)",
        }}
        aria-hidden
      />

      <div className="relative flex flex-1 items-center justify-center p-10 xl:p-14">
        <div className="relative w-full max-w-[520px]">
          <div
            className="pointer-events-none absolute -inset-6 rounded-2xl opacity-40 blur-2xl"
            style={{ background: "rgba(5,181,219,0.08)" }}
            aria-hidden
          />

          <div className="relative overflow-hidden rounded-lg border border-[#232323] bg-[#0e0e0e] shadow-[0_24px_80px_rgba(0,0,0,0.55)]">
            <div className="flex h-9 items-center gap-2 border-b border-[#232323] bg-[#090909] px-3">
              <span className="h-2 w-2 rounded-full bg-[#2b2b2b]" />
              <span className="h-2 w-2 rounded-full bg-[#2b2b2b]" />
              <span className="h-2 w-2 rounded-full bg-[#2b2b2b]" />
              <span className="ml-3 font-mono text-[10px] text-[#707070]">
                forceia · operations
              </span>
              <span className="ml-auto flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#0da387]" />
                <span className="text-[10px] text-[#707070]">live</span>
              </span>
            </div>

            <div className="flex">
              <div className="flex w-10 shrink-0 flex-col items-center gap-2 border-r border-[#232323] bg-[#090909] py-3">
                <div className="h-5 w-5 rounded bg-[#05b5db]/20" />
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className={`h-5 w-5 rounded ${i === 1 ? "bg-[#1a1a1a]" : "bg-[#141414]"}`}
                  />
                ))}
              </div>

              <div className="min-w-0 flex-1 p-3">
                <div className="mb-3 grid grid-cols-4 gap-px overflow-hidden rounded border border-[#232323] bg-[#232323]">
                  {[
                    { l: "Pipeline", v: "R$ 420k" },
                    { l: "Leads", v: "35" },
                    { l: "Reuniões", v: "7" },
                    { l: "Qualif.", v: "12" },
                  ].map((m) => (
                    <div key={m.l} className="bg-[#0e0e0e] px-2.5 py-2">
                      <p className="text-[9px] uppercase tracking-wider text-[#707070]">
                        {m.l}
                      </p>
                      <p className="mt-0.5 font-mono text-[13px] font-medium tabular-nums text-[#f5f5f5]">
                        {m.v}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="overflow-hidden rounded border border-[#232323]">
                  <div className="border-b border-[#232323] bg-[#141414] px-2.5 py-1.5">
                    <span className="text-[10px] font-medium text-[#a7a7a7]">
                      Agentes
                    </span>
                  </div>
                  {[
                    { n: "SDR IA", s: "18 conv" },
                    { n: "Closer IA", s: "5 neg" },
                    { n: "Follow-up IA", s: "12 fup" },
                  ].map((a) => (
                    <div
                      key={a.n}
                      className="flex items-center justify-between border-b border-[#232323] px-2.5 py-2 last:border-0"
                    >
                      <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#0da387]" />
                        <span className="text-[11px] text-[#f5f5f5]">{a.n}</span>
                      </div>
                      <span className="font-mono text-[10px] text-[#707070]">
                        {a.s}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="mt-3 space-y-1.5 opacity-70">
                  {[
                    "QUAL  Lead qualificado · Clínica Norte",
                    "MTG   Reunião confirmada · 14:30",
                    "PIPE  +R$ 48.000 pipeline",
                  ].map((line) => (
                    <p
                      key={line}
                      className="truncate font-mono text-[10px] text-[#707070]"
                    >
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div
            className="pointer-events-none absolute inset-0 rounded-lg"
            style={{
              boxShadow: "inset 0 0 80px 20px rgba(10,10,10,0.35)",
            }}
            aria-hidden
          />
        </div>
      </div>
    </div>
  );
}
