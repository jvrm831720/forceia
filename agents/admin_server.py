"""
ForceIA - Painel Admin (API + dashboard)

Auth JWT (recomendado):
  POST /api/auth/login  {username, password} -> access_token
  Authorization: Bearer <jwt>

Legado: ADMIN_TOKEN ainda aceito via Bearer ou X-Admin-Token.
Defina ADMIN_PASSWORD (+ JWT_SECRET) ou ADMIN_TOKEN no .env.

  cd agents
  python admin_server.py            # sobe em http://localhost:8100
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from auth import (
    LoginIn,
    TokenOut,
    assert_admin_password_policy,
    auth_enabled,
    create_access_token,
    require_auth,
    validate_password_strength,
    verify_password,
)
from db import (
    count_leads_by_stage,
    create_workspace,
    get_lead_by_id,
    get_messages_for_lead,
    get_prompt_suggestion,
    get_workspace_by_slug,
    list_active_workspaces,
    list_leads,
    list_prompt_suggestions,
    list_recent_events,
    update_prompt_suggestion,
    upsert_prompt_override,
)
from learning import ensure_meta_protocol
from datetime import UTC, datetime
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from logging_config import get_logger
from pydantic import BaseModel
from state_machine import STAGES

load_dotenv()

log = get_logger("forceia.admin")

APP_VERSION = "1.7.0"
STATIC_DIR = Path(__file__).resolve().parent / "static"
WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"

app = FastAPI(title="ForceIA Admin", version=APP_VERSION)

require_token = require_auth


class WorkspaceIn(BaseModel):
    name: str
    slug: str
    instance: str | None = None
    plan: str = "completo"


@app.get("/", include_in_schema=False)
async def index():
    spa = WEB_DIST / "index.html"
    if spa.exists():
        return FileResponse(spa)
    html = STATIC_DIR / "admin.html"
    if html.exists():
        return FileResponse(html)
    return JSONResponse(
        {"error": "UI nao encontrada. Rode: cd web && npm run build"},
        status_code=404,
    )


@app.get("/assets/{path:path}", include_in_schema=False)
async def spa_assets(path: str):
    target = (WEB_DIST / "assets" / path).resolve()
    if WEB_DIST.resolve() in target.parents and target.is_file():
        return FileResponse(target)
    raise HTTPException(status_code=404, detail="asset nao encontrado")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "forceia-admin",
        "version": APP_VERSION,
        "enabled": auth_enabled(),
        "auth": "jwt",
    }


@app.post("/api/auth/login", response_model=TokenOut)
async def api_login(payload: LoginIn):
    if not auth_enabled():
        raise HTTPException(
            status_code=503,
            detail="Auth desativada: defina ADMIN_PASSWORD ou ADMIN_TOKEN",
        )
    if not verify_password(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    token, expires_in = create_access_token(username=payload.username.strip())
    log.info("login ok", extra={"user": payload.username.strip()})
    return TokenOut(
        access_token=token,
        expires_in=expires_in,
        username=payload.username.strip(),
    )


@app.get("/api/auth/me")
async def api_me(claims: dict = Depends(require_token)):
    return {
        "username": claims.get("sub"),
        "role": claims.get("role"),
        "type": claims.get("type"),
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


@app.get("/api/workspaces/{slug}/leads/{lead_id}", dependencies=[Depends(require_token)])
async def api_lead_detail(slug: str, lead_id: str, messages_limit: int = 100):
    """Detalhe do lead + transcript (mensagens ordenadas)."""
    ws = get_workspace_by_slug(slug)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    lead = get_lead_by_id(ws["id"], lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nao encontrado")
    limit = max(1, min(int(messages_limit or 100), 500))
    messages = get_messages_for_lead(lead_id, limit=limit)
    transcript = []
    for m in messages:
        content = m.get("content") or ""
        if "---META---" in content:
            content = content.split("---META---", 1)[0].rstrip()
        transcript.append(
            {
                "role": m.get("role"),
                "content": content,
                "agent": m.get("agent"),
                "created_at": m.get("created_at"),
            }
        )
    return {
        "lead": {
            "id": lead.get("id"),
            "phone": lead.get("phone"),
            "name": lead.get("name"),
            "company": lead.get("company"),
            "email": lead.get("email"),
            "stage": lead.get("stage"),
            "bant": lead.get("bant") or {},
            "metadata": lead.get("metadata") or {},
            "last_message_at": lead.get("last_message_at"),
            "updated_at": lead.get("updated_at"),
            "created_at": lead.get("created_at"),
        },
        "messages": transcript,
        "message_count": len(transcript),
    }


@app.get("/api/workspaces/{slug}/events", dependencies=[Depends(require_token)])
async def api_events(slug: str, limit: int = 50):
    ws = get_workspace_by_slug(slug)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    return list_recent_events(ws["id"], limit=limit)


class ReviewIn(BaseModel):
    note: str | None = None


@app.get("/api/learning/suggestions", dependencies=[Depends(require_token)])
async def api_list_suggestions(status: str = "pending", limit: int = 50):
    return list_prompt_suggestions(status=status or None, limit=limit)


@app.get("/api/learning/suggestions/{suggestion_id}", dependencies=[Depends(require_token)])
async def api_get_suggestion(suggestion_id: str):
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sugestao nao encontrada")
    return row


@app.post("/api/learning/suggestions/{suggestion_id}/approve", dependencies=[Depends(require_token)])
async def api_approve(suggestion_id: str, body: ReviewIn | None = None):
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sugestao nao encontrada")
    return update_prompt_suggestion(
        suggestion_id,
        status="approved",
        reviewed_at=datetime.now(UTC).isoformat(),
        reviewed_note=(body.note if body else None),
    )


@app.post("/api/learning/suggestions/{suggestion_id}/reject", dependencies=[Depends(require_token)])
async def api_reject(suggestion_id: str, body: ReviewIn | None = None):
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sugestao nao encontrada")
    return update_prompt_suggestion(
        suggestion_id,
        status="rejected",
        reviewed_at=datetime.now(UTC).isoformat(),
        reviewed_note=(body.note if body else None),
    )


@app.post("/api/learning/suggestions/{suggestion_id}/apply", dependencies=[Depends(require_token)])
async def api_apply(suggestion_id: str):
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sugestao nao encontrada")
    if row.get("status") == "pending":
        update_prompt_suggestion(
            suggestion_id,
            status="approved",
            reviewed_at=datetime.now(UTC).isoformat(),
            reviewed_note="approved via admin apply",
        )
    content = ensure_meta_protocol(row["suggested_prompt"])
    override = upsert_prompt_override(
        row["agent"],
        content,
        workspace_id=row.get("workspace_id"),
        source_suggestion_id=suggestion_id,
    )
    update_prompt_suggestion(
        suggestion_id,
        status="applied",
        reviewed_at=datetime.now(UTC).isoformat(),
    )
    log.info("prompt applied", extra={"workspace": str(row.get("workspace_id")), "event": row["agent"]})
    return {"ok": True, "override": override, "agent": row["agent"]}


@app.post("/api/learning/run/{slug}", dependencies=[Depends(require_token)])
async def api_run_learning(slug: str, per_outcome: int = 8):
    from improve_agents import run_learning_for_workspace
    from workspace_context import WorkspaceContext

    ws_row = get_workspace_by_slug(slug)
    if not ws_row:
        raise HTTPException(status_code=404, detail="Workspace nao encontrado")
    ws = WorkspaceContext.from_row(ws_row)
    return run_learning_for_workspace(ws, per_outcome=per_outcome)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("ADMIN_PORT", "8100"))
    if not auth_enabled():
        print("AVISO: auth desativada — defina ADMIN_PASSWORD (JWT) ou ADMIN_TOKEN.")
    elif not (os.getenv("JWT_SECRET") or "").strip():
        print("AVISO: JWT_SECRET nao definido — usando segredo de desenvolvimento.")
    weak = assert_admin_password_policy()
    if weak:
        print("ERRO: ADMIN_PASSWORD fraca — login JWT bloqueado ate corrigir:")
        for err in weak:
            print(f"  - {err}")
        print("Ex.: Admin!ForceIA2026x  |  ou FORCEIA_ALLOW_WEAK_PASSWORD=1 so em dev.")
    uvicorn.run(app, host="0.0.0.0", port=port)
