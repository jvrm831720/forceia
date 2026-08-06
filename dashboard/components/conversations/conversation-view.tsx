"use client";

import type { Conversation } from "@/types/conversation";
import { agentLabel } from "@/lib/conversation-utils";
import { ConversationHeader } from "./conversation-header";
import { ConversationInput } from "./conversation-input";
import { HandoffCard } from "./handoff-card";
import { MessageBubble } from "./message-bubble";
import { TypingIndicator } from "./typing-indicator";

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
  if (!conversation) {
    return (
      <div className="flex h-full flex-col items-center justify-center border-r border-border bg-background px-6 text-center">
        <p className="text-[13px] text-ink">Nenhuma conversa selecionada</p>
        <p className="mt-1 max-w-xs text-[12px] text-ink-soft">
          Selecione uma conversa para acompanhar a operação.
        </p>
      </div>
    );
  }

  const isClosed = conversation.status === "closed";
  const showHandoff =
    conversation.handoff &&
    !conversation.handoff.dismissed &&
    conversation.status === "needs_attention";

  const typingLabel =
    conversation.isTyping === "ai"
      ? `${agentLabel(
          conversation.currentOwner === "human"
            ? "sdr"
            : conversation.currentOwner,
        )} respondendo…`
      : conversation.isTyping === "lead"
        ? "Lead digitando…"
        : null;

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col border-r border-border bg-background">
      <ConversationHeader
        conversation={conversation}
        onBack={onBack}
        onAssume={onAssume}
        onReturnToAi={onReturnToAi}
        onResolve={onResolve}
        onAddNote={onAddNote}
        onOpenLead={onOpenLead}
      />

      {showHandoff && conversation.handoff && (
        <HandoffCard
          handoff={conversation.handoff}
          onAssume={onAssume}
          onDismiss={onDismissHandoff}
        />
      )}

      <div className="min-h-0 flex-1 overflow-y-auto">
        {conversation.messages.length === 0 ? (
          <div className="flex h-full items-center justify-center px-6">
            <p className="text-[12px] text-ink-soft">
              Nenhuma mensagem. Aguardando atividade.
            </p>
          </div>
        ) : (
          conversation.messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))
        )}
        {typingLabel && <TypingIndicator label={typingLabel} />}
      </div>

      <ConversationInput
        onSend={onSend}
        disabled={isClosed}
        placeholder={
          isClosed
            ? "Conversa resolvida"
            : conversation.currentOwner === "human"
              ? "Escrever como humano…"
              : "Assuma para enviar, ou aguarde a IA"
        }
      />
    </div>
  );
}
