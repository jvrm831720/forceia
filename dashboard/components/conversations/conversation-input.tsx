"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useState } from "react";

/** Midday-style footer input inside detail panel. */
export function ConversationInput({
  onSend,
  disabled,
  placeholder = "Escrever…",
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  const [value, setValue] = useState("");
  const hasContent = value.trim().length > 0;

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  return (
    <div className="shrink-0 border-t border-border p-3">
      <div
        className={cn(
          "flex items-end gap-2 border border-border bg-surface/40 px-3 py-2",
          "focus-within:border-ink-muted",
          disabled && "opacity-40",
        )}
      >
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={2}
          disabled={disabled}
          placeholder={placeholder}
          className="min-h-[40px] max-h-28 flex-1 resize-none border-0 bg-transparent text-sm leading-5 text-ink placeholder:text-ink-soft focus:outline-none focus:ring-0 disabled:cursor-not-allowed"
        />
        <Button
          type="button"
          size="sm"
          variant={hasContent && !disabled ? "secondary" : "ghost"}
          disabled={disabled || !hasContent}
          onClick={submit}
          className="h-8 shrink-0 text-xs"
        >
          Enviar
        </Button>
      </div>
      <p className="mt-1.5 text-[10px] text-ink-soft">
        Enter para enviar · Shift+Enter para nova linha
      </p>
    </div>
  );
}
