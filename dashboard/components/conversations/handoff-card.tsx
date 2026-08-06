"use client";

import { Button } from "@/components/ui/button";
import type { HandoffRequest } from "@/types/conversation";

/** Compact operational interrupt lane. */
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
      className="relative border-b border-border bg-warning-soft/15 px-4 py-2.5"
      role="region"
      aria-label="Precisa de você"
    >
      <span
        className="absolute left-0 top-0 h-full w-0.5 bg-warning"
        aria-hidden
      />

      <div className="mb-1 flex items-center gap-2">
        <span className="text-[10px] font-medium uppercase tracking-[0.08em] text-warning">
          Precisa de você
        </span>
        <span className="text-mono font-medium text-warning">HO</span>
        <span className="ml-auto text-mono text-ink-soft">{time}</span>
      </div>

      <p className="text-[13px] leading-5 text-ink">{handoff.reason}</p>

      <div className="mt-2 flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={onAssume}
          className="h-7 px-2.5 text-[12px]"
        >
          Assumir
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={onDismiss}
          className="h-7 px-2.5 text-[12px]"
        >
          Manter com a IA
        </Button>
      </div>
    </div>
  );
}
