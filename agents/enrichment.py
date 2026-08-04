"""ForceIA — Enrichment antes da primeira mensagem (nome, cargo, empresa, LinkedIn)."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

log = logging.getLogger("forceia.enrichment")

_TITLE_HINT_RE = re.compile(
    r"(?:sou\s+(?:o|a)\s+|trabalho\s+como\s+|cargo\s*(?:é|e|:)\s*)"
    r"(ceo|cto|cfo|cmo|coo|founder|fundador|sócio|socio|diretor|diretora|"
    r"gerente|head|coordenador|coordenadora|vendedor|sdr|closer|owner|dono|dona)"
    r"(?:\s+[a-zà-ÿ]{2,20}){0,3}",
    re.IGNORECASE,
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def enrichment_needed(lead: dict | None) -> bool:
    if not lead:
        return True
    meta = lead.get("metadata") or {}
    if meta.get("enrichment_status") in ("done", "skipped"):
        enr = meta.get("enrichment") or {}
        if enr and (lead.get("name") or enr.get("name")):
            return False
    if lead.get("name") and lead.get("company"):
        return False
    return True


def extract_from_text(text: str) -> dict[str, str]:
    from intelligence import extract_contact_hints

    out = extract_contact_hints(text or "")
    for tok in (
        "CEO", "CTO", "CFO", "CMO", "COO", "Founder", "Fundador", "Sócio",
        "Diretor", "Diretora", "Gerente", "Head", "Coordenador", "Coordenadora", "Dono", "Dona",
    ):
        if re.search(rf"\b{re.escape(tok)}\b", text or "", re.I):
            out["title"] = tok
            break
    return out


def _composio_linkedin_lookup(workspace_id: str, *, name: str | None, company: str | None, email: str | None) -> dict[str, Any]:
    try:
        from integrations.composio_client import execute_tool, is_composio_enabled
        if not is_composio_enabled():
            return {}
    except Exception:
        return {}
    query_bits = [x for x in (name, company, email) if x]
    if not query_bits:
        return {}
    query = " ".join(query_bits)
    candidates = [
        ("LINKEDIN_SEARCH_PEOPLE", {"query": query, "keywords": query}),
        ("linkedin_search_people", {"query": query}),
        ("LINKEDIN_GET_PERSON", {"name": name or "", "company": company or ""}),
    ]
    for tool, args in candidates:
        try:
            result = execute_tool(workspace_id, tool, args)
            if not result.get("success"):
                continue
            return _normalize_linkedin_payload(result.get("data") or {})
        except Exception as e:
            log.debug("composio linkedin tool %s: %s", tool, e)
    return {}


def _normalize_linkedin_payload(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    person = data.get("person") or data.get("profile") or data.get("result") or data
    if isinstance(person, list) and person:
        person = person[0]
    if not isinstance(person, dict):
        return {}
    out: dict[str, Any] = {}
    mapping = [
        ("name", "name"), ("full_name", "name"), ("fullName", "name"),
        ("title", "title"), ("headline", "title"), ("job_title", "title"),
        ("company", "company"), ("companyName", "company"), ("organization", "company"),
        ("linkedin_url", "linkedin_url"), ("profileUrl", "linkedin_url"), ("url", "linkedin_url"),
    ]
    for k_src, k_dst in mapping:
        val = person.get(k_src)
        if val and k_dst not in out:
            out[k_dst] = str(val).strip()
    return out


def _http_enrichment_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    url = (os.getenv("FORCEIA_ENRICHMENT_URL") or "").strip()
    if not url:
        return {}
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "ForceIA-Enrichment/2.1"},
            method="POST",
        )
        timeout = float(os.getenv("FORCEIA_ENRICHMENT_TIMEOUT", "4"))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            data = json.loads(body) if body else {}
            if isinstance(data, dict):
                return {k: data[k] for k in ("name", "company", "title", "email", "linkedin_url", "role") if data.get(k)}
    except Exception as e:
        log.warning("enrichment webhook falhou: %s", e)
    return {}


def linkedin_search_url(name: str | None, company: str | None) -> str | None:
    if not name and not company:
        return None
    q = " ".join(x for x in (name, company) if x)
    return f"https://www.linkedin.com/search/results/people/?keywords={quote(q)}"


def enrich_lead(workspace_id: str, lead: dict, *, user_text: str = "", force: bool = False) -> dict[str, Any]:
    if not force and not enrichment_needed(lead):
        return {
            "fields": {},
            "enrichment": (lead.get("metadata") or {}).get("enrichment") or {},
            "changed": False,
            "skipped": True,
        }
    hints = extract_from_text(user_text)
    existing = {"name": lead.get("name"), "company": lead.get("company"), "email": lead.get("email")}
    merged = {k: existing.get(k) or hints.get(k) for k in ("name", "company", "email")}
    title = hints.get("title")
    remote: dict[str, Any] = {}
    try:
        remote = _composio_linkedin_lookup(
            workspace_id, name=merged.get("name"), company=merged.get("company"), email=merged.get("email")
        )
    except Exception as e:
        log.debug("composio enrichment: %s", e)
    if not remote:
        remote = _http_enrichment_webhook({
            "workspace_id": workspace_id,
            "phone": lead.get("phone"),
            "name": merged.get("name"),
            "company": merged.get("company"),
            "email": merged.get("email"),
            "text": (user_text or "")[:500],
        })
    for k in ("name", "company", "email"):
        if remote.get(k) and not merged.get(k):
            merged[k] = remote[k]
    if remote.get("title"):
        title = title or remote["title"]
    if remote.get("role") and not title:
        title = remote["role"]
    linkedin = remote.get("linkedin_url") or linkedin_search_url(merged.get("name"), merged.get("company"))
    enrichment = {
        "name": merged.get("name"),
        "company": merged.get("company"),
        "email": merged.get("email"),
        "title": title,
        "linkedin_url": linkedin,
        "source": "composio" if remote.get("linkedin_url") else ("webhook" if remote else "heuristic"),
        "enriched_at": _now(),
    }
    enrichment = {k: v for k, v in enrichment.items() if v is not None}
    fields = {}
    if merged.get("name") and not lead.get("name"):
        fields["name"] = merged["name"]
    if merged.get("company") and not lead.get("company"):
        fields["company"] = merged["company"]
    if merged.get("email") and not lead.get("email"):
        fields["email"] = merged["email"]
    return {"fields": fields, "enrichment": enrichment, "changed": bool(fields or enrichment), "skipped": False}


def apply_enrichment_to_lead(lead: dict, result: dict[str, Any]) -> dict:
    out = dict(lead)
    for k, v in (result.get("fields") or {}).items():
        if v:
            out[k] = v
    meta = dict(out.get("metadata") or {})
    meta["enrichment"] = result.get("enrichment") or meta.get("enrichment") or {}
    meta["enrichment_status"] = "done" if result.get("changed") or result.get("skipped") else "empty"
    out["metadata"] = meta
    return out


def format_enrichment_for_prompt(lead: dict) -> str:
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    if not enr:
        return ""
    lines = ["## Enrichment (dados descobertos antes/durante a conversa)"]
    if enr.get("name"):
        lines.append(f"Nome: {enr['name']}")
    if enr.get("title"):
        lines.append(f"Cargo: {enr['title']}")
    if enr.get("company"):
        lines.append(f"Empresa: {enr['company']}")
    if enr.get("linkedin_url"):
        lines.append(f"LinkedIn: {enr['linkedin_url']}")
    lines.append("Use esses dados; não peça de novo o que já sabe.")
    return "\n".join(lines)
