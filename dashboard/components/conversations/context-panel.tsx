"use client";

import { Button } from "@/components/ui/button";
import { agentLabel, statusLabel } from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

function Block({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <section className="border-b border-border px-3 py-2.5">
      <p className="mb-1 text-[10px] font-medium uppercase tracking-[0.08em] text-ink-soft">
        {label}
      </p>
      {children}
    </section>
  );
}

export function ContextPanel({
  conversation,
  onClose,
}: {
  conversation: Conversation | null;
  onClose?: () => void;
}) {
  if (!conversation) {
    return (
      <aside className="hidden h-full w-[280px] shrink-0 flex-col border-l border-border bg-background xl:flex">
        <div className="flex h-10 items-center border-b border-border px-3">
          <span className="text-[13px] font-medium text-ink">Contexto</span>
        </div>
        <div className="flex flex-1 items-center justify-center px-4 text-center">
          <p className="text-[12px] text-ink-soft">Selecione uma conversa.</p>
        </div>
      </aside>
    );
  }

  const opp = conversation.opportunity;

  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-l border-border bg-background",
        "xl:w-[280px] xl:shrink-0",
      )}
    >
      <div className="flex h-10 items-center justify-between border-b border-border px-3">
        <span className="text-[13px] font-medium text-ink">Contexto</span>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-7 w-7 items-center justify-center text-ink-soft hover:text-ink xl:hidden"
            aria-label="Fechar"
          >
            <X className="h-3.5 w-3.5" strokeWidth={1.75} />
          </button>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <Block label="Operador">
          <p className="text-[13px] text-ink">{agentLabel(opp.currentOwner)}</p>
          <p className="mt-0.5 text-[12px] text-ink-soft">
            {statusLabel(conversation.status)}
          </p>
        </Block>

        <Block label="Próxima decisão">
          <p className="text-[13px] leading-5 text-ink">{opp.nextAction}</p>
        </Block>

        <Block label="Resumo IA">
          <p className="text-[12px] leading-5 text-ink-muted">{opp.aiSummary}</p>
        </Block>

        <Block label="Objetivo">
          <p className="text-[13px] text-ink">{opp.pipelineStage}</p>
          <p className="mt-0.5 text-[12px] capitalize text-ink-soft">
            {opp.temperature}
          </p>
        </Block>

        <Block label="Lead">
          <p className="text-[13px] text-ink">{opp.leadName}</p>
          <p className="text-[12px] text-ink-soft">{opp.company}</p>
          {opp.phone && (
            <p className="mt-1 text-mono text-ink-soft">{opp.phone}</p>
          )}
          {opp.email && <p className="text-mono text-ink-soft">{opp.email}</p>}
        </Block>

        {opp.meeting && (
          <Block label="Reunião">
            <p className="text-[13px] text-ink">
              {opp.meeting.title || "Reunião"}
            </p>
            <p className="text-mono text-ink-soft">
              {opp.meeting.date} · {opp.meeting.time}
            </p>
          </Block>
        )}

        <Block label="Timeline">
          <ol className="space-y-2">
            {opp.timeline.map((event) => (
              <li key={event.id} className="flex gap-2">
                <span
                  className={cn(
                    "mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full",
                    event.done ? "bg-success" : "bg-border",
                  )}
                />
                <div className="min-w-0">
                  <p
                    className={cn(
                      "text-[12px] leading-4",
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
        </Block>
      </div>

      <div className="border-t border-border p-2">
        <Button variant="ghost" size="sm" className="h-7 w-full justify-start">
          Abrir lead
        </Button>
      </div>
    </aside>
  );
}
