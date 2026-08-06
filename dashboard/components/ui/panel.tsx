import { cn } from "@/lib/utils";

/**
 * Unified surface language.
 * One outer border · internal dividers · shared header chrome.
 */
export function Panel({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        "flex flex-col overflow-hidden border border-border bg-canvas",
        className,
      )}
    >
      {children}
    </section>
  );
}

export function PanelHeader({
  title,
  meta,
  className,
}: {
  title: string;
  meta?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex h-9 shrink-0 items-center justify-between gap-3 border-b border-border px-3",
        className,
      )}
    >
      <h2 className="text-section text-ink">{title}</h2>
      {meta != null && (
        <div className="flex shrink-0 items-center gap-2 text-meta text-ink-soft">
          {meta}
        </div>
      )}
    </div>
  );
}

export function PanelBody({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={cn("min-h-0 flex-1", className)}>{children}</div>;
}

export function PanelRow({
  children,
  className,
  as: Comp = "div",
}: {
  children: React.ReactNode;
  className?: string;
  as?: "div" | "li" | "a";
}) {
  return (
    <Comp
      className={cn(
        "flex items-start gap-2.5 px-3 py-2 transition-ui duration-fast hover:bg-surface",
        className,
      )}
    >
      {children}
    </Comp>
  );
}
