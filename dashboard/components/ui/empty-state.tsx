import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
interface EmptyStateProps { icon?: LucideIcon; title: string; description?: string; className?: string; }
export function EmptyState({ icon: Icon, title, description, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center px-6 py-16 text-center", className)}>
      {Icon && <Icon className="mb-3 h-8 w-8 text-ink-soft" strokeWidth={1.5} />}
      <h3 className="font-display text-base font-semibold text-ink">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-ink-muted">{description}</p>}
    </div>
  );
}
