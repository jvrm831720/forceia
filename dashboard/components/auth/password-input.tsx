"use client";

import { cn } from "@/lib/utils";
import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";

export function PasswordInput({
  id = "password",
  name = "password",
  value,
  onChange,
  placeholder = "Sua senha",
  disabled,
  autoComplete = "current-password",
  "aria-invalid": ariaInvalid,
  "aria-describedby": ariaDescribedBy,
  className,
}: {
  id?: string;
  name?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  autoComplete?: string;
  "aria-invalid"?: boolean;
  "aria-describedby"?: string;
  className?: string;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <div className={cn("relative", className)}>
      <input
        id={id}
        name={name}
        type={visible ? "text" : "password"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        autoComplete={autoComplete}
        aria-invalid={ariaInvalid}
        aria-describedby={ariaDescribedBy}
        className={cn(
          "h-11 w-full rounded-xl border border-border bg-white px-3.5 pr-11 text-sm text-ink placeholder:text-ink-soft shadow-card transition",
          "focus:border-brand focus:outline-none focus:shadow-focus",
          "disabled:cursor-not-allowed disabled:opacity-60",
          ariaInvalid && "border-alert focus:border-alert focus:shadow-[0_0_0_3px_rgba(221,101,57,0.2)]"
        )}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        disabled={disabled}
        className="absolute right-2 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg text-ink-soft transition hover:bg-border-soft hover:text-ink focus-visible:outline-none focus-visible:shadow-focus disabled:opacity-50"
        aria-label={visible ? "Ocultar senha" : "Mostrar senha"}
      >
        {visible ? (
          <EyeOff className="h-4 w-4" aria-hidden />
        ) : (
          <Eye className="h-4 w-4" aria-hidden />
        )}
      </button>
    </div>
  );
}
