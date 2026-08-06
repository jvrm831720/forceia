"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  agentBadgeVariant,
  agentLabel,
  formatMessageTime,
  statusCode,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";

const CODE_COLOR: Record<string, string> = {
  AI: "text-brand",
  HO: "text-warning",
  HUM: "text-ink-muted",
  DONE: "text-ink-soft",
};

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
    lastMessage,
    lastMessageAt,
    currentOwner,
    status,
    unreadCount,
  } = conversation;

  const code = statusCode(status);
  const needsYou = status === "needs_attention";

  return (
    <button
      type="button"
      onClick={() => onSelect(id)}
      aria-current={selected ? "true" : undefined}
      className={cn(
        "group relative flex w-full gap-2.5 border-l-2 px-3 py-2.5 text-left transition-ui duration-fast",
        selected
          ? "border-l-brand bg-surface"
          : needsYou
            ? "border-l-warning hover:bg-surface"
            : "border-l-transparent hover:bg-surface",
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate text-body font-medium text-ink">{leadName}</p>
            <p className="truncate text-meta text-ink-soft">{company}</p>
          </div>
          <div className="flex shrink-0 flex-col items-end gap-0.5">
            <time className="text-mono text-ink-soft">
              {formatMessageTime(lastMessageAt)}
            </time>
            {typeof unreadCount === "number" && unreadCount > 0 && (
              <span className="inline-flex h-4 min-w-4 items-center justify-center rounded-sm bg-brand px-1 text-mono text-white">
                {unreadCount}
              </span>
            )}
          </div>
        </div>

        <p className="mt-1 line-clamp-1 text-meta text-ink-muted">{lastMessage}</p>

        <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
          <span className={cn("text-mono font-medium", CODE_COLOR[code] ?? "text-ink-soft")}>
            {code}
          </span>
          <span className="text-mono text-ink-soft">·</span>
          <Badge variant={agentBadgeVariant(currentOwner)}>
            {agentLabel(currentOwner)}
          </Badge>
          {needsYou && <Badge variant="warning">handoff</Badge>}
        </div>
      </div>
    </button>
  );
}
