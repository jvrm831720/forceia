"use client";

import { cn } from "@/lib/utils";
import {
  agentLabel,
  formatMessageTime,
  statusCode,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";

export function ConversationItem({
  conversation,
  selected,
  onSelect,
}: {
  conversation: Conversation;
  selected: boolean;
  onSelect: (id: string) => void;
}) {
  const code = statusCode(conversation.status);
  const needsYou = conversation.status === "needs_attention";
  const unread =
    typeof conversation.unreadCount === "number" && conversation.unreadCount > 0;

  return (
    <button
      type="button"
      onClick={() => onSelect(conversation.id)}
      aria-current={selected ? "true" : undefined}
      className={cn(
        "grid w-full grid-cols-[28px_1fr_auto] gap-x-2 border-b border-border px-3 py-2 text-left transition-colors duration-100",
        selected ? "bg-elevated" : "hover:bg-surface",
        needsYou && !selected && "bg-warning-soft/30",
      )}
    >
      <span
        className={cn(
          "pt-0.5 text-mono font-medium tabular-nums",
          code === "HO" && "text-warning",
          code === "AI" && "text-ink-muted",
          code === "HUM" && "text-ink-soft",
          code === "DONE" && "text-ink-soft",
        )}
      >
        {code}
      </span>

      <div className="min-w-0">
        <div className="flex items-baseline gap-1.5">
          <span
            className={cn(
              "truncate text-[13px] leading-4 text-ink",
              unread && "font-medium",
            )}
          >
            {conversation.leadName}
          </span>
          {unread && (
            <span className="shrink-0 text-mono text-brand">
              {conversation.unreadCount}
            </span>
          )}
        </div>
        <p className="truncate text-[12px] leading-4 text-ink-soft">
          {conversation.company}
        </p>
        <p className="mt-0.5 truncate text-[12px] leading-4 text-ink-soft">
          {conversation.lastMessage}
        </p>
        <p className="mt-0.5 text-[11px] leading-4 text-ink-soft">
          {agentLabel(conversation.currentOwner)}
        </p>
      </div>

      <time className="pt-0.5 text-right text-mono text-ink-soft">
        {formatMessageTime(conversation.lastMessageAt)}
      </time>
    </button>
  );
}
