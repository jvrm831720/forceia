"""Admin API — Prioridade 3: Experiência de produto."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def mount_product_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    # --- 9. Dashboard performance (reuniões + IA vs humano) ---
    @app.get("/api/workspaces/{slug}/performance", dependencies=[Depends(require_admin)])
    async def api_performance(slug: str, period: str = "week"):
        from performance import fetch_performance

        ws = _ws(slug)
        data = fetch_performance(ws["id"], period=period)
        data["workspace"] = slug
        data["workspace_name"] = ws.get("name")
        return data

    # --- 10. Relatório WhatsApp para o dono ---
    class ReportBody(BaseModel):
        period: str = "week"
        phone: str | None = None
        dry_run: bool = False

    @app.get("/api/workspaces/{slug}/reports/preview", dependencies=[Depends(require_admin)])
    async def api_report_preview(slug: str, period: str = "week"):
        from owner_reports import build_and_send_owner_report

        ws = _ws(slug)
        return build_and_send_owner_report(workspace=ws, period=period, dry_run=True)

    @app.post("/api/workspaces/{slug}/reports/send", dependencies=[Depends(require_admin)])
    async def api_report_send(slug: str, body: ReportBody | None = None):
        from owner_reports import build_and_send_owner_report

        ws = _ws(slug)
        body = body or ReportBody()
        result = build_and_send_owner_report(
            workspace=ws,
            period=body.period,
            phone=body.phone,
            dry_run=body.dry_run,
        )
        if not result.get("sent") and not body.dry_run and result.get("error"):
            raise HTTPException(status_code=502, detail=result.get("error") or "falha ao enviar")
        if not result.get("phone") and not body.dry_run:
            raise HTTPException(
                status_code=400,
                detail=result.get("message") or "owner_phone não configurado",
            )
        return result

    class OwnerPhoneBody(BaseModel):
        phone: str = Field(min_length=10, max_length=20)

    @app.put("/api/workspaces/{slug}/owner-phone", dependencies=[Depends(require_admin)])
    async def api_set_owner_phone(slug: str, body: OwnerPhoneBody):
        from db import update_workspace_metadata

        ws = _ws(slug)
        digits = "".join(c for c in body.phone if c.isdigit())
        meta = update_workspace_metadata(ws["id"], {"owner_phone": digits})
        return {"ok": True, "owner_phone": digits, "metadata_keys": list((meta or {}).keys())}

    # --- 11. Playground de simulação ---
    class PlaygroundLeadIn(BaseModel):
        name: str | None = "Lead Demo"
        company: str | None = "Empresa Fictícia"
        stage: str = "sdr"
        persona_note: str | None = None
        bant: dict | None = None

    class PlaygroundTurnIn(BaseModel):
        message: str = Field(min_length=1, max_length=4000)
        history: list[dict] = Field(default_factory=list)
        lead: PlaygroundLeadIn | None = None
        agent: str | None = None

    @app.post("/api/workspaces/{slug}/playground", dependencies=[Depends(require_admin)])
    async def api_playground(slug: str, body: PlaygroundTurnIn):
        from playground import default_fictional_lead, simulate_turn

        ws = _ws(slug)
        lead_in = body.lead
        if lead_in:
            lead = default_fictional_lead(
                name=lead_in.name,
                company=lead_in.company,
                stage=lead_in.stage,
                persona_note=lead_in.persona_note,
            )
            if lead_in.bant:
                lead["bant"] = lead_in.bant
        else:
            lead = default_fictional_lead()

        # Se history já carrega estado do lead no último turno, preferir stage/bant do cliente
        try:
            result = simulate_turn(
                workspace=ws,
                user_message=body.message.strip(),
                history=body.history,
                lead=lead,
                agent=body.agent,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"playground falhou: {e}") from e
        return result
