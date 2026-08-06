"use client";

import { Search } from "lucide-react";
import { Icon } from "@/components/ui/icon";

export function ConversationSearch({
  value,
  onChange,
}: {
  value: string;
  onChange: (q: string) => void;
}) {
  return (
    <label className="relative block">
      <Icon
        icon={Search}
        size="sm"
        className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-ink-soft"
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar conversa…"
        className="h-8 w-full rounded-md border border-border bg-surface pl-8 pr-2.5 text-body text-ink placeholder:text-ink-soft transition-ui duration-fast focus:border-brand focus:outline-none focus:shadow-focus"
      />
    </label>
  );
}
