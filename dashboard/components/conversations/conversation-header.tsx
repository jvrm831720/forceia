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
  CheckCircle2,
  ExternalLink,
  StickyNote,
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
    <header className="shrink-0 border-b border-border bg-background">
      <div className="flex h-9 items-center justify-between gap-2 px-2 sm:px-3">
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
              <span className="truncate text-[13px] font-medium leading-4 text-ink">
                {conversation.leadName}
              </span>
              <span
                className={cn(
                  "text-mono font-medium",
                  code === "HO" ? "text-warning" : "text-ink-soft",
                )}
              >
                {code}
              </span>
            </div>
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
                  className="hidden h-7 px-2 text-[12px] sm:inline-flex"
                >
                  Devolver para IA
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant={needsYou ? "secondary" : "ghost"}
                  onClick={onAssume}
                  className="hidden h-7 px-2 text-[12px] sm:inline-flex"
                >
                  Assumir
                </Button>
              )}
              <Button
                size="sm"
                variant="ghost"
                onClick={onResolve}
                className="hidden h-7 px-2 text-[12px] md:inline-flex"
              >
                Resolver
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onOpenLead}
                className="hidden h-7 px-2 text-[12px] lg:inline-flex"
              >
                Abrir lead
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onAddNote}
                aria-label="Nota interna"
                title="Nota interna"
                className="h-7 w-7 p-0"
              >
                <StickyNote className="h-3.5 w-3.5" strokeWidth={1.75} />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onResolve}
                aria-label="Resolver"
                title="Resolver"
                className="h-7 w-7 p-0 md:hidden"
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
            title="Contexto"
            className="h-7 w-7 p-0 xl:hidden"
          >
            <ExternalLink className="h-3.5 w-3.5" strokeWidth={1.75} />
          </Button>
        </div>
      </div>

      <div className="flex h-7 items-center gap-2 border-t border-border/60 px-3">
        <span className="truncate text-[11px] text-ink-soft">
          {conversation.company}
          <span className="text-ink-soft/50"> · </span>
          {channelLabel(conversation.channel)}
        </span>
        <span className="text-ink-soft/40">·</span>
        <span
          className={cn(
            "text-[11px]",
            needsYou ? "text-warning" : "text-ink-muted",
          )}
        >
          {agentLabel(conversation.currentOwner)}
          <span className="text-ink-soft/50"> · </span>
          {statusLabel(conversation.status)}
        </span>
      </div>
    </header>
  );
}
