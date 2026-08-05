"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  agentBadgeVariant,
  agentLabel,
  channelLabel,
  formatMessageTime,
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
  const {
    id,
    leadName,
    company,
    avatarInitials,
    lastMessage,
    lastMessageAt,
    channel,
    currentOwner,
    status,
    unreadCount,
  } = conversation;

  return (
    <button
      type="button"
      onClick={() => onSelect(id)}
      aria-current={selected ? "true" : undefined}
      className={cn(
        "group flex w-full gap-3 rounded-xl px-3 py-3 text-left transition duration-200",
        selected
          ? "bg-brand-soft shadow-card"
          : "hover:bg-border-soft"
      )}
    >
      <div className="relative shrink-0">
        <div
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-full font-display text-xs font-bold",
            selected ? "bg-brand text-white" : "bg-border-soft text-ink-muted"
          )}
        >
          {avatarInitials}
        </div>
        {status === "needs_attention" && (
          <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-alert" />
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-ink">{leadName}</p>
            <p className="truncate text-[12px] text-ink-soft">{company}</p>
          </div>
          <span className="shrink-0 text-[11px] text-ink-soft">
            {formatMessageTime(lastMessageAt)}
          </span>
        </div>

        <p className="mt-1 truncate text-[12.5px] text-ink-muted">{lastMessage}</p>

        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <Badge variant={agentBadgeVariant(currentOwner)} className="!py-0 !text-[10px]">
            {agentLabel(currentOwner)}
          </Badge>
          <span className="text-[10px] text-ink-soft">{channelLabel(channel)}</span>
          {typeof unreadCount === "number" && unreadCount > 0 && (
            <span className="ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-brand px-1.5 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
