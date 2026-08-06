"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Icon } from "@/components/ui/icon";
import {
  agentBadgeVariant,
  agentLabel,
  statusLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";
import { cn } from "@/lib/utils";
import { ExternalLink, X } from "lucide-react";

/**
 * Context — priority order (Product Language):
 * next action → AI summary → stage/owner → meeting → timeline
 */
export function ContextPanel({
  conversation,
  onClose,
}: {
  conversation: Conversation | null;
  onClose?: () => void;
}) {
  if (!conversation) {
    return (
      <aside className="hidden h-full w-[300px] shrink-0 flex-col border-l border-border bg-canvas xl:flex">
        <div className="flex h-11 items-center border-b border-border px-3">
          <h2 className="text-section text-ink">Contexto</h2>
        </div>
        <div className="flex flex-1 items-center justify-center px-4 text-center">
          <p className="text-body-muted text-ink-soft">
            Selecione uma conversa para ver o contexto operacional.
          </p>
        </div>
      </aside>
    );
  }

  const opp = conversation.opportunity;

  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-l border-border bg-canvas",
        "xl:w-[300px] xl:shrink-0",
      )}
    >
      <div className="flex h-11 items-center justify-between border-b border-border px-3">
        <h2 className="text-section text-ink">Contexto</h2>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md text-ink-soft transition-ui duration-fast hover:bg-surface xl:hidden"
            aria-label="Fechar contexto"
          >
            <Icon icon={X} size="sm" />
          </button>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <section className="border-b border-border px-3 py-3">
          <p className="text-label">Próxima ação</p>
          <p className="mt-1 text-body font-medium text-ink">{opp.nextAction}</p>
        </section>

        <section className="relative border-b border-border px-3 py-3">
          <div className="absolute inset-y-0 left-0 w-0.5 bg-brand" aria-hidden />
          <p className="text-label">Resumo da IA</p>
          <p className="mt-1 text-body-muted text-ink-muted">{opp.aiSummary}</p>
        </section>

        <section className="grid grid-cols-2 gap-3 border-b border-border px-3 py-3">
          <div>
            <p className="text-label">Estágio</p>
            <p className="mt-0.5 text-body text-ink">{opp.pipelineStage}</p>
          </div>
          <div>
            <p className="text-label">Temperatura</p>
            <p className="mt-0.5 text-body capitalize text-ink">{opp.temperature}</p>
          </div>
          <div>
            <p className="text-label">Responsável</p>
            <div className="mt-0.5">
              <Badge variant={agentBadgeVariant(opp.currentOwner)}>
                {agentLabel(opp.currentOwner)}
              </Badge>
            </div>
          </div>
          <div>
            <p className="text-label">Estado</p>
            <p className="mt-0.5 text-body text-ink">
              {statusLabel(conversation.status)}
            </p>
          </div>
        </section>

        <section className="border-b border-border px-3 py-3">
          <p className="text-label">Lead</p>
          <p className="mt-1 text-body font-medium text-ink">{opp.leadName}</p>
          <p className="text-meta text-ink-soft">{opp.company}</p>
          {opp.phone && <p className="mt-1 text-mono text-ink-muted">{opp.phone}</p>}
          {opp.email && <p className="text-mono text-ink-muted">{opp.email}</p>}
          {opp.source && (
            <p className="mt-1 text-meta text-ink-soft">Origem · {opp.source}</p>
          )}
        </section>

        {opp.meeting && (
          <section className="border-b border-border px-3 py-3">
            <p className="text-label">Reunião</p>
            <p className="mt-1 text-body text-ink">
              {opp.meeting.title || "Reunião"}
            </p>
            <p className="text-mono text-ink-muted">
              {opp.meeting.date} · {opp.meeting.time}
            </p>
            {opp.meeting.link && (
              <a
                href={opp.meeting.link}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 inline-flex items-center gap-1 text-meta text-brand transition-ui duration-fast hover:underline"
              >
                Abrir link
                <Icon icon={ExternalLink} size="xs" />
              </a>
            )}
          </section>
        )}

        <section className="px-3 py-3">
          <p className="mb-2 text-label">Linha do tempo</p>
          <ol>
            {opp.timeline.map((event, idx) => (
              <li key={event.id} className="relative flex gap-2.5 pb-3 last:pb-0">
                {idx < opp.timeline.length - 1 && (
                  <span
                    className={cn(
                      "absolute left-[5px] top-3 h-full w-px",
                      event.done ? "bg-success/40" : "bg-border",
                    )}
                  />
                )}
                <span
                  className={cn(
                    "relative z-10 mt-1 h-2.5 w-2.5 shrink-0 rounded-full",
                    event.done ? "bg-success" : "bg-elevated ring-1 ring-border",
                  )}
                />
                <div className="min-w-0">
                  <p
                    className={cn(
                      "text-body",
                      event.done ? "text-ink" : "text-ink-soft",
                    )}
                  >
                    {event.label}
                  </p>
                  <p className="text-mono text-ink-soft">{event.timestamp}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <div className="border-t border-border p-3">
        <Button variant="secondary" size="sm" className="w-full">
          <Icon icon={ExternalLink} size="sm" />
          Abrir lead
        </Button>
      </div>
    </aside>
  );
}
