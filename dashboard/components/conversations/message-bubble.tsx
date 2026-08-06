"use client";

import { cn } from "@/lib/utils";
import { agentLabel, formatMessageTime } from "@/lib/conversation-utils";
import type { ConversationMessage } from "@/types/conversation";

/** Operational timeline row — not a chat bubble. */
export function MessageBubble({ message }: { message: ConversationMessage }) {
  const { sender, content, timestamp, agentRole, systemKind } = message;

  if (sender === "system") {
    return (
      <div className="border-b border-border px-4 py-2">
        <p className="text-center text-[11px] text-ink-soft">
          {content}
          <span className="ml-2 text-mono">
            {formatMessageTime(timestamp)}
            {systemKind ? ` · ${systemKind}` : ""}
          </span>
        </p>
      </div>
    );
  }

  const who =
    sender === "lead"
      ? "LEAD"
      : sender === "human"
        ? "HUM"
        : agentRole
          ? agentLabel(agentRole).replace(" IA", "").toUpperCase()
          : "IA";

  return (
    <article
      className={cn(
        "border-b border-border px-4 py-2.5",
        sender === "ai" && "bg-surface/40",
      )}
    >
      <div className="mb-1 flex items-baseline justify-between gap-2">
        <span
          className={cn(
            "text-mono font-medium",
            sender === "ai" && "text-brand",
            sender === "lead" && "text-ink-muted",
            sender === "human" && "text-ink-soft",
          )}
        >
          {who}
        </span>
        <time className="text-mono text-ink-soft">
          {formatMessageTime(timestamp)}
        </time>
      </div>
      <p className="whitespace-pre-wrap text-[13px] leading-5 text-ink">
        {content}
      </p>
    </article>
  );
}
