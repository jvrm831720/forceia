"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useState } from "react";

/** Discrete composer — send only elevates when content is valid. */
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
  const [sending, setSending] = useState(false);
  const hasContent = value.trim().length > 0;

  const submit = () => {
    const text = value.trim();
    if (!text || disabled || sending) return;
    setSending(true);
    onSend(text);
    setValue("");
    setSending(false);
  };

  return (
    <div className="shrink-0 border-t border-border bg-background px-3 py-2">
      <div
        className={cn(
          "flex items-end gap-2 rounded-sm bg-surface/50 px-2.5 py-1.5 transition-colors duration-100",
          "focus-within:bg-surface focus-within:ring-1 focus-within:ring-brand/30",
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
          rows={1}
          disabled={disabled || sending}
          placeholder={placeholder}
          className="min-h-[28px] max-h-24 flex-1 resize-none border-0 bg-transparent py-1 text-[13px] leading-5 text-ink placeholder:text-ink-soft focus:outline-none focus:ring-0 disabled:cursor-not-allowed"
        />
        <Button
          type="button"
          size="sm"
          variant={hasContent && !disabled ? "secondary" : "ghost"}
          disabled={disabled || !hasContent || sending}
          onClick={submit}
          className={cn(
            "h-7 shrink-0 px-2.5 text-[12px]",
            hasContent && !disabled && "text-ink",
          )}
        >
          {sending ? "…" : "Enviar"}
        </Button>
      </div>
      <p className="mt-1 px-0.5 text-[10px] leading-3 text-ink-soft">
        Enter para enviar · Shift+Enter para nova linha
      </p>
    </div>
  );
}
