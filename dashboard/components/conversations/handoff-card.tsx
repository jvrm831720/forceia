"use client";

import { Button } from "@/components/ui/button";
import type { ConversationHandoff } from "@/types/conversation";
import { AlertTriangle } from "lucide-react";

export function HandoffCard({
  handoff,
  onAssume,
  onDismiss,
}: {
  handoff: ConversationHandoff;
  onAssume: () => void;
  onDismiss: () => void;
}) {
  if (!handoff.requested) return null;

  return (
    <div
      className="mx-4 mt-3 rounded-2xl border border-alert/25 bg-alert-soft p-4 shadow-card"
      role="status"
      aria-live="polite"
    >
      <div className="flex gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-alert shadow-card">
          <AlertTriangle className="h-5 w-5" strokeWidth={1.75} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-display text-sm font-semibold text-ink">
            A IA solicitou sua interven\u00e7\u00e3o
          </p>
          <p className="mt-1 text-sm text-ink-muted">
            <span className="font-medium text-ink">Motivo:</span> {handoff.reason}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button type="button" size="sm" onClick={onAssume}>
              Assumir conversa
            </Button>
            <Button type="button" size="sm" variant="secondary" onClick={onDismiss}>
              Ignorar
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
