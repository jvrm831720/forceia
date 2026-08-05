import { Badge } from "@/components/ui/badge";

const AGENTS = [
  {
    name: "SDR IA",
    role: "Atendendo novos leads",
    status: "working" as const,
  },
  {
    name: "Closer IA",
    role: "Conduzindo oportunidades",
    status: "working" as const,
  },
  {
    name: "Follow-up IA",
    role: "Recuperando conversas",
    status: "working" as const,
  },
];

export function AuthBrandPanel() {
  return (
    <div className="relative flex h-full flex-col justify-between overflow-hidden p-8 lg:p-12">
      {/* Soft ambient shapes */}
      <div
        className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand/10 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -bottom-16 -left-16 h-56 w-56 rounded-full bg-ai/10 blur-3xl"
        aria-hidden
      />

      <div className="relative">
        <div className="mb-10 flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-white shadow-card">
            <span className="font-display text-base font-bold tracking-tight">
              F
            </span>
          </div>
          <div className="leading-tight">
            <div className="font-display text-lg font-semibold tracking-tight text-ink">
              ForceIA
            </div>
            <div className="text-[12px] text-ink-soft">
              Time de vendas com IA
            </div>
          </div>
        </div>

        <h1 className="font-display text-3xl font-semibold leading-tight tracking-tight text-ink lg:text-[2.15rem]">
          Sua força de vendas
          <br />
          continua trabalhando.
        </h1>
        <p className="mt-4 max-w-md text-[15px] leading-relaxed text-ink-muted">
          Acompanhe seus agentes de IA, conversas, oportunidades, reuniões e
          resultados em um só lugar.
        </p>
      </div>

      <div className="relative mt-10 max-w-sm">
        <div className="rounded-2xl border border-border bg-surface-card/90 p-4 shadow-card backdrop-blur-sm">
          <div className="mb-3 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            <span className="text-xs font-semibold text-ink">
              Equipe IA ativa
            </span>
          </div>

          <ul className="space-y-2.5">
            {AGENTS.map((agent) => (
              <li
                key={agent.name}
                className="flex items-center justify-between gap-3 rounded-xl border border-border-soft bg-surface px-3 py-2.5"
              >
                <div className="min-w-0">
                  <p className="text-[13px] font-semibold text-ink">
                    {agent.name}
                  </p>
                  <p className="truncate text-[11px] text-ink-soft">
                    {agent.role}
                  </p>
                </div>
                <Badge variant="success" className="!py-0 shrink-0">
                  ativo
                </Badge>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
