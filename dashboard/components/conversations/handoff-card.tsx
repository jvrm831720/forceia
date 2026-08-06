"use client";

import { Button } from "@/components/ui/button";
import type { HandoffRequest } from "@/types/conversation";

/** Midday detail alert strip — compact, bordered, action row. */
export function HandoffCard({
  handoff,
  onAssume,
  onDismiss,
}: {
  handoff: HandoffRequest;
  onAssume: () => void;
  onDismiss: () => void;
}) {
  const time = new Date(handoff.requestedAt).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className="border-b border-warning/40 bg-warning-soft/15 px-4 py-3"
      role="region"
      aria-label="Precisa de você"
    >
      <div className="mb-1 flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-warning">
          Precisa de você
        </span>
        <span className="font-mono text-xs font-medium text-warning">HO</span>
        <span className="ml-auto font-mono text-xs text-ink-soft">{time}</span>
      </div>
      <p className="text-sm text-ink">{handoff.reason}</p>
      <div className="mt-2.5 flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={onAssume}
          className="h-8 text-xs"
        >
          Assumir
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={onDismiss}
          className="h-8 text-xs"
        >
          Manter com a IA
        </Button>
      </div>
    </div>
  );
}
