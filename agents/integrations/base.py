"""Contratos da camada de integrações ForceIA."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class IntegrationStatus(str, Enum):
    DISABLED = "disabled"  # feature off / sem API key
    DISCONNECTED = "disconnected"
    PENDING = "pending"  # OAuth iniciado
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ToolkitInfo:
    """Toolkit disponível para o workspace (allowlist)."""

    slug: str
    name: str
    description: str = ""
    category: str = "general"  # calendar | email | crm | notify | other
    priority: str = "P2"  # P0 | P1 | P2 | P3


@dataclass
class ConnectedAccount:
    id: str
    toolkit: str
    status: IntegrationStatus
    display_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizeResult:
    """Resultado de iniciar OAuth / Connect Link."""

    toolkit: str
    redirect_url: str | None
    connection_id: str | None = None
    status: IntegrationStatus = IntegrationStatus.PENDING
    message: str | None = None


@runtime_checkable
class IntegrationProvider(Protocol):
    """Provider de toolkits autenticados (Composio, futuro custom, etc.)."""

    name: str

    def enabled(self) -> bool:
        ...

    def get_or_create_session(self, workspace_id: str) -> str:
        """Retorna session_id persistido para o workspace."""
        ...

    def authorize(
        self,
        workspace_id: str,
        toolkit: str,
        *,
        callback_url: str | None = None,
    ) -> AuthorizeResult:
        ...

    def list_connected(self, workspace_id: str) -> list[ConnectedAccount]:
        ...

    def disconnect(self, workspace_id: str, toolkit: str) -> bool:
        ...

    def execute_tool(
        self,
        workspace_id: str,
        tool: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        ...

    def list_toolkits(self) -> list[ToolkitInfo]:
        ...
