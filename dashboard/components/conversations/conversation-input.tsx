"use client";

import { Button } from "@/components/ui/button";
import { Icon } from "@/components/ui/icon";
import { Send } from "lucide-react";
import { useState } from "react";

export function ConversationInput({
  onSend,
  disabled,
  placeholder = "Escrever mensagem…",
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
    <div className="border-t border-border bg-canvas px-3 py-2.5">
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
          className="min-h-[40px] flex-1 resize-none rounded-md border border-border bg-surface px-2.5 py-2 text-body text-ink placeholder:text-ink-soft transition-ui duration-fast focus:border-brand focus:outline-none focus:shadow-focus disabled:opacity-50"
        />
        <Button
          type="button"
          size="sm"
          variant="secondary"
          disabled={disabled || !value.trim()}
          onClick={submit}
          aria-label="Enviar mensagem"
        >
          <Icon icon={Send} size="sm" />
          Enviar
        </Button>
      </div>
      <p className="mt-1.5 text-meta text-ink-soft">
        Enter envia · Shift+Enter nova linha
      </p>
    </div>
  );
}
