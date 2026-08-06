import { cn } from "@/lib/utils";
import type { LucideIcon, LucideProps } from "lucide-react";

const SIZE = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 20,
} as const;

/**
 * Single icon language for ForceIA.
 * Always Lucide · stroke 1.75 · fixed size grid.
 */
export function Icon({
  icon: IconComp,
  size = "md",
  className,
  strokeWidth = 1.75,
  ...props
}: {
  icon: LucideIcon;
  size?: keyof typeof SIZE;
  className?: string;
  strokeWidth?: number;
} & Omit<LucideProps, "size" | "strokeWidth" | "ref">) {
  return (
    <IconComp
      size={SIZE[size]}
      strokeWidth={strokeWidth}
      className={cn("shrink-0", className)}
      aria-hidden={props["aria-label"] ? undefined : true}
      {...props}
    />
  );
}

export { SIZE as ICON_SIZE };
