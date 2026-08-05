import { cn } from "@/lib/utils";
import * as React from "react";
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", ...props }, ref) => (
    <input ref={ref} type={type} className={cn(
      "flex h-9 w-full rounded-md border border-border bg-surface px-3 text-sm text-ink placeholder:text-ink-soft transition-ui focus:border-brand focus:outline-none focus:shadow-focus disabled:cursor-not-allowed disabled:opacity-50",
      className,
    )} {...props} />
  ),
);
Input.displayName = "Input";
