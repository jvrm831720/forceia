"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Paperclip, Send, Smile } from "lucide-react";
import { useState } from "react";

export function ConversationInput({
  disabled,
  placeholder = "Escreva uma mensagem\u2026",
  onSend,
}: {
  disabled?: boolean;
  placeholder?: string;
  onSend: (text: string) => void;
}) {
  const [value, setValue] = useState("");

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  }

  return (
    <div className="border-t border-border bg-surface-card p-3 sm:p-4">
      <div
        className={cn(
          "flex items-end gap-2 rounded-2xl border border-border bg-white p-2 shadow-card",
          disabled && "opacity-60"
        )}
      >
        <button
          type="button"
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-ink-soft transition hover:bg-border-soft hover:text-ink disabled:pointer-events-none"
          aria-label="Anexar arquivo"
          disabled={disabled}
        >
          <Paperclip className="h-4 w-4" strokeWidth={1.75} />
        </button>
        <button
          type="button"
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-ink-soft transition hover:bg-border-soft hover:text-ink disabled:pointer-events-none"
          aria-label="Inserir emoji"
          disabled={disabled}
        >
          <Smile className="h-4 w-4" strokeWidth={1.75} />
        </button>
        <label className="min-w-0 flex-1">
          <span className="sr-only">Mensagem</span>
          <textarea
            rows={1}
            value={value}
            disabled={disabled}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            placeholder={placeholder}
            className="max-h-28 w-full resize-none bg-transparent py-2 text-sm text-ink placeholder:text-ink-soft focus:outline-none disabled:cursor-not-allowed"
          />
        </label>
        <Button
          type="button"
          size="sm"
          disabled={disabled || !value.trim()}
          onClick={submit}
          aria-label="Enviar mensagem"
        >
          <Send className="h-3.5 w-3.5" />
          Enviar
        </Button>
      </div>
      <p className="mt-2 px-1 text-[11px] text-ink-soft">
        Enter envia \u00b7 Shift+Enter nova linha
      </p>
    </div>
  );
}
