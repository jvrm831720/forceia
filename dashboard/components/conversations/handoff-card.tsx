"use client";

import { Button } from "@/components/ui/button";
import type { HandoffRequest } from "@/types/conversation";

/** Interrupt lane — Product Language: "Precisa de você" */
export function HandoffCard({
  handoff,
  onAssume,
  onDismiss,
}: {
  handoff: HandoffRequest;
  onAssume: () => void;
  onDismiss: () => void;
}) {
  return (
    <div
      className="mx-3 mt-3 border border-warning/40 bg-canvas"
      role="region"
      aria-label="Handoff — precisa de você"
    >
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-warning" aria-hidden />
          <p className="text-section text-ink">Precisa de você</p>
        </div>
        <span className="text-mono text-warning">HO</span>
      </div>
      <div className="space-y-2 px-3 py-2.5">
        <p className="text-body text-ink">{handoff.reason}</p>
        <p className="text-meta text-ink-soft">
          Solicitado às{" "}
          <span className="text-mono">
            {new Date(handoff.requestedAt).toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </p>
        <div className="flex flex-wrap gap-2 pt-1">
          <Button type="button" size="sm" variant="secondary" onClick={onAssume}>
            Assumir
          </Button>
          <Button type="button" size="sm" variant="ghost" onClick={onDismiss}>
            Manter com a IA
          </Button>
        </div>
      </div>
    </div>
  );
}
