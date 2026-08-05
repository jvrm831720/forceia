"use client";

import { cn } from "@/lib/utils";
import { formatMessageTime } from "@/lib/conversation-utils";
import type { ConversationMessage } from "@/types/conversation";
import { Check, CheckCheck } from "lucide-react";

export function MessageBubble({ message }: { message: ConversationMessage }) {
  if (message.sender === "system") {
    return (
      <div className="flex justify-center py-2">
        <span className="rounded-full bg-border-soft px-3 py-1 text-[11px] font-medium text-ink-muted">
          {message.content}
        </span>
      </div>
    );
  }

  const isLead = message.sender === "lead";
  const isAi = message.sender === "ai";
  const isHuman = message.sender === "human";

  return (
    <div
      className={cn(
        "flex w-full",
        isLead ? "justify-start" : "justify-end"
      )}
    >
      <div
        className={cn(
          "max-w-[78%] rounded-2xl px-3.5 py-2.5 shadow-card transition duration-200",
          isLead && "rounded-bl-md bg-white border border-border text-ink",
          isAi && "rounded-br-md bg-ai-soft text-ink",
          isHuman && "rounded-br-md bg-brand-soft text-ink"
        )}
      >
        {(isAi || isHuman) && (
          <div className="mb-1 flex items-center gap-1.5">
            {isAi && (
              <span className="inline-flex items-center rounded-full bg-ai/15 px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-ai">
                IA
              </span>
            )}
            {isHuman && (
              <span className="inline-flex items-center rounded-full bg-brand/15 px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-brand">
                Você
              </span>
            )}
          </div>
        )}
        <p className="whitespace-pre-wrap text-[13.5px] leading-relaxed">
          {message.content}
        </p>
        <div
          className={cn(
            "mt-1.5 flex items-center gap-1",
            isLead ? "justify-start" : "justify-end"
          )}
        >
          <span className="text-[10px] text-ink-soft">
            {formatMessageTime(message.timestamp)}
          </span>
          {!isLead && message.status && (
            <span className="text-ink-soft">
              {message.status === "read" ? (
                <CheckCheck className="h-3 w-3 text-brand" />
              ) : message.status === "delivered" ? (
                <CheckCheck className="h-3 w-3" />
              ) : (
                <Check className="h-3 w-3" />
              )}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
