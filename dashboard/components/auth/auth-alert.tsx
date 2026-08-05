import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2, Info } from "lucide-react";

const VARIANTS = {
  error: {
    wrap: "border-warning/30 bg-warning-soft text-warning",
    Icon: AlertCircle,
  },
  success: {
    wrap: "border-success/30 bg-success-soft text-success",
    Icon: CheckCircle2,
  },
  info: {
    wrap: "border-border bg-surface text-ink-muted",
    Icon: Info,
  },
} as const;

export function AuthAlert({
  variant = "info",
  children,
  className,
}: {
  variant?: keyof typeof VARIANTS;
  children: React.ReactNode;
  className?: string;
}) {
  const { wrap, Icon } = VARIANTS[variant];
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-2 rounded-md border px-3 py-2.5 text-[12px] leading-relaxed",
        wrap,
        className,
      )}
    >
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" strokeWidth={1.75} aria-hidden />
      <div>{children}</div>
    </div>
  );
}
