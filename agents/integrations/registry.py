"""Catálogo de toolkits e status consolidado por workspace."""

from __future__ import annotations

from typing import Any

from .base import ConnectedAccount, IntegrationStatus, ToolkitInfo

# Catálogo canônico ForceIA (BR B2B). Slugs alinhados ao Composio quando possível.
TOOLKIT_CATALOG: list[ToolkitInfo] = [
    ToolkitInfo(
        slug="googlecalendar",
        name="Google Calendar",
        description="Agendar demos e reuniões no calendário do time comercial",
        category="calendar",
        priority="P0",
    ),
    ToolkitInfo(
        slug="gmail",
        name="Gmail",
        description="Follow-up por e-mail paralelo ao WhatsApp",
        category="email",
        priority="P0",
    ),
    ToolkitInfo(
        slug="outlook",
        name="Outlook",
        description="Calendar + e-mail Microsoft 365",
        category="calendar",
        priority="P0",
    ),
    ToolkitInfo(
        slug="slack",
        name="Slack",
        description="Alertas de handoff e leads quentes para o time humano",
        category="notify",
        priority="P1",
    ),
    ToolkitInfo(
        slug="hubspot",
        name="HubSpot",
        description="CRM alternativo ao Twenty",
        category="crm",
        priority="P1",
    ),
    ToolkitInfo(
        slug="pipedrive",
        name="Pipedrive",
        description="CRM alternativo ao Twenty",
        category="crm",
        priority="P1",
    ),
    ToolkitInfo(
        slug="googlesheets",
        name="Google Sheets",
        description="Export simples de leads e métricas",
        category="other",
        priority="P2",
    ),
]


def toolkit_catalog(*, only_slugs: list[str] | None = None) -> list[ToolkitInfo]:
    if not only_slugs:
        return list(TOOLKIT_CATALOG)
    allowed = {s.strip().lower() for s in only_slugs if s.strip()}
    return [t for t in TOOLKIT_CATALOG if t.slug.lower() in allowed]


def get_workspace_integrations(
    *,
    available: list[ToolkitInfo],
    connected: list[ConnectedAccount],
    provider_enabled: bool,
) -> list[dict[str, Any]]:
    """
    Junta catálogo + contas conectadas para a API admin.

    Retorno estável para o front:
      [{slug, name, description, category, priority, status, connection_id, display_name}]
    """
    by_toolkit: dict[str, ConnectedAccount] = {}
    for acc in connected:
        key = (acc.toolkit or "").lower()
        prev = by_toolkit.get(key)
        if prev is None or acc.status == IntegrationStatus.CONNECTED:
            by_toolkit[key] = acc

    rows: list[dict[str, Any]] = []
    for tk in available:
        if not provider_enabled:
            status = IntegrationStatus.DISABLED.value
            acc = None
        else:
            acc = by_toolkit.get(tk.slug.lower())
            status = (acc.status.value if acc else IntegrationStatus.DISCONNECTED.value)
        rows.append(
            {
                "slug": tk.slug,
                "name": tk.name,
                "description": tk.description,
                "category": tk.category,
                "priority": tk.priority,
                "status": status,
                "connection_id": acc.id if acc else None,
                "display_name": acc.display_name if acc else None,
            }
        )
    return rows
