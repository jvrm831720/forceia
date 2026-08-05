"""Admin API — P2: badges, bulk import, closer tools."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def mount_p2_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    @app.get("/api/workspaces/{slug}/leads-enriched", dependencies=[Depends(require_admin)])
    async def api_leads_enriched(slug: str, limit: int = 60):
        """Lista de leads com badges (score/ICP/health/intent)."""
        from db import get_workspace_playbook, list_leads
        from lead_badges import enrich_lead_row

        ws = _ws(slug)
        playbook = get_workspace_playbook(ws["id"])
        leads = list_leads(ws["id"], limit=min(max(1, limit), 200))
        rows = [enrich_lead_row(l, playbook) for l in leads]
        return {"workspace": slug, "count": len(rows), "leads": rows}

    @app.get("/api/workspaces/{slug}/metrics-intel", dependencies=[Depends(require_admin)])
    async def api_metrics_intel(slug: str):
        """Métricas clássicas + agregados de inteligência."""
        from db import count_leads_by_stage, get_workspace_playbook, list_leads
        from lead_badges import summarize_workspace_intelligence
        from state_machine import STAGES

        ws = _ws(slug)
        counts = count_leads_by_stage(ws["id"])
        ordered = {stage: counts.get(stage, 0) for stage in STAGES}
        total = sum(ordered.values())
        won = ordered.get("won", 0)
        closed = won + ordered.get("lost", 0)
        playbook = get_workspace_playbook(ws["id"])
        sample = list_leads(ws["id"], limit=120)
        intel = summarize_workspace_intelligence(sample, playbook)
        return {
            "workspace": slug,
            "total": total,
            "by_stage": ordered,
            "win_rate": round(won / closed, 3) if closed else 0.0,
            "intel": intel,
        }

    class BulkContact(BaseModel):
        phone: str | None = None
        telefone: str | None = None
        name: str | None = None
        nome: str | None = None
        company: str | None = None
        empresa: str | None = None
        email: str | None = None
        stage: str | None = None
        notes: str | None = None
        source: str | None = None
        title: str | None = None
        cargo: str | None = None
        linkedin: str | None = None
        domain: str | None = None

    class BulkImportBody(BaseModel):
        contacts: list[dict] = Field(default_factory=list, max_length=500)
        default_stage: str = "sdr"
        source: str = "bulk_import"
        sync_twenty: bool = False

    @app.post("/api/workspaces/{slug}/leads/bulk", dependencies=[Depends(require_admin)])
    async def api_bulk_import(slug: str, body: BulkImportBody):
        from list_builder import import_leads_bulk

        ws = _ws(slug)
        if not body.contacts:
            raise HTTPException(status_code=400, detail="contacts vazio")
        if len(body.contacts) > 500:
            raise HTTPException(status_code=400, detail="máximo 500 contatos por chamada")
        result = import_leads_bulk(
            ws["id"],
            body.contacts,
            default_stage=body.default_stage or "sdr",
            source=body.source or "bulk_import",
            sync_twenty=bool(body.sync_twenty),
            workspace_row=ws,
        )
        return {"workspace": slug, **result}

    @app.get("/api/tools/closer", dependencies=[Depends(require_admin)])
    async def api_list_closer_tools():
        from tools.closer_registry import list_closer_tools, tool_specs_for_prompt

        return {"tools": list_closer_tools(), "prompt_block": tool_specs_for_prompt()}

    class ToolExecBody(BaseModel):
        name: str
        args: dict = Field(default_factory=dict)

    @app.post("/api/workspaces/{slug}/leads/{lead_id}/tools/execute", dependencies=[Depends(require_admin)])
    async def api_execute_tool(slug: str, lead_id: str, body: ToolExecBody):
        from db import get_lead_by_id, get_workspace_playbook, log_event, merge_metadata
        from tools.closer_registry import execute_tool_calls_from_meta

        ws = _ws(slug)
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        playbook = get_workspace_playbook(ws["id"])
        meta = {"tools": [{"name": body.name, "args": body.args or {}}]}
        out = execute_tool_calls_from_meta(
            workspace_id=ws["id"],
            workspace_slug=slug,
            lead=lead,
            meta=meta,
            playbook=playbook,
        )
        if out.get("calendar") and lead.get("phone"):
            cal = out["calendar"]
            merge_metadata(
                ws["id"],
                lead["phone"],
                {
                    "last_meeting": {
                        "start": cal.get("start"),
                        "link": cal.get("event_link"),
                        "provider": cal.get("provider"),
                    }
                },
            )
        if out.get("proposal") and lead.get("phone"):
            merge_metadata(ws["id"], lead["phone"], {"last_proposal": out["proposal"]})
        log_event(
            "tool_executed",
            {"name": body.name, "success": any(c.get("success") for c in out.get("calls") or [])},
            lead_id=lead_id,
            workspace_id=ws["id"],
        )
        return out
