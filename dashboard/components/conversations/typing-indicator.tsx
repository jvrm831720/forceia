import { cn } from "@/lib/utils";

export function TypingIndicator({
  label,
  align = "left",
}: {
  label: string;
  align?: "left" | "right";
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-1",
        align === "right" ? "justify-end" : "justify-start",
      )}
      aria-live="polite"
      aria-label={label}
    >
      <div className="flex items-center gap-1.5 border border-border bg-surface px-2.5 py-1.5">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand opacity-50" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand" />
        </span>
        <span className="text-meta text-ink-muted">{label}</span>
      </div>
    </div>
  );
}
