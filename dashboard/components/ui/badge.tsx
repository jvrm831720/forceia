import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-sm px-1.5 py-0.5 text-[11px] font-medium leading-none",
  {
    variants: {
      variant: {
        default: "bg-surface-strong text-ink-muted",
        success: "bg-success-soft text-success",
        ai: "bg-ai-soft text-ai",
        warning: "bg-warning-soft text-warning",
        danger: "bg-danger-soft text-danger",
        muted: "bg-surface-hover text-ink-soft",
        outline: "border border-border text-ink-muted bg-transparent",
        soft: "bg-brand-soft text-brand",
        secondary: "bg-surface-strong text-ink-muted",
        alert: "bg-warning-soft text-warning",
        highlight: "bg-highlight-soft text-ink",
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
