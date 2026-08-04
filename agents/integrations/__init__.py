"""Camada de integrações ForceIA (Composio e providers futuros)."""

from __future__ import annotations

from .base import (
    AuthorizeResult,
    ConnectedAccount,
    IntegrationProvider,
    IntegrationStatus,
    ToolkitInfo,
)
from .composio_client import (
    ComposioProvider,
    execute_tool,
    get_or_create_session,
    get_provider,
    is_composio_enabled,
    list_available_toolkits,
    list_connected,
    authorize,
)
from .registry import get_workspace_integrations, toolkit_catalog
from .actions import run_agent_actions

__all__ = [
    "AuthorizeResult",
    "ConnectedAccount",
    "ComposioProvider",
    "IntegrationProvider",
    "IntegrationStatus",
    "ToolkitInfo",
    "authorize",
    "execute_tool",
    "get_or_create_session",
    "get_provider",
    "get_workspace_integrations",
    "is_composio_enabled",
    "list_available_toolkits",
    "list_connected",
    "toolkit_catalog",
    "run_agent_actions",
]
