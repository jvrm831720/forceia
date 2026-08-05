"use client";

import { useEffect, useRef } from "react";
import type { Conversation } from "@/types/conversation";
import { dateKey } from "@/lib/conversation-utils";
import { ConversationHeader } from "./conversation-header";
import { ConversationInput } from "./conversation-input";
import { MessageBubble } from "./message-bubble";
import { HandoffCard } from "./handoff-card";
import { TypingIndicator } from "./typing-indicator";
import { ConversationsEmptyState } from "./empty-state";

export function ConversationView({
  conversation,
  onBack,
  onAssume,
  onReturnToAi,
  onResolve,
  onAddNote,
  onOpenLead,
  onDismissHandoff,
  onSend,
}: {
  conversation: Conversation | null;
  onBack?: () => void;
  onAssume: () => void;
  onReturnToAi: () => void;
  onResolve: () => void;
  onAddNote: () => void;
  onOpenLead: () => void;
  onDismissHandoff: () => void;
  onSend: (text: string) => void;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation?.id, conversation?.messages.length, conversation?.isTyping]);

  if (!conversation) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-surface">
        <ConversationsEmptyState
          title="Selecione uma conversa"
          description="Escolha um atendimento na lista para acompanhar o time de IA em tempo real."
        />
      </div>
    );
  }

  const isClosed = conversation.status === "closed";
  const messages = conversation.messages;

  let lastDate = "";

  return (
    <div className="flex h-full flex-col bg-surface">
      <ConversationHeader
        conversation={conversation}
        onBack={onBack}
        onAssume={onAssume}
        onReturnToAi={onReturnToAi}
        onResolve={onResolve}
        onAddNote={onAddNote}
        onOpenLead={onOpenLead}
      />

      {conversation.handoff && !conversation.handoff.dismissed && (
        <div className="pt-3">
          <HandoffCard
            handoff={conversation.handoff}
            onAssume={onAssume}
            onDismiss={onDismissHandoff}
          />
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-2xl flex-col gap-3">
          {messages.map((msg) => {
            const dk = dateKey(msg.timestamp);
            const showSeparator = dk !== lastDate;
            lastDate = dk;

            return (
              <div key={msg.id}>
                {showSeparator && (
                  <div className="my-3 flex justify-center">
                    <span className="rounded-full bg-border-soft px-3 py-1 text-[11px] font-medium capitalize text-ink-soft">
                      {dk}
                    </span>
                  </div>
                )}
                <MessageBubble message={msg} />
              </div>
            );
          })}

          {conversation.isTyping === "ai" && (
            <TypingIndicator label="IA digitando" variant="ai" />
          )}
          {conversation.isTyping === "lead" && (
            <TypingIndicator label="Cliente digitando" variant="lead" />
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <ConversationInput
        disabled={isClosed}
        onSend={onSend}
        placeholder={
          conversation.currentOwner === "human"
            ? "Responder como humano…"
            : "Assuma a conversa para responder…"
        }
      />
    </div>
  );
}
