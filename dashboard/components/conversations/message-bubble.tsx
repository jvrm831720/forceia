import { Badge } from "@/components/ui/badge";
import { agentLabel, formatMessageTime, senderBubbleAlign } from "@/lib/conversation-utils";
import { cn } from "@/lib/utils";
import type { ConversationMessage } from "@/types/conversation";

export function MessageBubble({ message }: { message: ConversationMessage }) {
  const align = senderBubbleAlign(message.sender);

  if (message.sender === "system") {
    return (
      <div className="flex justify-center py-1" role="status">
        <p className="rounded-full bg-border-soft px-3 py-1 text-[12px] font-medium text-ink-muted">
          {message.content}
        </p>
      </div>
    );
  }

  const isLead = message.sender === "lead";
  const isAi = message.sender === "ai";
  const isHuman = message.sender === "human";

  return (
    <div
      className={cn(
        "flex max-w-[min(100%,420px)] flex-col gap-1",
        align === "right" ? "ml-auto items-end" : "mr-auto items-start"
      )}
    >
      <div
        className={cn(
          "rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed shadow-card",
          isLead && "rounded-tl-md border border-border bg-white text-ink",
          isAi && "rounded-tr-md bg-ai-soft text-ink",
          isHuman && "rounded-tr-md bg-brand-soft text-ink"
        )}
      >
        {isAi && message.agentRole && (
          <div className="mb-1.5">
            <Badge variant="ai" className="text-[10px]">
              IA \u00b7 {agentLabel(message.agentRole)}
            </Badge>
          </div>
        )}
        {isHuman && (
          <div className="mb-1.5">
            <Badge variant="default" className="text-[10px]">
              Humano
            </Badge>
          </div>
        )}
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
      <div
        className={cn(
          "flex items-center gap-1.5 px-1 font-mono text-[11px] text-ink-soft",
          align === "right" ? "flex-row-reverse" : "flex-row"
        )}
      >
        <time dateTime={message.createdAt}>{formatMessageTime(message.createdAt)}</time>
        {message.status && align === "right" && (
          <span className="capitalize">{message.status === "read" ? "lida" : message.status === "delivered" ? "entregue" : "enviada"}</span>
        )}
      </div>
    </div>
  );
}
