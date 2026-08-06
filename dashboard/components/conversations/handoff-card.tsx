"use client";

import { Button } from "@/components/ui/button";
import type { HandoffRequest } from "@/types/conversation";

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
      className="border-b border-warning/50 bg-warning-soft/20 px-4 py-2.5"
      role="region"
      aria-label="Precisa de você"
    >
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="text-[12px] font-medium text-ink">Precisa de você</span>
        <span className="text-mono text-warning">HO</span>
      </div>
      <p className="text-[13px] leading-5 text-ink-muted">{handoff.reason}</p>
      <p className="mt-1 text-mono text-ink-soft">
        {new Date(handoff.requestedAt).toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </p>
      <div className="mt-2 flex gap-2">
        <Button type="button" size="sm" variant="secondary" onClick={onAssume}>
          Assumir
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={onDismiss}>
          Manter com a IA
        </Button>
      </div>
    </div>
  );
}
