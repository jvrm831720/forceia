"use client";

import { cn } from "@/lib/utils";
import {
  agentLabel,
  formatMessageTime,
} from "@/lib/conversation-utils";
import type { ConversationMessage } from "@/types/conversation";

export function MessageBubble({ message }: { message: ConversationMessage }) {
  const { sender, content, timestamp, agentRole, systemKind, status } = message;

  if (sender === "system") {
    return (
      <div className="flex justify-center px-3 py-1.5">
        <div className="max-w-[90%] border border-border bg-background px-2.5 py-1.5 text-center">
          <p className="text-meta text-ink-muted">{content}</p>
          <p className="mt-0.5 text-mono text-ink-soft">
            {formatMessageTime(timestamp)}
            {systemKind ? ` · ${systemKind}` : ""}
          </p>
        </div>
      </div>
    );
  }

  const isLead = sender === "lead";
  const isAi = sender === "ai";
  const isHuman = sender === "human";

  return (
    <div
      className={cn(
        "flex px-3 py-1",
        isLead ? "justify-start" : "justify-end",
      )}
    >
      <div
        className={cn(
          "max-w-[min(100%,420px)] border px-3 py-2",
          isLead && "border-border bg-surface",
          isAi && "border-brand/30 bg-brand-soft/40",
          isHuman && "border-border bg-elevated",
        )}
      >
        <div className="mb-1 flex items-center gap-1.5">
          <span
            className={cn(
              "text-mono font-medium",
              isLead && "text-ink-muted",
              isAi && "text-brand",
              isHuman && "text-ink-soft",
            )}
          >
            {isLead && "LEAD"}
            {isAi &&
              (agentRole
                ? agentLabel(agentRole).replace(" IA", "").toUpperCase()
                : "IA")}
            {isHuman && "HUM"}
          </span>
          <span className="text-mono text-ink-soft">
            {formatMessageTime(timestamp)}
          </span>
          {status && isHuman && (
            <span className="text-mono text-ink-soft">{status}</span>
          )}
        </div>
        <p className="whitespace-pre-wrap text-body text-ink">{content}</p>
      </div>
    </div>
  );
}
