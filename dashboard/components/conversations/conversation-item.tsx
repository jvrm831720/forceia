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
        "group relative flex h-11 w-full items-center gap-2 border-b border-border px-3 text-left transition-colors duration-100",
        selected ? "bg-surface" : "hover:bg-surface/60",
        needsYou && !selected && "bg-warning-soft/20",
      )}
    >
      <span
        className={cn(
          "absolute left-0 top-0 h-full w-0.5",
          selected && "bg-ink",
          needsYou && !selected && "bg-warning",
          !selected && !needsYou && "bg-transparent group-hover:bg-border",
        )}
        aria-hidden
      />

      <span
        className={cn(
          "w-7 shrink-0 text-mono font-medium tabular-nums",
          code === "HO" && "text-warning",
          code === "AI" && "text-ink-muted",
          code === "HUM" && "text-ink-soft",
          code === "DONE" && "text-ink-soft",
        )}
      >
        {code}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-1.5">
          <span
            className={cn(
              "truncate text-[13px] font-medium leading-4 text-ink",
              unread && "font-medium",
            )}
          >
            {conversation.leadName}
          </span>
          {unread && (
            <span className="shrink-0 text-mono text-brand tabular-nums">
              {conversation.unreadCount}
            </span>
          )}
        </div>
        <p className="truncate text-[12px] leading-4 text-ink-soft">
          {conversation.company}
          <span className="text-ink-soft/60"> · </span>
          {conversation.lastMessage}
        </p>
      </div>

      <div className="flex shrink-0 flex-col items-end gap-0.5">
        <time className="text-mono text-ink-soft">
          {formatMessageTime(conversation.lastMessageAt)}
        </time>
        <span className="text-[10px] leading-3 text-ink-soft">
          {agentLabel(conversation.currentOwner)}
        </span>
      </div>
    </button>
  );
}
