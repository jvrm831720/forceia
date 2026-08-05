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
        "flex items-end gap-2",
        align === "right" ? "justify-end" : "justify-start"
      )}
      aria-live="polite"
      aria-label={label}
    >
      <div className="rounded-2xl border border-border bg-white px-3.5 py-2.5 shadow-card">
        <div className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-soft [animation-delay:0ms]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-soft [animation-delay:150ms]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-soft [animation-delay:300ms]" />
        </div>
      </div>
      <span className="text-[11px] text-ink-soft">{label}</span>
    </div>
  );
}
