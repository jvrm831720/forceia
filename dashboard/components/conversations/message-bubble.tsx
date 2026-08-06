"use client";

import { cn } from "@/lib/utils";
import { agentLabel, formatMessageTime } from "@/lib/conversation-utils";
import type { ConversationMessage } from "@/types/conversation";

/** Operational timeline event — not a chat bubble. */
export function MessageBubble({ message }: { message: ConversationMessage }) {
  const { sender, content, timestamp, agentRole, systemKind, status } = message;

  if (sender === "system") {
    return (
      <div className="border-b border-border px-4 py-2">
        <p className="text-center text-[11px] leading-4 text-ink-soft">
          {content}
          <span className="ml-2 text-mono">
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
    <article
      className={cn(
        "relative border-b border-border px-4 py-2.5",
        sender === "ai" && "bg-surface/30",
      )}
    >
      <span
        className={cn(
          "absolute left-0 top-0 h-full w-0.5",
          sender === "ai" && "bg-brand/40",
          sender === "lead" && "bg-border",
          sender === "human" && "bg-ink-soft/40",
        )}
        aria-hidden
      />

      <div className="mb-1 flex items-baseline gap-2">
        <span
          className={cn(
            "text-mono font-medium tabular-nums",
            sender === "ai" && "text-brand",
            sender === "lead" && "text-ink-muted",
            sender === "human" && "text-ink",
          )}
        >
          {code}
        </span>
        <time className="text-mono text-ink-soft">
          {formatMessageTime(timestamp)}
        </time>
        <span className="text-[11px] text-ink-soft">{origin}</span>
        {status && status !== "sent" && (
          <span className="ml-auto text-mono text-ink-soft">{status}</span>
        )}
      </div>

      <p className="whitespace-pre-wrap text-[13px] leading-5 text-ink">
        {content}
      </p>
    </article>
  );
}
