"""ForceIA P2 — Registry formal de tools dos agentes (closer-first)."""

from __future__ import annotations

from tools.closer_registry import (
    CLOSER_TOOLS,
    execute_tool_calls_from_meta,
    list_closer_tools,
    tool_specs_for_prompt,
)

__all__ = [
    "CLOSER_TOOLS",
    "list_closer_tools",
    "tool_specs_for_prompt",
    "execute_tool_calls_from_meta",
]
