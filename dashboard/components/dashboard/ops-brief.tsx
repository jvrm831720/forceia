import type { WorkspaceInfo } from "@/types/dashboard";

/**
 * Operational brief — the story of what the AI team did.
 * ForceIA signature: mono timestamp + live pulse + narrative sentence.
 */
export function OpsBrief({
  workspace,
  summary,
}: {
  workspace: WorkspaceInfo;
  summary: string;
}) {
  return (
    <section className="relative overflow-hidden border border-border bg-canvas">
      <div
        className="absolute inset-y-0 left-0 w-0.5 bg-brand"
        aria-hidden
      />

      <div className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-start sm:justify-between sm:gap-6 sm:px-5">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-50" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
            </span>
            <span className="text-label !tracking-[0.12em]">Operação ao vivo</span>
            <span className="text-mono text-ink-soft">·</span>
            <span className="text-mono text-ink-muted">{workspace.companyName}</span>
          </div>

          <p className="max-w-2xl text-[15px] font-medium leading-snug tracking-tight text-ink sm:text-base">
            {summary}
          </p>
        </div>

        <div className="flex shrink-0 flex-col items-start gap-1 sm:items-end">
          <span className="text-label">Equipe</span>
          <span className="text-mono text-ink-muted">SDR · Closer · Follow-up</span>
        </div>
      </div>
    </section>
  );
}
