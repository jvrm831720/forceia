export function ConversationsEmptyState({
  title = "Nenhuma conversa",
  description = "Quando a equipe de IA começar a atender, as conversas aparecem aqui.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-12 text-center">
      <p className="text-[13px] text-ink">{title}</p>
      <p className="mt-1 max-w-xs text-[12px] text-ink-soft">{description}</p>
    </div>
  );
}
