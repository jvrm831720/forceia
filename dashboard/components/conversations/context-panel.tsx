"use client";

import { Button } from "@/components/ui/button";
import {
  agentLabel,
  statusLabel,
  temperatureLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 border-b border-border px-4 py-3">
      <span className="text-[10px] font-medium uppercase tracking-wide text-ink-soft">
        {label}
      </span>
      {children}
    </div>
  );
}

/** Midday secondary column — stacked meta rows. ForceIA decision content. */
export function ContextPanel({
  conversation,
  onClose,
}: {
  conversation: Conversation | null;
  onClose?: () => void;
}) {
  if (!conversation) {
    return (
      <aside className="hidden h-full w-[280px] shrink-0 flex-col border-l border-border xl:flex">
        <div className="flex h-10 items-center border-b border-border px-4">
          <span className="text-sm font-medium text-ink">Decisão</span>
        </div>
        <div className="flex flex-1 items-center justify-center px-4 text-center">
          <p className="text-xs text-ink-soft">Selecione uma conversa.</p>
        </div>
      </aside>
    );
  }

  const opp = conversation.opportunity;
  const needsYou = conversation.status === "needs_attention";

  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-l border-border",
        "xl:w-[280px] xl:shrink-0",
      )}
    >
      <div className="flex h-10 items-center justify-between border-b border-border px-4">
        <span className="text-sm font-medium text-ink">Decisão</span>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center text-ink-soft hover:text-ink xl:hidden"
            aria-label="Fechar"
          >
            <X className="h-4 w-4" strokeWidth={1.75} />
          </button>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <Row label="Operador">
          <p className="text-sm font-medium text-ink">
            {agentLabel(opp.currentOwner)}
          </p>
        </Row>

        <Row label="Status">
          <p
            className={cn(
              "text-sm",
              needsYou ? "font-medium text-warning" : "text-ink",
            )}
          >
            {statusLabel(conversation.status)}
          </p>
          <p className="text-xs text-ink-soft">{opp.lastActivity}</p>
        </Row>

        <Row label="Próxima decisão">
          <p className="text-sm leading-relaxed text-ink">{opp.nextAction}</p>
        </Row>

        <Row label="Recomendação da IA">
          <p className="text-xs leading-relaxed text-ink-muted">{opp.aiSummary}</p>
        </Row>

        <Row label="Objetivo">
          <p className="text-sm text-ink">{opp.pipelineStage}</p>
          <p className="text-xs text-ink-soft">
            {temperatureLabel(opp.temperature)}
          </p>
        </Row>

        <Row label="Sinais">
          <div className="flex flex-wrap gap-2">
            {opp.source && (
              <span className="font-mono text-xs text-ink-soft">{opp.source}</span>
            )}
            <span className="font-mono text-xs text-ink-soft">
              {temperatureLabel(opp.temperature)}
            </span>
          </div>
        </Row>

        <Row label="Timeline">
          <ol className="space-y-2">
            {opp.timeline.map((event) => (
              <li key={event.id} className="flex gap-2">
                <span
                  className={cn(
                    "mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full",
                    event.done ? "bg-success" : "bg-border",
                  )}
                  aria-hidden
                />
                <div className="min-w-0">
                  <p
                    className={cn(
                      "text-xs",
                      event.done ? "text-ink" : "text-ink-soft",
                    )}
                  >
                    {event.label}
                  </p>
                  <p className="font-mono text-[10px] text-ink-soft">
                    {event.timestamp}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </Row>

        <Row label="Dados do lead">
          <p className="text-sm text-ink">{opp.leadName}</p>
          <p className="text-xs text-ink-soft">{opp.company}</p>
          {opp.phone && (
            <p className="mt-1 font-mono text-xs text-ink-soft">{opp.phone}</p>
          )}
          {opp.email && (
            <p className="font-mono text-xs text-ink-soft">{opp.email}</p>
          )}
        </Row>

        {opp.meeting && (
          <Row label="Reunião">
            <p className="text-sm text-ink">{opp.meeting.title || "Reunião"}</p>
            <p className="font-mono text-xs text-ink-soft">
              {opp.meeting.date} · {opp.meeting.time}
            </p>
          </Row>
        )}
      </div>

      <div className="border-t border-border p-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-full justify-start text-xs"
        >
          Abrir lead
        </Button>
      </div>
    </aside>
  );
}
