import { greetingForHour } from "@/lib/utils";
import type { WorkspaceInfo } from "@/types/dashboard";
import { Sparkles } from "lucide-react";

export function Hero({
  workspace,
  summary,
}: {
  workspace: WorkspaceInfo;
  summary: string;
}) {
  const greeting = greetingForHour();

  return (
    <section className="relative overflow-hidden rounded-2xl border border-border bg-surface-card p-6 shadow-card sm:p-8">
      <div
        className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full opacity-60"
        style={{
          background:
            "radial-gradient(circle, rgba(155,149,254,0.22) 0%, rgba(5,181,219,0.10) 45%, transparent 70%)",
        }}
      />
      <div
        className="pointer-events-none absolute -bottom-24 left-1/3 h-48 w-48 rounded-full opacity-50"
        style={{
          background:
            "radial-gradient(circle, rgba(13,163,135,0.12) 0%, transparent 70%)",
        }}
      />

      <div className="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-border bg-white/80 px-3 py-1 text-xs font-medium text-ink-muted shadow-card backdrop-blur">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-50" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Equipe em operação agora
          </div>

          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            {greeting}, {workspace.userName}{" "}
            <span aria-hidden className="inline-block">
              👋
            </span>
          </h1>

          <p className="mt-2 flex items-center gap-2 font-display text-lg font-medium text-ink sm:text-xl">
            <Sparkles className="h-5 w-5 text-ai" strokeWidth={1.75} />
            Sua equipe de IA está ativa.
          </p>

          <p className="mt-3 max-w-xl text-[15px] leading-relaxed text-ink-muted">
            {summary}
          </p>
        </div>

        <div className="flex shrink-0 flex-col gap-2 sm:flex-row lg:flex-col">
          <div className="rounded-xl border border-border bg-white px-4 py-3 shadow-card">
            <p className="text-[11px] font-medium uppercase tracking-wider text-ink-soft">
              Operação
            </p>
            <p className="mt-0.5 text-sm font-semibold text-ink">
              Contínua \u00b7 24/7
            </p>
          </div>
          <div className="rounded-xl border border-border bg-white px-4 py-3 shadow-card">
            <p className="text-[11px] font-medium uppercase tracking-wider text-ink-soft">
              Configuração
            </p>
            <p className="mt-0.5 text-sm font-semibold text-ink">
              Gerida pela ForceIA
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
