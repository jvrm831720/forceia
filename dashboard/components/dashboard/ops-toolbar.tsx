import type { WorkspaceInfo } from "@/types/dashboard";

export function OpsToolbar({
  workspace,
  period = "Últimos 7 dias",
}: {
  workspace: WorkspaceInfo;
  period?: string;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-2.5">
      <div className="flex min-w-0 flex-wrap items-center gap-2.5">
        <div>
          <p className="text-label">Operação</p>
          <h1 className="text-[14px] font-medium tracking-tight text-ink">
            {workspace.companyName}
          </h1>
        </div>
        <div className="hidden h-5 w-px bg-border sm:block" aria-hidden />
        <button
          type="button"
          className="rounded-sm border border-border bg-surface px-2 py-1 text-[11px] text-ink-muted transition-ui duration-fast hover:bg-surface-hover hover:text-ink focus-visible:outline-none focus-visible:shadow-focus"
        >
          {period}
        </button>
      </div>

      <div className="flex items-center gap-2.5">
        <div
          className="flex items-center gap-1.5 rounded-sm border border-border bg-surface px-2 py-1"
          role="status"
          aria-label="Status da equipe de IA"
        >
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-40" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
          </span>
          <span className="text-[11px] text-ink-muted">IA em operação</span>
        </div>
        <span className="hidden font-mono text-[10px] tracking-wide text-ink-soft sm:inline">
          SDR · CLOSER · FUP
        </span>
      </div>
    </div>
  );
}
