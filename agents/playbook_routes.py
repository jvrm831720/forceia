"""Rotas admin do Playbook por workspace."""

from __future__ import annotations

from db import (
    get_workspace_by_slug,
    get_workspace_playbook,
    log_event,
    update_workspace_playbook,
)
from fastapi import Depends, FastAPI, HTTPException
from logging_config import get_logger
from playbook import (
    EMPTY_PLAYBOOK,
    format_playbook_for_prompt,
    playbook_completeness,
)

log = get_logger("forceia.playbook")


def mount_playbook_routes(app: FastAPI, require_token) -> None:
    @app.get("/api/workspaces/{slug}/playbook", dependencies=[Depends(require_token)])
    async def api_get_playbook(slug: str):
        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace nao encontrado")
        pb = get_workspace_playbook(ws["id"])
        comp = playbook_completeness(pb)
        return {
            "workspace": slug,
            "playbook": pb,
            "completeness": comp,
            "prompt_preview": format_playbook_for_prompt(pb)[:2000],
        }

    @app.put("/api/workspaces/{slug}/playbook", dependencies=[Depends(require_token)])
    async def api_put_playbook(slug: str, body: dict):
        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace nao encontrado")
        current = get_workspace_playbook(ws["id"])
        incoming = body if isinstance(body, dict) else {}
        if "playbook" in incoming and isinstance(incoming.get("playbook"), dict):
            incoming = incoming["playbook"]
        merged = {**current, **{k: v for k, v in incoming.items() if v is not None}}
        for key in ("icp", "persona", "pricing", "tone"):
            if isinstance(incoming.get(key), dict) and isinstance(current.get(key), dict):
                merged[key] = {**current.get(key, {}), **incoming[key]}
        saved = update_workspace_playbook(ws["id"], merged)
        comp = playbook_completeness(saved)
        log_event(
            "playbook_updated",
            {"score": comp.get("score"), "ready": comp.get("ready")},
            workspace_id=ws["id"],
        )
        log.info("playbook updated", extra={"workspace": slug, "score": comp.get("score")})
        return {"ok": True, "workspace": slug, "playbook": saved, "completeness": comp}

    @app.get("/api/workspaces/{slug}/playbook/template", dependencies=[Depends(require_token)])
    async def api_playbook_template(slug: str):
        return {
            "workspace": slug,
            "playbook": EMPTY_PLAYBOOK,
            "completeness": playbook_completeness({}),
        }
