import { Button } from "@/components/ui/button";

export function ConversationsError({
  message = "Não foi possível atualizar a operação. Tente de novo.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="flex h-full flex-col items-center justify-center px-6 text-center"
      role="alert"
    >
      <p className="text-[13px] text-ink">Não foi possível carregar</p>
      <p className="mt-1 max-w-sm text-[12px] text-ink-soft">{message}</p>
      {onRetry && (
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="mt-3 h-7"
          onClick={onRetry}
        >
          Tentar de novo
        </Button>
      )}
    </div>
  );
}
