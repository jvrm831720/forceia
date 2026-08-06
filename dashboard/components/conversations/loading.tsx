export function ConversationsLoading() {
  return (
    <div className="flex h-full flex-col" role="status" aria-label="Carregando">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="border-b border-border px-3 py-2">
          <div className="mb-1.5 h-2.5 w-1/4 animate-pulse bg-elevated" />
          <div className="mb-1 h-2 w-1/2 animate-pulse bg-elevated" />
          <div className="h-2 w-2/3 animate-pulse bg-elevated" />
        </div>
      ))}
    </div>
  );
}
