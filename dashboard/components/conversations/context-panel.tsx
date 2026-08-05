"use client";

import {
  Building2,
  Calendar,
  ExternalLink,
  Mail,
  Phone,
  Thermometer,
  User,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  agentBadgeVariant,
  agentLabel,
  temperatureLabel,
} from "@/lib/conversation-utils";
import type { Conversation } from "@/types/conversation";
import { cn } from "@/lib/utils";

export function ContextPanel({
  conversation,
  onClose,
}: {
  conversation: Conversation | null;
  onClose?: () => void;
}) {
  if (!conversation) {
    return (
      <aside className="hidden h-full w-[300px] shrink-0 flex-col border-l border-border bg-surface-card xl:flex">
        <div className="flex flex-1 items-center justify-center p-6 text-center">
          <p className="text-[13px] text-ink-soft">
            Selecione uma conversa para ver o resumo da oportunidade.
          </p>
        </div>
      </aside>
    );
  }

  const { opportunity: opp } = conversation;

  return (
    <aside className="flex h-full w-full flex-col border-l border-border bg-surface-card xl:w-[300px] xl:shrink-0">
      <div className="flex h-16 items-center justify-between border-b border-border px-4">
        <h2 className="font-display text-[15px] font-semibold tracking-tight text-ink">
          Resumo da Oportunidade
        </h2>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-ink-soft hover:bg-border-soft xl:hidden"
            aria-label="Fechar painel"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-5">
          <section className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-border-soft font-display text-sm font-bold text-ink-muted">
                {conversation.avatarInitials}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-ink">
                  {opp.leadName}
                </p>
                <p className="truncate text-[12px] text-ink-soft">{opp.company}</p>
              </div>
            </div>

            <div className="grid gap-2 text-[12.5px]">
              {opp.phone && (
                <div className="flex items-center gap-2 text-ink-muted">
                  <Phone className="h-3.5 w-3.5 shrink-0 text-ink-soft" />
                  <span className="truncate">{opp.phone}</span>
                </div>
              )}
              {opp.email && (
                <div className="flex items-center gap-2 text-ink-muted">
                  <Mail className="h-3.5 w-3.5 shrink-0 text-ink-soft" />
                  <span className="truncate">{opp.email}</span>
                </div>
              )}
              {opp.source && (
                <div className="flex items-center gap-2 text-ink-muted">
                  <Building2 className="h-3.5 w-3.5 shrink-0 text-ink-soft" />
                  <span>Origem: {opp.source}</span>
                </div>
              )}
            </div>
          </section>

          <section className="flex flex-wrap gap-1.5">
            <Badge
              variant={
                opp.temperature === "hot"
                  ? "alert"
                  : opp.temperature === "warm"
                    ? "highlight"
                    : "muted"
              }
            >
              <Thermometer className="h-3 w-3" />
              {temperatureLabel(opp.temperature)}
            </Badge>
            <Badge variant="default">{opp.pipelineStage}</Badge>
            <Badge variant={agentBadgeVariant(opp.currentOwner)}>
              <User className="h-3 w-3" />
              {agentLabel(opp.currentOwner)}
            </Badge>
          </section>

          <section>
            <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink-soft">
              Resumo da IA
            </h3>
            <p className="rounded-xl bg-ai-soft/60 p-3 text-[12.5px] leading-relaxed text-ink">
              {opp.aiSummary}
            </p>
          </section>

          <section>
            <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink-soft">
              Próxima ação
            </h3>
            <p className="text-[13px] font-medium text-ink">{opp.nextAction}</p>
            <p className="mt-0.5 text-[11px] text-ink-soft">
              Última atividade: {opp.lastActivity}
            </p>
          </section>

          {opp.meeting && (
            <section className="rounded-xl border border-border bg-white p-3 shadow-card">
              <div className="mb-2 flex items-center gap-2">
                <Calendar className="h-4 w-4 text-brand" />
                <h3 className="text-[12px] font-semibold text-ink">
                  {opp.meeting.title || "Reunião"}
                </h3>
              </div>
              <p className="text-[13px] text-ink">
                {opp.meeting.date} · {opp.meeting.time}
              </p>
              {opp.meeting.link && (
                <a
                  href={opp.meeting.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1 text-[12px] font-medium text-brand hover:underline"
                >
                  Abrir link
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </section>
          )}

          <section>
            <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-ink-soft">
              Linha do tempo
            </h3>
            <ol className="relative space-y-0">
              {opp.timeline.map((event, idx) => (
                <li key={event.id} className="relative flex gap-3 pb-4 last:pb-0">
                  {idx < opp.timeline.length - 1 && (
                    <span
                      className={cn(
                        "absolute left-[7px] top-4 h-full w-px",
                        event.done ? "bg-success/40" : "bg-border"
                      )}
                    />
                  )}
                  <span
                    className={cn(
                      "relative z-10 mt-0.5 h-3.5 w-3.5 shrink-0 rounded-full border-2",
                      event.done
                        ? "border-success bg-success"
                        : "border-border bg-white"
                    )}
                  />
                  <div className="min-w-0 pt-0">
                    <p
                      className={cn(
                        "text-[12.5px] font-medium",
                        event.done ? "text-ink" : "text-ink-soft"
                      )}
                    >
                      {event.label}
                    </p>
                    <p className="text-[11px] text-ink-soft">{event.timestamp}</p>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        </div>
      </div>

      <div className="border-t border-border p-3">
        <Button variant="secondary" size="sm" className="w-full">
          <ExternalLink className="h-3.5 w-3.5" />
          Abrir Lead
        </Button>
      </div>
    </aside>
  );
}
