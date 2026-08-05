export function ConversationsLoading() {
  return (
    <div className="flex h-full min-h-[320px] items-center justify-center" role="status" aria-live="polite">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-brand" />
        <p className="text-sm text-ink-muted">Carregando conversas\u2026</p>
      </div>
    </div>
  );
}
