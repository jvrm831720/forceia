"use client";

import { Badge } from "@/components/ui/badge";
import {
  agentBadgeVariant,
  agentLabel,
  channelLabel,
  formatListTime,
} from "@/lib/conversation-utils";
import { cn } from "@/lib/utils";
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
  const { participant, responsible, lastMessagePreview, lastMessageAt, unreadCount, channel, status } =
    conversation;

  return (
    <button
      type="button"
      onClick={() => onSelect(conversation.id)}
      aria-current={selected ? "true" : undefined}
      className={cn(
        "w-full rounded-xl border px-3 py-3 text-left transition duration-200",
        selected
          ? "border-brand/30 bg-brand-soft shadow-card"
          : "border-transparent bg-transparent hover:bg-white hover:border-border hover:shadow-card"
      )}
    >
      <div className="flex gap-3">
        <div
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl font-display text-xs font-bold",
            selected ? "bg-white text-brand" : "bg-border-soft text-ink-muted"
          )}
        >
          {participant.initials}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink">{participant.name}</p>
              <p className="truncate text-[12px] text-ink-muted">{participant.company}</p>
            </div>
            <time className="shrink-0 font-mono text-[11px] text-ink-soft">
              {formatListTime(lastMessageAt)}
            </time>
          </div>
          <p className="mt-1.5 line-clamp-1 text-[13px] text-ink-muted">{lastMessagePreview}</p>
          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <Badge variant={agentBadgeVariant(responsible)}>
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  responsible === "sdr" && "bg-success",
                  responsible === "closer" && "bg-ai",
                  responsible === "followup" && "bg-highlight",
                  responsible === "human" && "bg-ink-soft"
                )}
              />
              {agentLabel(responsible)}
            </Badge>
            <span className="text-[11px] text-ink-soft">{channelLabel(channel)}</span>
            {status === "needs_attention" && <Badge variant="alert">Aten\u00e7\u00e3o</Badge>}
            {unreadCount > 0 && (
              <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-brand px-1.5 text-[10px] font-bold text-white">
                {unreadCount}
              </span>
            )}
          </div>
        </div>
      </div>
    </button>
  );
}
