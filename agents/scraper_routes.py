"""Admin API — scraping de boards de vaga → hiring signals (hardened)."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


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
        from security import rate_limit_allow, validate_public_http_url

        ws = _ws(slug)
        url = body.url.strip()

        if not rate_limit_allow(f"scrape:{ws['id']}", limit=10, window_seconds=60):
            raise HTTPException(status_code=429, detail="Rate limit de scrape")

        ok, reason = validate_public_http_url(url)
        if not ok:
            raise HTTPException(status_code=400, detail=f"URL bloqueada: {reason}")

        playbook = get_workspace_playbook(ws["id"])
        try:
            report = prospect_hiring_signals(
                url=url,
                role_filter=body.role_filter,
                limit=body.limit,
                playbook=playbook,
                decision_maker_name=body.decision_maker_name,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            log_event(
                "scrape_hiring_error",
                {"url": url[:200], "error": str(exc)[:300]},
                workspace_id=ws["id"],
            )
            raise HTTPException(status_code=502, detail="scrape falhou") from exc

        log_event(
            "scrape_hiring_done",
            {"url": url[:200], "count": report.get("count"), "strong": report.get("strong")},
            workspace_id=ws["id"],
        )
        return report
