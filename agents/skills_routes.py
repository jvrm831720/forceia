"""Admin API — Skills de elite (ICP, personalização, pré-call, revival, pipeline, hiring)."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def mount_skills_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    @app.get("/api/skills", dependencies=[Depends(require_admin)])
    async def api_list_skills():
        from skills import list_skills

        return {"skills": list_skills()}

    @app.get("/api/workspaces/{slug}/leads/{lead_id}/skills", dependencies=[Depends(require_admin)])
    async def api_lead_skills(slug: str, lead_id: str):
        from db import get_lead_by_id, get_messages_for_lead, get_workspace_playbook
        from skills import (
            build_personalization_brief,
            build_pre_call_brief,
            compute_icp_fit,
            score_pipeline_lead,
            score_revival,
        )
        from skills.hiring_signal import hiring_signal_from_lead

        ws = _ws(slug)
        lead = get_lead_by_id(ws["id"], lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="lead não encontrado")
        playbook = get_workspace_playbook(ws["id"])
        msgs = get_messages_for_lead(lead_id, limit=20)
        return {
            "lead_id": lead_id,
            "icp_fit": compute_icp_fit(lead, playbook),
            "personalization": build_personalization_brief(lead, playbook),
            "pre_call": build_pre_call_brief(lead, playbook, messages=msgs),
            "revival": score_revival(lead, playbook),
            "pipeline_health": score_pipeline_lead(lead),
            "hiring_signal": hiring_signal_from_lead(lead, playbook),
        }

    class HiringSignalIn(BaseModel):
        role: str = ""
        company: str = ""
        domain: str = ""
        jd_snippet: str = Field(default="", max_length=4000)
        posting_url: str = ""
        posting_date: str = ""
        decision_maker_name: str = ""
        decision_maker_title: str = ""
        lead_id: str | None = None
        attach_to_lead: bool = False

    @app.post("/api/workspaces/{slug}/skills/hiring-signal", dependencies=[Depends(require_admin)])
    async def api_analyze_hiring_signal(slug: str, body: HiringSignalIn):
        from db import get_lead_by_id, get_workspace_playbook, merge_metadata, log_event
        from skills.hiring_signal import analyze_hiring_signal

        ws = _ws(slug)
        playbook = get_workspace_playbook(ws["id"])
        analysis = analyze_hiring_signal(
            role=body.role,
            company=body.company,
            domain=body.domain,
            jd_snippet=body.jd_snippet,
            posting_url=body.posting_url,
            posting_date=body.posting_date,
            decision_maker_name=body.decision_maker_name,
            decision_maker_title=body.decision_maker_title,
            playbook=playbook,
        )

        attached = False
        if body.attach_to_lead and body.lead_id:
            lead = get_lead_by_id(ws["id"], body.lead_id)
            if not lead:
                raise HTTPException(status_code=404, detail="lead não encontrado")
            phone = lead.get("phone")
            payload = {
                "role": body.role,
                "company": body.company or lead.get("company"),
                "domain": body.domain,
                "jd_snippet": body.jd_snippet,
                "posting_url": body.posting_url,
                "posting_date": body.posting_date,
                "decision_maker_name": body.decision_maker_name or lead.get("name"),
                "decision_maker_title": body.decision_maker_title,
                "signal_strength": analysis["signal_strength"],
                "pain_point": analysis["pain_point"],
            }
            if phone:
                merge_metadata(ws["id"], phone, {"hiring_signal": payload})
                attached = True
            log_event(
                "hiring_signal_attached",
                {"lead_id": body.lead_id, "strength": analysis["signal_strength"]},
                lead_id=body.lead_id,
                workspace_id=ws["id"],
            )

        return {"analysis": analysis, "attached": attached}
