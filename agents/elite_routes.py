"""Admin API — Inteligência de elite (hot leads, enrich, schedule, proposal)."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel


def mount_elite_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    @app.get("/api/workspaces/{slug}/hot-leads", dependencies=[Depends(require_admin)])
    async def hot_leads(slug: str, limit: int = 20, min_score: int | None = None):
        from db import list_leads
        from lead_score import compute_lead_score, rank_hot_leads

        ws = _ws(slug)
        leads = list_leads(ws["id"], limit=200)
        ranked = rank_hot_leads(leads, limit=limit, min_score=min_score)
        rows = []
        for r in ranked:
            info = compute_lead_score(r)
            rows.append(
                {
                    "id": r.get("id"),
                    "phone": r.get("phone"),
                    "name": r.get("name"),
                    "company": r.get("company"),
                    "stage": r.get("stage"),
                    "score": info["score"],
                    "tier": info["tier"],
                    "hot": info["hot"],
                    "parts": info["parts"],
                    "buying_intent": (r.get("metadata") or {}).get("buying_intent"),
                    "last_message_at": r.get("last_message_at"),
                }
            )
        return {"workspace": slug, "count": len(rows), "leads": rows}

    class EnrichBody(BaseModel):
        force: bool = False
        text: str = ""

    @app.post("/api/workspaces/{slug}/leads/{lead_id}/enrich", dependencies=[Depends(require_admin)])
    async def enrich_lead_route(slug: str, lead_id: str, body: EnrichBody | None = None):
        from db import get_lead_by_id, log_event, update_lead_fields
        from enrichment import apply_enrichment_to_lead, enrich_lead

        ws = _ws(slug)
        body = body or EnrichBody()
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        result = enrich_lead(ws["id"], lead, user_text=body.text, force=body.force)
        updated = apply_enrichment_to_lead(lead, result)
        fields = dict(result.get("fields") or {})
        fields["metadata"] = updated.get("metadata")
        saved = update_lead_fields(ws["id"], lead_id, **fields)
        log_event(
            "lead_enriched",
            {"source": (result.get("enrichment") or {}).get("source")},
            lead_id=lead_id,
            workspace_id=ws["id"],
        )
        return {"lead": saved, "enrichment": result.get("enrichment"), "changed": result.get("changed")}

    class ScheduleBody(BaseModel):
        start_iso: str
        end_iso: str | None = None
        title: str = "Reunião comercial"
        attendee_email: str | None = None

    @app.post("/api/workspaces/{slug}/leads/{lead_id}/schedule", dependencies=[Depends(require_admin)])
    async def schedule_route(slug: str, lead_id: str, body: ScheduleBody):
        from closer_tools import schedule_meeting
        from db import get_lead_by_id, log_event, merge_metadata

        ws = _ws(slug)
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        result = schedule_meeting(
            ws["id"],
            title=body.title or f"Reunião — {lead.get('name') or lead.get('phone')}",
            start_iso=body.start_iso,
            end_iso=body.end_iso,
            attendee_email=body.attendee_email or lead.get("email"),
        )
        if lead.get("phone"):
            merge_metadata(
                ws["id"],
                lead["phone"],
                {"last_meeting": {"start": body.start_iso, "link": result.get("event_link"), "provider": result.get("provider")}},
            )
        log_event("meeting_scheduled", result, lead_id=lead_id, workspace_id=ws["id"])
        return result

    class ProposalBody(BaseModel):
        plan: str | None = None
        amount: str | None = None

    @app.post("/api/workspaces/{slug}/leads/{lead_id}/proposal", dependencies=[Depends(require_admin)])
    async def proposal_route(slug: str, lead_id: str, body: ProposalBody | None = None):
        from closer_tools import generate_proposal_link
        from db import get_lead_by_id, get_workspace_playbook, log_event, merge_metadata

        ws = _ws(slug)
        body = body or ProposalBody()
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        playbook = get_workspace_playbook(ws["id"])
        result = generate_proposal_link(
            workspace_slug=slug, lead=lead, playbook=playbook, plan=body.plan, amount=body.amount
        )
        if lead.get("phone"):
            merge_metadata(ws["id"], lead["phone"], {"last_proposal": result})
        log_event("proposal_generated", result, lead_id=lead_id, workspace_id=ws["id"])
        return result

    @app.get("/api/workspaces/{slug}/leads/{lead_id}/score", dependencies=[Depends(require_admin)])
    async def score_route(slug: str, lead_id: str):
        from db import get_lead_by_id
        from intent import intent_label_pt
        from lead_score import compute_lead_score

        ws = _ws(slug)
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        info = compute_lead_score(lead)
        meta = lead.get("metadata") or {}
        return {
            **info,
            "buying_intent": meta.get("buying_intent"),
            "intent_label": intent_label_pt(meta.get("buying_intent") or "unknown"),
            "intent_confidence": meta.get("intent_confidence"),
            "enrichment": meta.get("enrichment"),
        }
