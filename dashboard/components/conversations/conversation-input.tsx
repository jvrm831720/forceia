"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";

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

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  return (
    <div className="border-t border-border bg-background px-3 py-2">
      <div className="flex items-end gap-2">
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
          className="min-h-[36px] flex-1 resize-none border border-border bg-surface px-2.5 py-1.5 text-[13px] text-ink placeholder:text-ink-soft focus:border-ink-muted focus:outline-none disabled:opacity-40"
        />
        <Button
          type="button"
          size="sm"
          variant="secondary"
          disabled={disabled || !value.trim()}
          onClick={submit}
          className="h-8"
        >
          Enviar
        </Button>
      </div>
    </div>
  );
}
