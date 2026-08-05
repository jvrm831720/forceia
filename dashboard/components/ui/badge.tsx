import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-sm px-1.5 py-0.5 text-[10px] font-medium leading-none tracking-wide",
  {
    variants: {
      variant: {
        default: "bg-elevated text-ink-muted border border-border",
        success: "bg-success-soft text-success",
        ai: "bg-ai-soft text-ai",
        warning: "bg-warning-soft text-warning",
        danger: "bg-danger-soft text-danger",
        muted: "bg-surface text-ink-soft border border-border",
        outline: "border border-border text-ink-muted bg-transparent",
        soft: "bg-brand-soft text-brand",
        secondary: "bg-elevated text-ink-muted border border-border",
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
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
export { badgeVariants };
