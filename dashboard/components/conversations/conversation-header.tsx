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
  MoreVertical,
  StickyNote,
} from "lucide-react";
import { cn } from "@/lib/utils";

/** Midday details header: action icons left, meta right. ForceIA content. */
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
    <div className="shrink-0 border-b border-border">
      <div className="flex items-center gap-2 p-2">
        {onBack && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            className="h-8 w-8 md:hidden"
            aria-label="Voltar"
          >
            <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
          </Button>
        )}

        {!isClosed && (
          <>
            {isHuman ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={onReturnToAi}
                className="hidden h-8 text-xs sm:inline-flex"
              >
                Devolver para IA
              </Button>
            ) : (
              <Button
                variant={needsYou ? "secondary" : "ghost"}
                size="sm"
                onClick={onAssume}
                className="hidden h-8 text-xs sm:inline-flex"
              >
                Assumir
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={onAddNote}
              className="h-8 w-8"
              aria-label="Nota"
              title="Nota interna"
            >
              <StickyNote className="h-4 w-4" strokeWidth={1.75} />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onResolve}
              className="h-8 w-8"
              aria-label="Resolver"
              title="Resolver"
            >
              <CheckCircle2 className="h-4 w-4" strokeWidth={1.75} />
            </Button>
          </>
        )}

        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onOpenLead}
            className="h-8 text-xs xl:hidden"
          >
            Decisão
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            aria-label="Mais"
          >
            <MoreVertical className="h-4 w-4" strokeWidth={1.75} />
          </Button>
        </div>
      </div>

      <div className="px-4 pb-3">
        <div className="flex items-baseline gap-2">
          <h2 className="truncate text-sm font-semibold text-ink">
            {conversation.leadName}
          </h2>
          <span
            className={cn(
              "font-mono text-xs font-medium",
              code === "HO" ? "text-warning" : "text-ink-soft",
            )}
          >
            {code}
          </span>
        </div>
        <p className="mt-0.5 text-xs text-ink-soft">
          {conversation.company}
          <span className="text-ink-soft/50"> · </span>
          {channelLabel(conversation.channel)}
          <span className="text-ink-soft/50"> · </span>
          <span className={needsYou ? "text-warning" : undefined}>
            {agentLabel(conversation.currentOwner)} ·{" "}
            {statusLabel(conversation.status)}
          </span>
        </p>
      </div>
    </div>
  );
}
