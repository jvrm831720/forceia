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
          "h-9 w-full rounded-md border border-border bg-surface px-3 pr-10 text-[13px] text-ink placeholder:text-ink-soft",
          "transition-ui duration-fast",
          "hover:border-[#2b2b2b]",
          "focus:border-brand focus:outline-none focus:shadow-focus",
          "disabled:cursor-not-allowed disabled:opacity-50",
          ariaInvalid &&
            "border-warning focus:border-warning focus:shadow-[0_0_0_2px_rgba(221,101,57,0.25)]",
        )}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        disabled={disabled}
        className={cn(
          "absolute right-1.5 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-sm",
          "text-ink-soft transition-ui duration-fast",
          "hover:bg-surface-hover hover:text-ink",
          "active:scale-95 active:opacity-80",
          "focus-visible:outline-none focus-visible:shadow-focus",
          "disabled:opacity-50",
        )}
        aria-label={visible ? "Ocultar senha" : "Mostrar senha"}
      >
        {visible ? (
          <EyeOff className="h-3.5 w-3.5" aria-hidden />
        ) : (
          <Eye className="h-3.5 w-3.5" aria-hidden />
        )}
      </button>
    </div>
  );
}
