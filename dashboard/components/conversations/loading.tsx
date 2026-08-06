import { Skeleton } from "@/components/ui/skeleton";

export function ConversationsLoading() {
  return (
    <div
      className="flex h-full min-h-[320px] flex-col gap-0 border border-border bg-canvas"
      role="status"
      aria-live="polite"
      aria-label="Carregando conversas"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="border-b border-border px-3 py-2.5">
          <Skeleton className="mb-1.5 h-3 w-1/3" />
          <Skeleton className="mb-1 h-2.5 w-1/2" />
          <Skeleton className="h-2.5 w-2/3" />
        </div>
      ))}
    </div>
  );
}
