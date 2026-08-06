export function ConversationsEmptyState({
  title = "Nenhuma conversa",
  description = "Quando a equipe de IA começar a atender, as conversas aparecem aqui.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <div className="max-w-[250px] space-y-1">
        <p className="text-sm font-medium text-ink">{title}</p>
        <p className="text-xs text-ink-soft">{description}</p>
      </div>
    </div>
  );
}
