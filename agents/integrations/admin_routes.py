"""Rotas admin de integrações (Composio) — montadas no admin_server."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from pydantic import BaseModel

from db import get_workspace_by_slug, log_event


class ConnectIn(BaseModel):
    callback_url: str | None = None


def mount_integration_routes(app, require_token):
    """Registra rotas de integração no app FastAPI."""

    @app.get("/api/workspaces/{slug}/integrations", dependencies=[Depends(require_token)])
    async def api_list_integrations(slug: str):
        from integrations import (
            get_workspace_integrations,
            is_composio_enabled,
            list_available_toolkits,
            list_connected,
        )

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace nao encontrado")
        enabled = is_composio_enabled()
        available = list_available_toolkits()
        connected = list_connected(ws["id"]) if enabled else []
        items = get_workspace_integrations(
            available=available,
            connected=connected,
            provider_enabled=enabled,
        )
        return {
            "workspace": slug,
            "provider": "composio",
            "enabled": enabled,
            "integrations": items,
        }

    @app.post(
        "/api/workspaces/{slug}/integrations/{toolkit}/connect",
        dependencies=[Depends(require_token)],
    )
    async def api_connect_integration(slug: str, toolkit: str, body: ConnectIn | None = None):
        from integrations import authorize, is_composio_enabled

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace nao encontrado")
        if not is_composio_enabled():
            raise HTTPException(
                status_code=503,
                detail="Composio desabilitado (FORCEIA_COMPOSIO / COMPOSIO_API_KEY)",
            )
        body = body or ConnectIn()
        result = authorize(ws["id"], toolkit, callback_url=body.callback_url)
        if result.status.value == "error":
            raise HTTPException(status_code=400, detail=result.message or "authorize falhou")
        if result.status.value == "disabled":
            raise HTTPException(status_code=503, detail=result.message or "Composio desabilitado")
        log_event(
            "integration_connect_started",
            {"toolkit": toolkit, "connection_id": result.connection_id},
            workspace_id=ws["id"],
        )
        return {
            "toolkit": result.toolkit,
            "redirect_url": result.redirect_url,
            "connection_id": result.connection_id,
            "status": result.status.value,
            "message": result.message,
        }

    @app.post(
        "/api/workspaces/{slug}/integrations/{toolkit}/disconnect",
        dependencies=[Depends(require_token)],
    )
    async def api_disconnect_integration(slug: str, toolkit: str):
        from integrations import disconnect, is_composio_enabled

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace nao encontrado")
        if not is_composio_enabled():
            raise HTTPException(status_code=503, detail="Composio desabilitado")
        ok = disconnect(ws["id"], toolkit)
        log_event(
            "integration_disconnected",
            {"toolkit": toolkit, "ok": ok},
            workspace_id=ws["id"],
        )
        return {"ok": ok, "toolkit": toolkit}

    @app.get("/api/integrations/health", dependencies=[Depends(require_token)])
    async def api_integrations_health():
        from integrations import is_composio_enabled, list_available_toolkits

        enabled = is_composio_enabled()
        sdk_ok = False
        if enabled:
            try:
                from integrations.composio_client import _import_composio

                _import_composio()
                sdk_ok = True
            except Exception:
                sdk_ok = False
        return {
            "enabled": enabled,
            "sdk_installed": sdk_ok,
            "toolkits": [t.slug for t in list_available_toolkits()],
        }

    try:
        from playbook_routes import mount_playbook_routes

        mount_playbook_routes(app, require_token)
    except Exception:
        pass

    try:
        from elite_routes import mount_elite_routes

        mount_elite_routes(app, require_admin=require_token)
    except Exception:
        pass

    try:
        from product_routes import mount_product_routes

        mount_product_routes(app, require_admin=require_token)
    except Exception:
        pass

    try:
        from trust_routes import mount_trust_routes

        mount_trust_routes(app, require_admin=require_token)
    except Exception:
        pass

    try:
        from skills_routes import mount_skills_routes

        mount_skills_routes(app, require_admin=require_token)
    except Exception:
        pass

    try:
        from scraper_routes import mount_scraper_routes

        mount_scraper_routes(app, require_admin=require_token)
    except Exception:
        pass
