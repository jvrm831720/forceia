"use client";

import { Button } from "@/components/ui/button";
import {
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
  const code = statusCode(conversation.status);

  return (
    <header className="flex h-10 shrink-0 items-center justify-between gap-2 border-b border-border bg-background px-2 sm:px-3">
      <div className="flex min-w-0 items-center gap-2">
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            className="inline-flex h-7 w-7 items-center justify-center text-ink-soft hover:text-ink md:hidden"
            aria-label="Voltar"
          >
            <ArrowLeft className="h-3.5 w-3.5" strokeWidth={1.75} />
          </button>
        )}
        <div className="min-w-0">
          <div className="flex items-baseline gap-2">
            <span className="truncate text-[13px] font-medium text-ink">
              {conversation.leadName}
            </span>
            <span
              className={cn(
                "text-mono",
                code === "HO" ? "text-warning" : "text-ink-soft",
              )}
            >
              {code}
            </span>
          </div>
          <p className="truncate text-[11px] text-ink-soft">
            {conversation.company} · {channelLabel(conversation.channel)} ·{" "}
            {agentLabel(conversation.currentOwner)} ·{" "}
            {statusLabel(conversation.status)}
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-0.5">
        {!isClosed && (
          <>
            {isHuman ? (
              <Button
                size="sm"
                variant="ghost"
                onClick={onReturnToAi}
                className="hidden h-7 sm:inline-flex"
              >
                <Bot className="h-3.5 w-3.5" strokeWidth={1.75} />
                Devolver
              </Button>
            ) : (
              <Button
                size="sm"
                variant="secondary"
                onClick={onAssume}
                className="hidden h-7 sm:inline-flex"
              >
                <UserCheck className="h-3.5 w-3.5" strokeWidth={1.75} />
                Assumir
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={onAddNote}
              aria-label="Nota"
              className="hidden h-7 w-7 p-0 md:inline-flex"
            >
              <StickyNote className="h-3.5 w-3.5" strokeWidth={1.75} />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={onResolve}
              aria-label="Resolver"
              className="hidden h-7 w-7 p-0 md:inline-flex"
            >
              <CheckCircle2 className="h-3.5 w-3.5" strokeWidth={1.75} />
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="ghost"
          onClick={onOpenLead}
          aria-label="Contexto"
          className="h-7 w-7 p-0"
        >
          <ExternalLink className="h-3.5 w-3.5" strokeWidth={1.75} />
        </Button>
      </div>
    </header>
  );
}
