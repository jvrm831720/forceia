"""
Pipeline: URL de board/vaga → scrape → analyze_hiring_signal (skill).
"""

from __future__ import annotations

from typing import Any

from scrapers.job_boards import scrape_board, scrape_job_url


def prospect_hiring_signals(
    *,
    url: str,
    role_filter: str | None = None,
    limit: int = 20,
    playbook: dict | None = None,
    decision_maker_name: str = "",
) -> dict[str, Any]:
    """
    Coleta vagas e devolve análises prontas para outreach.
    """
    from skills.hiring_signal import analyze_hiring_signal

    raw_jobs = scrape_board(url, role_filter=role_filter, limit=limit)
    if not raw_jobs and url:
        raw_jobs = scrape_job_url(url)

    results = []
    for job in raw_jobs:
        analysis = analyze_hiring_signal(
            role=str(job.get("role") or ""),
            company=str(job.get("company") or ""),
            jd_snippet=str(job.get("jd_snippet") or ""),
            posting_url=str(job.get("posting_url") or url),
            decision_maker_name=decision_maker_name,
            playbook=playbook,
        )
        results.append(
            {
                **analysis,
                "location": job.get("location"),
                "source": job.get("source"),
            }
        )

    # ordena Strong primeiro
    order = {"Strong": 0, "Medium": 1, "Soft": 2}
    results.sort(key=lambda x: order.get(x.get("signal_strength") or "Soft", 9))

    return {
        "url": url,
        "role_filter": role_filter,
        "count": len(results),
        "signals": results,
        "strong": sum(1 for r in results if r.get("signal_strength") == "Strong"),
        "medium": sum(1 for r in results if r.get("signal_strength") == "Medium"),
        "soft": sum(1 for r in results if r.get("signal_strength") == "Soft"),
    }
