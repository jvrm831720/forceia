import { Button } from "@/components/ui/button";
import { Icon } from "@/components/ui/icon";
import { AlertTriangle } from "lucide-react";

export function ConversationsError({
  message = "Não foi possível atualizar a operação. Tente de novo.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="flex h-full min-h-[240px] flex-col items-center justify-center px-6 text-center"
      role="alert"
    >
      <Icon icon={AlertTriangle} size="lg" className="mb-2 text-warning" />
      <p className="text-section text-ink">Não foi possível carregar</p>
      <p className="mt-1 max-w-sm text-body-muted text-ink-muted">{message}</p>
      {onRetry && (
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="mt-3"
          onClick={onRetry}
        >
          Tentar de novo
        </Button>
      )}
    </div>
  );
}
