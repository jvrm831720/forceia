"use client";

import { cn } from "@/lib/utils";
import {
  agentLabel,
  formatMessageTime,
  statusCode,
  statusLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";

/**
 * Midday inbox-item structure:
 * h-[90px] · border · p-4 · flex-col gap-2
 * Row 1: name (font-semibold) + time (text-xs)
 * Row 2: secondary metric + status
 * Selected: bg-accent + border elevated
 */
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
        "flex h-[90px] w-full flex-col items-start gap-2 border border-border p-4 text-left text-sm transition-colors",
        selected
          ? "border-[#2C2C2C] bg-elevated"
          : "hover:bg-surface",
        needsYou && !selected && "border-warning/40",
      )}
    >
      <div className="flex w-full flex-col gap-1">
        <div className="mb-1 flex items-center">
          <div className="flex min-w-0 items-center gap-2">
            <span
              className={cn(
                "truncate font-semibold text-ink",
                unread && "font-semibold",
              )}
            >
              {conversation.leadName}
            </span>
            <span
              className={cn(
                "shrink-0 font-mono text-[10px] font-medium tabular-nums",
                code === "HO" && "text-warning",
                code === "AI" && "text-ink-muted",
                code === "HUM" && "text-ink-soft",
                code === "DONE" && "text-ink-soft",
              )}
            >
              {code}
            </span>
            {unread && (
              <span className="shrink-0 font-mono text-[10px] text-brand tabular-nums">
                {conversation.unreadCount}
              </span>
            )}
          </div>
          <time
            className={cn(
              "ml-auto shrink-0 text-xs",
              selected ? "text-ink" : "text-ink-soft",
            )}
          >
            {formatMessageTime(conversation.lastMessageAt)}
          </time>
        </div>

        <div className="flex w-full items-center">
          <p className="min-w-0 truncate text-xs font-medium text-ink-muted">
            {conversation.company}
            <span className="font-normal text-ink-soft"> · </span>
            <span className="font-normal text-ink-soft">
              {conversation.lastMessage}
            </span>
          </p>
          <span
            className={cn(
              "ml-auto shrink-0 pl-2 text-xs",
              needsYou ? "text-warning" : "text-ink-soft",
            )}
          >
            {needsYou ? statusLabel(conversation.status) : agentLabel(conversation.currentOwner)}
          </span>
        </div>
      </div>
    </button>
  );
}
