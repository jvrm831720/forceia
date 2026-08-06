export function ConversationsLoading() {
  return (
    <div
      className="flex flex-col gap-4"
      role="status"
      aria-label="Carregando"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="flex h-[90px] flex-col gap-2 border border-border p-4"
        >
          <div className="flex items-center justify-between">
            <div className="h-3 w-[120px] animate-pulse bg-elevated" />
            <div className="h-3 w-[50px] animate-pulse bg-elevated" />
          </div>
          <div className="flex items-center justify-between">
            <div className="h-3 w-[80px] animate-pulse bg-elevated" />
            <div className="h-4 w-[60px] animate-pulse bg-elevated" />
          </div>
        </div>
      ))}
    </div>
  );
}
