import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export function ConversationsError({
  message = "N\u00e3o foi poss\u00edvel carregar as conversas.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex h-full min-h-[240px] flex-col items-center justify-center px-6 text-center" role="alert">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-alert-soft text-alert">
        <AlertTriangle className="h-5 w-5" strokeWidth={1.75} />
      </div>
      <p className="font-display text-base font-semibold text-ink">Algo deu errado</p>
      <p className="mt-1 max-w-sm text-sm text-ink-muted">{message}</p>
      {onRetry && (
        <Button type="button" variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
          Tentar de novo
        </Button>
      )}
    </div>
  );
}
