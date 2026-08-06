"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Icon } from "@/components/ui/icon";
import {
  agentBadgeVariant,
  agentLabel,
  channelLabel,
  statusCode,
  statusLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";
import {
  ArrowLeft,
  Bot,
  CheckCircle2,
  ExternalLink,
  StickyNote,
  UserCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

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
  const isClosed = conversation.status === "closed";
  const isHuman = conversation.currentOwner === "human";
  const needsYou = conversation.status === "needs_attention";
  const code = statusCode(conversation.status);

  return (
    <header className="flex h-11 shrink-0 items-center justify-between gap-2 border-b border-border bg-canvas px-2 sm:px-3">
      <div className="flex min-w-0 items-center gap-2">
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md text-ink-soft transition-ui duration-fast hover:bg-surface hover:text-ink md:hidden"
            aria-label="Voltar para lista"
          >
            <Icon icon={ArrowLeft} size="sm" />
          </button>
        )}
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-1.5">
            <p className="truncate text-section text-ink">
              {conversation.leadName}
            </p>
            <span
              className={cn(
                "text-mono font-medium",
                needsYou ? "text-warning" : "text-brand",
              )}
            >
              {code}
            </span>
            <Badge
              variant={agentBadgeVariant(conversation.currentOwner)}
              className="hidden sm:inline-flex"
            >
              {agentLabel(conversation.currentOwner)}
            </Badge>
          </div>
          <p className="truncate text-meta text-ink-soft">
            {conversation.company} · {channelLabel(conversation.channel)} ·{" "}
            {statusLabel(conversation.status)}
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        {!isClosed && (
          <>
            {isHuman ? (
              <Button
                size="sm"
                variant="soft"
                onClick={onReturnToAi}
                className="hidden sm:inline-flex"
              >
                <Icon icon={Bot} size="sm" />
                Devolver para IA
              </Button>
            ) : (
              <Button
                size="sm"
                variant="secondary"
                onClick={onAssume}
                className="hidden sm:inline-flex"
              >
                <Icon icon={UserCheck} size="sm" />
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
              <Icon icon={StickyNote} size="sm" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={onResolve}
              aria-label="Marcar como resolvida"
              className="hidden md:inline-flex"
            >
              <Icon icon={CheckCircle2} size="sm" />
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="ghost"
          onClick={onOpenLead}
          aria-label="Abrir lead"
        >
          <Icon icon={ExternalLink} size="sm" />
        </Button>
      </div>
    </header>
  );
}
