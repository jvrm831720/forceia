"""Admin API — Prioridade 4: Confiabilidade e confiança."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def mount_trust_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    @app.get("/api/workspaces/{slug}/ab-report", dependencies=[Depends(require_admin)])
    async def api_ab_report(slug: str):
        from ab_testing import compute_ab_report
        from db import list_leads

        ws = _ws(slug)
        leads = list_leads(ws["id"], limit=500)
        report = compute_ab_report(leads)
        report["workspace"] = slug
        return report

    class HandoffBody(BaseModel):
        reason: str | None = "handoff manual pelo painel"
        notify: bool = True
        phone: str | None = None

    @app.post("/api/workspaces/{slug}/leads/{lead_id}/handoff", dependencies=[Depends(require_admin)])
    async def api_handoff(slug: str, lead_id: str, body: HandoffBody | None = None):
        from db import get_lead_by_id
        from handoff import execute_handoff

        ws = _ws(slug)
        body = body or HandoffBody()
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        result = execute_handoff(
            workspace=ws,
            lead=lead,
            reason=body.reason,
            notify=body.notify,
            phone_override=body.phone,
            by="admin",
        )
        return result

    class GuardrailScanBody(BaseModel):
        text: str = Field(min_length=1, max_length=8000)

    @app.post("/api/workspaces/{slug}/guardrails/scan", dependencies=[Depends(require_admin)])
    async def api_guardrail_scan(slug: str, body: GuardrailScanBody):
        from db import get_workspace_playbook
        from guardrails import enforce_guardrails, scan_reply

        ws = _ws(slug)
        playbook = get_workspace_playbook(ws["id"])
        scan = scan_reply(body.text, playbook=playbook)
        enforced = enforce_guardrails(body.text, playbook=playbook, strict=True)
        return {"scan": scan, "enforced": enforced}
