"""Resolve workspace e credenciais por tenant."""

from __future__ import annotations

import os
from dataclasses import dataclass

from db import get_workspace_by_api_key, get_workspace_by_evolution_instance, get_workspace_by_slug


@dataclass
class WorkspaceContext:
    id: str
    name: str
    slug: str
    evolution_instance: str
    evolution_api_url: str
    evolution_api_key: str
    twenty_api_url: str
    twenty_api_key: str
    openai_api_key: str
    gpt_model: str
    followup_stale_days: int
    followup_min_hours: int
    raw: dict

    @classmethod
    def from_row(cls, row: dict) -> WorkspaceContext:
        return cls(
            id=row["id"],
            name=row.get("name") or row.get("slug") or "",
            slug=row.get("slug") or "",
            evolution_instance=row.get("evolution_instance")
            or os.getenv("EVOLUTION_INSTANCE", "forceia"),
            evolution_api_url=row.get("evolution_api_url")
            or os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
            evolution_api_key=row.get("evolution_api_key")
            or os.getenv("EVOLUTION_API_KEY", "forceia-dev-key"),
            twenty_api_url=row.get("twenty_api_url") or os.getenv("TWENTY_API_URL", ""),
            twenty_api_key=row.get("twenty_api_key") or os.getenv("TWENTY_API_KEY", ""),
            openai_api_key=row.get("openai_api_key") or os.getenv("OPENAI_API_KEY", ""),
            gpt_model=row.get("gpt_model") or os.getenv("GPT_MODEL", "gpt-4o-mini"),
            followup_stale_days=int(
                row.get("followup_stale_days")
                or os.getenv("FOLLOWUP_STALE_DAYS", "5")
            ),
            followup_min_hours=int(
                row.get("followup_min_hours")
                or os.getenv("FOLLOWUP_MIN_HOURS", "48")
            ),
            raw=row,
        )


def resolve_workspace(
    *,
    api_key: str | None = None,
    evolution_instance: str | None = None,
    slug: str | None = None,
    workspace_id: str | None = None,
) -> WorkspaceContext | None:
    from db import get_workspace_by_id

    row = None
    if workspace_id:
        row = get_workspace_by_id(workspace_id)
    if not row and api_key:
        row = get_workspace_by_api_key(api_key)
    if not row and evolution_instance:
        row = get_workspace_by_evolution_instance(evolution_instance)
    if not row and slug:
        row = get_workspace_by_slug(slug)
    if not row and os.getenv("DEFAULT_WORKSPACE_SLUG"):
        row = get_workspace_by_slug(os.getenv("DEFAULT_WORKSPACE_SLUG", "default"))
    if not row:
        return None
    return WorkspaceContext.from_row(row)
