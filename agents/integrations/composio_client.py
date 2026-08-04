"""
Provider Composio para ForceIA.

- user_id Composio = workspace UUID (multi-tenant isolado)
- session_id persistido em workspaces.metadata.composio_session_id
- Degradação graciosa se SDK/API key ausentes
"""

from __future__ import annotations

import logging
import os
from typing import Any

from .base import (
    AuthorizeResult,
    ConnectedAccount,
    IntegrationStatus,
    ToolkitInfo,
)
from .registry import TOOLKIT_CATALOG, toolkit_catalog

log = logging.getLogger("forceia.integrations.composio")


def is_composio_enabled() -> bool:
    flag = (os.getenv("FORCEIA_COMPOSIO") or "").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    if flag in ("1", "true", "yes", "on"):
        return bool(os.getenv("COMPOSIO_API_KEY", "").strip())
    return bool(os.getenv("COMPOSIO_API_KEY", "").strip())


def _api_key() -> str:
    return (os.getenv("COMPOSIO_API_KEY") or "").strip()


def _default_toolkits() -> list[str]:
    raw = os.getenv("FORCEIA_COMPOSIO_TOOLKITS", "googlecalendar,gmail,slack,outlook")
    return [s.strip().lower() for s in raw.split(",") if s.strip()]


def _callback_url() -> str | None:
    return (os.getenv("FORCEIA_COMPOSIO_CALLBACK_URL") or "").strip() or None


def _user_id(workspace_id: str) -> str:
    return str(workspace_id)


def _get_workspace_meta(workspace_id: str) -> dict[str, Any]:
    try:
        from db import get_workspace_by_id
        row = get_workspace_by_id(workspace_id)
        if not row:
            return {}
        return dict(row.get("metadata") or {})
    except Exception as e:
        log.warning("falha ao ler metadata do workspace: %s", e)
        return {}


def _set_workspace_meta(workspace_id: str, extra: dict[str, Any]) -> dict[str, Any]:
    from db import update_workspace_metadata
    return update_workspace_metadata(workspace_id, extra)


def _import_composio():
    try:
        from composio import Composio  # type: ignore
        return Composio
    except ImportError as e:
        raise RuntimeError("Pacote 'composio' não instalado. pip install composio") from e


def _client():
    if not _api_key():
        raise RuntimeError("COMPOSIO_API_KEY não definido")
    Composio = _import_composio()
    return Composio(api_key=_api_key())


class ComposioProvider:
    name = "composio"

    def enabled(self) -> bool:
        return is_composio_enabled()

    def get_or_create_session(self, workspace_id: str) -> str:
        return get_or_create_session(workspace_id)

    def authorize(self, workspace_id: str, toolkit: str, *, callback_url: str | None = None) -> AuthorizeResult:
        return authorize(workspace_id, toolkit, callback_url=callback_url)

    def list_connected(self, workspace_id: str) -> list[ConnectedAccount]:
        return list_connected(workspace_id)

    def disconnect(self, workspace_id: str, toolkit: str) -> bool:
        return disconnect(workspace_id, toolkit)

    def execute_tool(self, workspace_id: str, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return execute_tool(workspace_id, tool, arguments)

    def list_toolkits(self) -> list[ToolkitInfo]:
        return list_available_toolkits()


_provider: ComposioProvider | None = None


def get_provider() -> ComposioProvider:
    global _provider
    if _provider is None:
        _provider = ComposioProvider()
    return _provider


def get_or_create_session(workspace_id: str) -> str:
    if not is_composio_enabled():
        raise RuntimeError("Composio desabilitado (FORCEIA_COMPOSIO / COMPOSIO_API_KEY)")
    meta = _get_workspace_meta(workspace_id)
    existing = meta.get("composio_session_id")
    client = _client()
    toolkits = _default_toolkits()
    user_id = _user_id(workspace_id)
    if existing:
        try:
            if hasattr(client, "use"):
                session = client.use(existing)
            elif hasattr(client, "sessions") and hasattr(client.sessions, "get"):
                session = client.sessions.get(existing)
            else:
                session = None
            if session is not None:
                sid = getattr(session, "session_id", None) or existing
                log.debug("reusou sessão Composio workspace=%s session=%s", workspace_id, sid)
                return str(sid)
        except Exception as e:
            log.info("sessão Composio inválida, recriando: %s", e)
    session = _create_session(client, user_id=user_id, toolkits=toolkits)
    sid = str(getattr(session, "session_id", None) or getattr(session, "id", None) or session)
    _set_workspace_meta(workspace_id, {"composio_session_id": sid, "composio_user_id": user_id, "composio_toolkits": toolkits})
    log.info("sessão Composio criada workspace=%s session=%s", workspace_id, sid)
    return sid


def _create_session(client: Any, *, user_id: str, toolkits: list[str]) -> Any:
    kwargs: dict[str, Any] = {"user_id": user_id}
    if toolkits:
        kwargs["toolkits"] = toolkits
    if hasattr(client, "create"):
        return client.create(**kwargs)
    if hasattr(client, "sessions") and hasattr(client.sessions, "create"):
        return client.sessions.create(**kwargs)
    raise RuntimeError("SDK Composio sem método create/sessions.create")


def _get_session(workspace_id: str) -> Any:
    sid = get_or_create_session(workspace_id)
    client = _client()
    if hasattr(client, "use"):
        return client.use(sid)
    if hasattr(client, "sessions") and hasattr(client.sessions, "get"):
        return client.sessions.get(sid)
    return type("Session", (), {"session_id": sid})()


def authorize(workspace_id: str, toolkit: str, *, callback_url: str | None = None) -> AuthorizeResult:
    toolkit = toolkit.strip().lower()
    allowed = {t.slug for t in list_available_toolkits()}
    if toolkit not in allowed and allowed:
        return AuthorizeResult(toolkit=toolkit, redirect_url=None, status=IntegrationStatus.ERROR, message=f"Toolkit '{toolkit}' fora da allowlist ForceIA")
    if not is_composio_enabled():
        return AuthorizeResult(toolkit=toolkit, redirect_url=None, status=IntegrationStatus.DISABLED, message="Composio desabilitado")
    cb = callback_url or _callback_url()
    session = _get_session(workspace_id)
    try:
        if hasattr(session, "authorize"):
            req = session.authorize(toolkit)
        else:
            client = _client()
            user_id = _user_id(workspace_id)
            if hasattr(client, "toolkits") and hasattr(client.toolkits, "authorize"):
                req = client.toolkits.authorize(user_id=user_id, toolkit=toolkit)
            else:
                raise RuntimeError("SDK Composio sem authorize")
        redirect = getattr(req, "redirect_url", None) or getattr(req, "redirectUrl", None) or getattr(req, "url", None)
        conn_id = getattr(req, "id", None) or getattr(req, "connected_account_id", None) or getattr(req, "connection_id", None)
        _set_workspace_meta(workspace_id, {f"composio_pending_{toolkit}": {"connection_id": str(conn_id) if conn_id else None, "status": "pending"}})
        return AuthorizeResult(toolkit=toolkit, redirect_url=str(redirect) if redirect else None, connection_id=str(conn_id) if conn_id else None, status=IntegrationStatus.PENDING, message="Abra redirect_url para autorizar" if redirect else None)
    except Exception as e:
        log.exception("authorize falhou toolkit=%s workspace=%s", toolkit, workspace_id)
        return AuthorizeResult(toolkit=toolkit, redirect_url=None, status=IntegrationStatus.ERROR, message=str(e))


def list_connected(workspace_id: str) -> list[ConnectedAccount]:
    if not is_composio_enabled():
        return []
    user_id = _user_id(workspace_id)
    client = _client()
    accounts: list[Any] = []
    try:
        ca = getattr(client, "connected_accounts", None)
        if ca is None:
            return []
        if hasattr(ca, "list"):
            try:
                resp = ca.list(user_ids=[user_id])
            except TypeError:
                try:
                    resp = ca.list(user_id=user_id)
                except TypeError:
                    resp = ca.list()
            if hasattr(resp, "items"):
                accounts = list(resp.items or [])
            elif isinstance(resp, list):
                accounts = resp
            elif hasattr(resp, "data"):
                accounts = list(resp.data or [])
            else:
                accounts = list(resp) if resp else []
    except Exception as e:
        log.warning("list_connected falhou workspace=%s: %s", workspace_id, e)
        return []
    out: list[ConnectedAccount] = []
    for acc in accounts:
        acc_user = getattr(acc, "user_id", None) or (acc.get("user_id") if isinstance(acc, dict) else None)
        if acc_user and str(acc_user) != user_id:
            continue
        toolkit = getattr(acc, "toolkit", None) or getattr(acc, "appName", None) or getattr(acc, "app_name", None) or (acc.get("toolkit") if isinstance(acc, dict) else None) or (acc.get("appName") if isinstance(acc, dict) else None) or ""
        if hasattr(toolkit, "slug"):
            toolkit = toolkit.slug
        toolkit = str(toolkit).lower()
        status_raw = getattr(acc, "status", None) or (acc.get("status") if isinstance(acc, dict) else None) or ""
        status_str = str(status_raw).upper()
        if status_str in ("ACTIVE", "CONNECTED", "SUCCESS"):
            status = IntegrationStatus.CONNECTED
        elif status_str in ("INITIATED", "PENDING", "INITIALIZING"):
            status = IntegrationStatus.PENDING
        else:
            status = IntegrationStatus.DISCONNECTED
        acc_id = str(getattr(acc, "id", None) or (acc.get("id") if isinstance(acc, dict) else None) or "")
        display = getattr(acc, "status_reason", None) or getattr(acc, "email", None) or (acc.get("email") if isinstance(acc, dict) else None)
        raw = acc if isinstance(acc, dict) else getattr(acc, "model_dump", lambda: {})()
        if not isinstance(raw, dict):
            raw = {}
        out.append(ConnectedAccount(id=acc_id, toolkit=toolkit, status=status, display_name=str(display) if display else None, raw=raw))
    return out


def disconnect(workspace_id: str, toolkit: str) -> bool:
    toolkit = toolkit.strip().lower()
    if not is_composio_enabled():
        return False
    connected = list_connected(workspace_id)
    targets = [c for c in connected if c.toolkit.lower() == toolkit and c.id]
    if not targets:
        return False
    client = _client()
    ca = getattr(client, "connected_accounts", None)
    ok = False
    for acc in targets:
        try:
            if ca and hasattr(ca, "delete"):
                ca.delete(acc.id)
                ok = True
            elif ca and hasattr(ca, "disable"):
                ca.disable(acc.id)
                ok = True
        except Exception as e:
            log.warning("disconnect %s id=%s: %s", toolkit, acc.id, e)
    try:
        _set_workspace_meta(workspace_id, {f"composio_pending_{toolkit}": None})
    except Exception:
        pass
    return ok


def execute_tool(workspace_id: str, tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    if not is_composio_enabled():
        return {"success": False, "error": "composio_disabled"}
    arguments = arguments or {}
    session = _get_session(workspace_id)
    try:
        if hasattr(session, "execute"):
            result = session.execute(tool, arguments)
        elif hasattr(session, "tools") and hasattr(session, "execute_tool"):
            result = session.execute_tool(tool, arguments)
        else:
            client = _client()
            tools = getattr(client, "tools", None)
            if tools and hasattr(tools, "execute"):
                result = tools.execute(slug=tool, arguments=arguments, user_id=_user_id(workspace_id))
            else:
                return {"success": False, "error": "execute_api_unavailable"}
        if hasattr(result, "model_dump"):
            data = result.model_dump()
        elif isinstance(result, dict):
            data = result
        else:
            data = {"result": str(result)}
        try:
            from db import log_event
            log_event("tool_executed", {"provider": "composio", "tool": tool, "arguments_keys": list(arguments.keys()), "success": True}, workspace_id=workspace_id)
        except Exception:
            pass
        return {"success": True, "data": data}
    except Exception as e:
        log.exception("execute_tool falhou tool=%s workspace=%s", tool, workspace_id)
        try:
            from db import log_event
            log_event("tool_executed", {"provider": "composio", "tool": tool, "success": False, "error": str(e)}, workspace_id=workspace_id)
        except Exception:
            pass
        return {"success": False, "error": str(e)}


def list_available_toolkits() -> list[ToolkitInfo]:
    allowed = _default_toolkits()
    if not allowed:
        return list(TOOLKIT_CATALOG)
    return toolkit_catalog(only_slugs=allowed)
