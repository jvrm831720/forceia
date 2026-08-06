import { MessageSquare } from "lucide-react";
import { Icon } from "@/components/ui/icon";

export function ConversationsEmptyState({
  title = "Nenhuma conversa",
  description = "Quando a equipe de IA começar a atender, as conversas aparecem aqui.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="flex h-full min-h-[200px] flex-col items-center justify-center px-6 text-center">
      <Icon icon={MessageSquare} size="lg" className="mb-2 text-ink-soft" />
      <p className="text-section text-ink">{title}</p>
      <p className="mt-1 max-w-xs text-body-muted text-ink-muted">{description}</p>
    </div>
  );
}
