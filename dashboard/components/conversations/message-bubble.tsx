"use client";

import { cn } from "@/lib/utils";
import { agentLabel, formatMessageTime } from "@/lib/conversation-utils";
import type { ConversationMessage } from "@/types/conversation";

/** Midday details body rhythm. ForceIA operational event rows. */
export function MessageBubble({ message }: { message: ConversationMessage }) {
  const { sender, content, timestamp, agentRole, systemKind, status } = message;

  if (sender === "system") {
    return (
      <div className="border-b border-border px-4 py-3">
        <p className="text-center text-xs text-ink-soft">
          {content}
          <span className="ml-2 font-mono">
            {formatMessageTime(timestamp)}
            {systemKind ? ` · ${systemKind}` : ""}
          </span>
        </p>
      </div>
    );
  }

  const code =
    sender === "lead"
      ? "LEAD"
      : sender === "human"
        ? "HUM"
        : agentRole === "sdr"
          ? "SDR"
          : agentRole === "closer"
            ? "CLO"
            : agentRole === "followup"
              ? "FUP"
              : "AI";

  const origin =
    sender === "lead"
      ? "Lead"
      : sender === "human"
        ? "Humano"
        : agentRole
          ? agentLabel(agentRole)
          : "IA";

  return (
    <article className="border-b border-border px-4 py-3">
      <div className="mb-1.5 flex items-center gap-2">
        <span
          className={cn(
            "font-mono text-xs font-medium tabular-nums",
            sender === "ai" && "text-brand",
            sender === "lead" && "text-ink-muted",
            sender === "human" && "text-ink",
          )}
        >
          {code}
        </span>
        <span className="text-xs text-ink-soft">{origin}</span>
        <time className="ml-auto font-mono text-xs text-ink-soft">
          {formatMessageTime(timestamp)}
        </time>
        {status && status !== "sent" && (
          <span className="font-mono text-xs text-ink-soft">{status}</span>
        )}
      </div>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink">
        {content}
      </p>
    </article>
  );
}
