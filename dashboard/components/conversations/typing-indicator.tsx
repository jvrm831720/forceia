export function TypingIndicator({ label }: { label: string }) {
  return (
    <div
      className="border-b border-border px-4 py-3"
      aria-live="polite"
      aria-label={label}
    >
      <div className="flex items-center gap-2">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand opacity-40" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand" />
        </span>
        <span className="text-xs text-ink-soft">{label}</span>
      </div>
    </div>
  );
}
