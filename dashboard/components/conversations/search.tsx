"use client";

import { Search } from "lucide-react";

/** Midday-style compact search field. */
export function ConversationSearch({
  value,
  onChange,
}: {
  value: string;
  onChange: (q: string) => void;
}) {
  return (
    <label className="relative block w-[200px] shrink-0">
      <Search
        className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-soft"
        strokeWidth={1.75}
        aria-hidden
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar…"
        className="h-8 w-full border border-border bg-transparent pl-8 pr-2.5 text-sm text-ink placeholder:text-ink-soft focus:border-ink-muted focus:outline-none"
      />
    </label>
  );
}
