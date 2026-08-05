import { MessageSquare } from "lucide-react";

export function ConversationsEmptyState({
  title = "Nenhuma conversa",
  description = "Quando sua equipe de IA começar a atender leads, elas aparecem aqui.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="flex h-full min-h-[240px] flex-col items-center justify-center px-6 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-border-soft text-ink-soft">
        <MessageSquare className="h-5 w-5" strokeWidth={1.75} />
      </div>
      <p className="font-display text-base font-semibold text-ink">{title}</p>
      <p className="mt-1 max-w-xs text-sm text-ink-muted">{description}</p>
    </div>
  );
}
