"""Admin API — Skills de elite (ICP, personalização, pré-call, revival, pipeline)."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException


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
        }
