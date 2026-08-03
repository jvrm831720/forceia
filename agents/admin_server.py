"""
ForceIA - Painel Admin (API + dashboard)

Endpoints protegidos por token (Authorization: Bearer <ADMIN_TOKEN>
ou header X-Admin-Token). Definir ADMIN_TOKEN no .env e obrigatorio
para ligar o painel (caso contrario as rotas retornam 503).

  cd agents
  python admin_server.py            # sobe em http://localhost:8100
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from db import (
    count_leads_by_stage,
    create_workspace,
    get_workspace_by_slug,
    list_active_workspaces,
    list_leads,
    list_recent_events,
)
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from logging_config import get_logger
from pydantic import BaseModel
from state_machine import STAGES

load_dotenv()

log = get_logger("forceia.admin")

APP_VERSION = "1.0.0"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="ForceIA Admin", version=APP_VERSION)


def require_token(
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> None:
    if not ADMIN_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Painel desativado: defina ADMIN_TOKEN no .env",
        )
    token = x_admin_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    if not token or not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Token invalido")


class WorkspaceIn(BaseModel):
    name: str
    slug: str
    instance: str | None = None
    plan: str = "completo"


@app.get("/", include_in_schema=False)
async def index():
    html = STATIC_DIR / "admin.html"
    if html.exists():
        return FileResponse(html)
    return JSONResponse({"error": "admin.html nao encontrado"}, status_code=404)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "forceia-admin",
        "version": APP_VERSION,
        "enabled": bool(ADMIN_TOKEN),
    }


@app.get("/api/workspaces", dependencies=[Depends(require_token)])
async def api_workspaces():
    rows = list_active_workspaces()
    return [
        {
            "id": w.get("id"),
            "name": w.get("name"),
            "slug": w.get("slug"),
            "instance": w.get("evolution_instance"),
            "plan": w.get("plan"),
            "created_at": w.get("created_at"),
        }
        for w in rows
    ]


@app.post("/api/workspaces", dependencies=[Depends(require_token)])
async def api_create_workspace(payload: WorkspaceIn):
    if get_workspace_by_slug(payload.slug):
        raise HTTPException(status_code=409, detail="Slug ja existe")
    api_key = secrets.token_hex(24)
    row = create_workspace(
        name=payload.name,
        slug=payload.slug,
        api_key=api_key,
        evolution_instance=payload.instance or payload.slug,
        plan=payload.plan,
    )
    log.info("workspace criado", extra={"workspace": payload.slug})
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "slug": row.get("slug"),
        "instance": row.get("evolution_instance"),
        "api_key": row.get("api_key") or api_key,
    }


@app.get("/api/workspaces/{slug}/metrics", dependencies=[Depends(require_token)])
async def api_metrics(slug: str):
    ws = get_workspace_by_slug(slug)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    counts = count_leads_by_stage(ws["id"])
    ordered = {stage: counts.get(stage, 0) for stage in STAGES}
    total = sum(ordered.values())
    won = ordered.get("won", 0)
    closed = won + ordered.get("lost", 0)
    return {
        "workspace": slug,
        "total": total,
        "by_stage": ordered,
        "win_rate": round(won / closed, 3) if closed else 0.0,
    }


@app.get("/api/workspaces/{slug}/leads", dependencies=[Depends(require_token)])
async def api_leads(slug: str, limit: int = 100):
    ws = get_workspace_by_slug(slug)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    return list_leads(ws["id"], limit=limit)


@app.get("/api/workspaces/{slug}/events", dependencies=[Depends(require_token)])
async def api_events(slug: str, limit: int = 50):
    ws = get_workspace_by_slug(slug)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    return list_recent_events(ws["id"], limit=limit)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("ADMIN_PORT", "8100"))
    if not ADMIN_TOKEN:
        print("AVISO: ADMIN_TOKEN nao definido — as rotas de dados retornarao 503.")
        print("Defina ADMIN_TOKEN no .env para habilitar o painel.")
    uvicorn.run(app, host="0.0.0.0", port=port)
