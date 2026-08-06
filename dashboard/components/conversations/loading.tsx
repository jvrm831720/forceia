export function ConversationsLoading() {
  return (
    <div className="flex h-full flex-col" role="status" aria-label="Carregando">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="flex h-11 items-center gap-2 border-b border-border px-3">
          <div className="h-2.5 w-6 animate-pulse bg-elevated" />
          <div className="min-w-0 flex-1 space-y-1.5">
            <div className="h-2.5 w-1/3 animate-pulse bg-elevated" />
            <div className="h-2 w-2/3 animate-pulse bg-elevated" />
          </div>
          <div className="h-2 w-8 animate-pulse bg-elevated" />
        </div>
      ))}
    </div>
  );
}
