import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "success" | "alert" | "ai" | "muted" | "highlight";

const variants: Record<BadgeVariant, string> = {
  default: "bg-brand-soft text-brand border-transparent",
  success: "bg-success-soft text-success border-transparent",
  alert: "bg-alert-soft text-alert border-transparent",
  ai: "bg-ai-soft text-ai border-transparent",
  muted: "bg-border-soft text-ink-muted border-border",
  highlight: "bg-highlight-soft text-ink border-transparent",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold tracking-wide",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
