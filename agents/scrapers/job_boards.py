"""
Scraper de páginas de vaga públicas (Greenhouse, Lever, genérico).

Respeita robots/ToS do site: use só boards públicos e rate-limit.
Não tenta LinkedIn (auth wall / ToS restritivo).
Anti-SSRF: bloqueia IPs privados, metadata e hosts locais.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from security import validate_public_http_url

_USER_AGENT = (
    "ForceIA-HiringSignal/1.0 (+https://github.com/jvrm831720/forceia; research bot)"
)
_TIMEOUT = 20.0


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=_TIMEOUT,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
        follow_redirects=True,
        max_redirects=5,
    )


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _guess_company_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    for prefix in ("boards.", "jobs.", "www."):
        if host.startswith(prefix):
            host = host[len(prefix) :]
    path = urlparse(url).path.strip("/").split("/")
    if "greenhouse.io" in host and path:
        return path[0].replace("-", " ").title()
    if "lever.co" in host and path:
        return path[0].replace("-", " ").title()
    return host.split(".")[0].title() if host else ""


def _parse_greenhouse_json(data: Any, url: str) -> list[dict[str, Any]]:
    jobs = []
    if isinstance(data, dict):
        items = data.get("jobs") or data.get("departments") or []
        if data.get("title"):
            items = [data]
    elif isinstance(data, list):
        items = data
    else:
        items = []

    flat: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if "jobs" in item and isinstance(item["jobs"], list):
            flat.extend(j for j in item["jobs"] if isinstance(j, dict))
        else:
            flat.append(item)

    for j in flat:
        title = str(j.get("title") or j.get("name") or "")
        abs_url = str(j.get("absolute_url") or j.get("url") or url)
        loc = j.get("location")
        if isinstance(loc, dict):
            loc = loc.get("name")
        content = str(j.get("content") or j.get("description") or "")
        content = _strip_html(content) if "<" in content else content
        jobs.append(
            {
                "role": title,
                "company": _guess_company_from_url(abs_url),
                "jd_snippet": content[:1500],
                "posting_url": abs_url,
                "location": loc,
                "source": "greenhouse",
            }
        )
    return jobs


def _parse_lever_json(data: Any, url: str) -> list[dict[str, Any]]:
    jobs = []
    items = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    for j in items:
        if not isinstance(j, dict):
            continue
        title = str(j.get("text") or j.get("title") or "")
        abs_url = str(j.get("hostedUrl") or j.get("applyUrl") or url)
        cats = j.get("categories") or {}
        loc = cats.get("location") if isinstance(cats, dict) else None
        lists = j.get("lists") or []
        parts = []
        if isinstance(lists, list):
            for block in lists:
                if isinstance(block, dict):
                    parts.append(str(block.get("text") or ""))
                    parts.append(str(block.get("content") or ""))
        desc = j.get("descriptionPlain") or j.get("description") or " ".join(parts)
        desc = _strip_html(str(desc))
        jobs.append(
            {
                "role": title,
                "company": _guess_company_from_url(abs_url),
                "jd_snippet": desc[:1500],
                "posting_url": abs_url,
                "location": loc,
                "source": "lever",
            }
        )
    return jobs


def _parse_html_generic(html: str, url: str) -> dict[str, Any]:
    title = ""
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    if m:
        title = _strip_html(m.group(1))
    if not title:
        m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        if m:
            title = _strip_html(m.group(1)).split("|")[0].split("-")[0].strip()
    body = _strip_html(html)[:2000]
    return {
        "role": title,
        "company": _guess_company_from_url(url),
        "jd_snippet": body,
        "posting_url": url,
        "location": None,
        "source": "html",
    }


def fetch_job_page(url: str) -> dict[str, Any]:
    """GET de uma URL de vaga; retorna {ok, status, content_type, text/json}."""
    ok, reason = validate_public_http_url(url)
    if not ok:
        return {
            "ok": False,
            "status": 0,
            "content_type": "",
            "url": url,
            "text": "",
            "error": reason,
        }
    with _client() as client:
        r = client.get(url)
        # revalida URL final após redirects
        final = str(r.url)
        ok2, reason2 = validate_public_http_url(final)
        if not ok2:
            return {
                "ok": False,
                "status": 0,
                "content_type": "",
                "url": final,
                "text": "",
                "error": f"redirect bloqueado: {reason2}",
            }
        ct = (r.headers.get("content-type") or "").lower()
        return {
            "ok": r.status_code < 400,
            "status": r.status_code,
            "content_type": ct,
            "url": final,
            "text": r.text[:500_000] if r.text else "",
        }


def scrape_job_url(url: str) -> list[dict[str, Any]]:
    url = (url or "").strip()
    if not url:
        return []

    ok, reason = validate_public_http_url(url)
    if not ok:
        raise ValueError(f"URL bloqueada (anti-SSRF): {reason}")

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    api_url = url
    if "greenhouse.io" in host and "/jobs" not in path and "boards-api" not in host:
        token = path.strip("/").split("/")[0]
        if token and re.fullmatch(r"[A-Za-z0-9_-]+", token):
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    elif "lever.co" in host and "api.lever.co" not in host:
        company = path.strip("/").split("/")[0]
        if company and re.fullmatch(r"[A-Za-z0-9_-]+", company):
            api_url = f"https://api.lever.co/v0/postings/{company}?mode=json"

    raw = fetch_job_page(api_url)
    if not raw["ok"]:
        raw = fetch_job_page(url)
        if not raw["ok"]:
            return []

    text = raw["text"]
    ct = raw["content_type"]

    if "json" in ct or text.lstrip().startswith(("{", "[")):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if data is not None:
            if "greenhouse" in api_url or "greenhouse" in host:
                jobs = _parse_greenhouse_json(data, url)
                if jobs:
                    return jobs
            if "lever" in api_url or "lever" in host:
                jobs = _parse_lever_json(data, url)
                if jobs:
                    return jobs
            if isinstance(data, dict) and (data.get("title") or data.get("text")):
                return _parse_greenhouse_json(data, url) or _parse_lever_json(data, url)

    return [_parse_html_generic(text, url)]


def scrape_board(
    board_url: str,
    *,
    role_filter: str | None = None,
    limit: int = 30,
) -> list[dict[str, Any]]:
    jobs = scrape_job_url(board_url)
    if role_filter:
        rf = role_filter.lower()
        jobs = [j for j in jobs if rf in (j.get("role") or "").lower()]
    return jobs[: max(1, min(limit, 100))]
