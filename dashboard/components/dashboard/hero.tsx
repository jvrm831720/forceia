import { greetingForHour } from "@/lib/utils";
import type { WorkspaceInfo } from "@/types/dashboard";
import { Sparkles } from "lucide-react";

export function Hero({ workspace, summary }: { workspace: WorkspaceInfo; summary: string }) {
  const greeting = greetingForHour();
  return (
    <section className="border-b border-border pb-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 inline-flex items-center gap-2 text-xs font-medium text-ink-muted">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-40" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Equipe em operação agora
          </div>
          <h1 className="font-display text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
            {greeting}, {workspace.userName}
          </h1>
          <p className="mt-2 flex items-center gap-2 text-[15px] font-medium text-ink">
            <Sparkles className="h-4 w-4 text-ai" strokeWidth={1.75} />
            Sua equipe de IA está ativa.
          </p>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-ink-muted">{summary}</p>
        </div>
        <div className="flex shrink-0 gap-6 border-l border-border pl-6">
          <div>
            <p className="text-label">Operação</p>
            <p className="mt-1 text-sm font-semibold text-ink">Contínua · 24/7</p>
          </div>
          <div>
            <p className="text-label">Configuração</p>
            <p className="mt-1 text-sm font-semibold text-ink">Gerida pela ForceIA</p>
          </div>
        </div>
      </div>
    </section>
  );
}
