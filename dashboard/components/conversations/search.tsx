"use client";

import { Search } from "lucide-react";

export function ConversationSearch({
  value,
  onChange,
}: {
  value: string;
  onChange: (q: string) => void;
}) {
  return (
    <label className="relative block">
      <Search
        className="pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-soft"
        strokeWidth={1.75}
        aria-hidden
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar…"
        className="h-7 w-full border-0 border-b border-border bg-transparent pl-7 pr-2 text-[13px] text-ink placeholder:text-ink-soft focus:border-ink-muted focus:outline-none"
      />
    </label>
  );
}
