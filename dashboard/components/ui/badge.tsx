import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-sm border border-transparent px-1.5 py-0.5 text-badge leading-none",
  {
    variants: {
      variant: {
        default: "border-border bg-elevated text-ink-muted",
        success: "bg-success-soft text-success",
        ai: "bg-ai-soft text-ai",
        warning: "bg-warning-soft text-warning",
        danger: "bg-danger-soft text-danger",
        muted: "border-border bg-surface text-ink-soft",
        outline: "border-border bg-transparent text-ink-muted",
        soft: "bg-brand-soft text-brand",
        secondary: "border-border bg-elevated text-ink-muted",
        alert: "bg-warning-soft text-warning",
        highlight: "bg-highlight-soft text-highlight",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
export { badgeVariants };
