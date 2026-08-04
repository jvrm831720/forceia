"""Admin API — scraping de boards de vaga → hiring signals."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl


def mount_scraper_routes(app: FastAPI, require_admin) -> None:
    def _ws(slug: str) -> dict:
        from db import get_workspace_by_slug

        ws = get_workspace_by_slug(slug)
        if not ws:
            raise HTTPException(status_code=404, detail="workspace não encontrado")
        return ws

    class ScrapeHiringIn(BaseModel):
        url: str = Field(..., min_length=8, max_length=2000)
        role_filter: str | None = Field(
            default=None,
            description="Filtra título (ex.: SDR, RevOps)",
        )
        limit: int = Field(default=20, ge=1, le=50)
        decision_maker_name: str = ""

    @app.post(
        "/api/workspaces/{slug}/skills/scrape-hiring",
        dependencies=[Depends(require_admin)],
    )
    async def api_scrape_hiring(slug: str, body: ScrapeHiringIn):
        from db import get_workspace_playbook, log_event
        from scrapers.hiring_pipeline import prospect_hiring_signals

        ws = _ws(slug)
        url = body.url.strip()
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="url deve começar com http(s)")

        # Domínios sensíveis — bloqueio explícito
        blocked = ("linkedin.com", "facebook.com", "instagram.com")
        low = url.lower()
        if any(b in low for b in blocked):
            raise HTTPException(
                status_code=400,
                detail="Scraping deste domínio não é suportado (ToS). Use Greenhouse/Lever/board público.",
            )

        playbook = get_workspace_playbook(ws["id"])
        try:
            report = prospect_hiring_signals(
                url=url,
                role_filter=body.role_filter,
                limit=body.limit,
                playbook=playbook,
                decision_maker_name=body.decision_maker_name,
            )
        except Exception as exc:
            log_event(
                "scrape_hiring_error",
                {"url": url, "error": str(exc)},
                workspace_id=ws["id"],
            )
            raise HTTPException(status_code=502, detail=f"scrape falhou: {exc}") from exc

        log_event(
            "scrape_hiring_done",
            {"url": url, "count": report.get("count"), "strong": report.get("strong")},
            workspace_id=ws["id"],
        )
        return report
