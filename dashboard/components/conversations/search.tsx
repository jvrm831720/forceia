"use client";

import { Search as SearchIcon } from "lucide-react";

export function ConversationSearch({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="relative block">
      <span className="sr-only">Pesquisar conversa</span>
      <SearchIcon
        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-soft"
        aria-hidden
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Pesquisar nome, empresa\u2026"
        className="h-10 w-full rounded-xl border border-border bg-white pl-10 pr-3 text-sm text-ink placeholder:text-ink-soft shadow-card transition focus:border-brand focus:outline-none focus:shadow-focus"
      />
    </label>
  );
}
