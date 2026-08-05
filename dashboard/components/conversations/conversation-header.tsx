"use client";

import {
  ArrowLeft,
  MoreHorizontal,
  StickyNote,
  UserCheck,
  Bot,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  agentBadgeVariant,
  agentLabel,
  channelLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";

export function ConversationHeader({
  conversation,
  onBack,
  onAssume,
  onReturnToAi,
  onResolve,
  onAddNote,
  onOpenLead,
}: {
  conversation: Conversation;
  onBack?: () => void;
  onAssume: () => void;
  onReturnToAi: () => void;
  onResolve: () => void;
  onAddNote: () => void;
  onOpenLead: () => void;
}) {
  const isHuman = conversation.currentOwner === "human";
  const isClosed = conversation.status === "closed";

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-border bg-surface-card px-3 sm:px-4">
      {onBack && (
        <button
          type="button"
          onClick={onBack}
          className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-white text-ink-muted lg:hidden"
          aria-label="Voltar para lista"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
      )}

      <div className="flex min-w-0 flex-1 items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-border-soft font-display text-xs font-bold text-ink-muted">
          {conversation.avatarInitials}
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-semibold text-ink">
              {conversation.leadName}
            </p>
            <Badge
              variant={agentBadgeVariant(conversation.currentOwner)}
              className="!py-0 !text-[10px] hidden sm:inline-flex"
            >
              {agentLabel(conversation.currentOwner)}
            </Badge>
          </div>
          <p className="truncate text-[12px] text-ink-soft">
            {conversation.company} · {channelLabel(conversation.channel)}
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        {!isClosed && (
          <>
            {isHuman ? (
              <Button
                size="sm"
                variant="soft"
                onClick={onReturnToAi}
                className="hidden sm:inline-flex"
              >
                <Bot className="h-3.5 w-3.5" />
                Devolver para IA
              </Button>
            ) : (
              <Button
                size="sm"
                variant="secondary"
                onClick={onAssume}
                className="hidden sm:inline-flex"
              >
                <UserCheck className="h-3.5 w-3.5" />
                Assumir
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={onAddNote}
              aria-label="Adicionar nota"
              className="hidden md:inline-flex"
            >
              <StickyNote className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={onResolve}
              aria-label="Marcar como resolvida"
              className="hidden md:inline-flex"
            >
              <CheckCircle2 className="h-4 w-4" />
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="ghost"
          onClick={onOpenLead}
          aria-label="Abrir lead"
        >
          <ExternalLink className="h-4 w-4" />
        </Button>
        <Button size="sm" variant="ghost" aria-label="Mais opções">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
