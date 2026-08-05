"use client";

import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2 } from "lucide-react";

type AuthAlertVariant = "error" | "success" | "info";

const styles: Record<AuthAlertVariant, string> = {
  error: "bg-alert-soft text-alert border-alert/20",
  success: "bg-success-soft text-success border-success/20",
  info: "bg-brand-soft text-brand border-brand/20",
};

const icons = {
  error: AlertCircle,
  success: CheckCircle2,
  info: AlertCircle,
};

export function AuthAlert({
  children,
  variant = "error",
  className,
}: {
  children: React.ReactNode;
  variant?: AuthAlertVariant;
  className?: string;
}) {
  const Icon = icons[variant];

  return (
    <div
      role="alert"
      aria-live="polite"
      className={cn(
        "flex items-start gap-2.5 rounded-xl border px-3.5 py-3 text-[13px] leading-relaxed",
        styles[variant],
        className
      )}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <div className="min-w-0">{children}</div>
    </div>
  );
}
