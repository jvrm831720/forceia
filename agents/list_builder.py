"""
ForceIA P2 — List building em massa (import de leads).

Aceita lista de contatos (phone obrigatório) e cria/atualiza leads no workspace.
Opcionalmente sincroniza com Twenty quando configurado.
"""

from __future__ import annotations

import re
from typing import Any

_PHONE_RE = re.compile(r"\D+")


def normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = _PHONE_RE.sub("", str(raw))
    if len(digits) < 10:
        return None
    # BR: se 10/11 dígitos sem country, prefixa 55
    if len(digits) in (10, 11) and not digits.startswith("55"):
        digits = "55" + digits
    return digits


def normalize_contact(row: dict[str, Any]) -> dict[str, Any] | None:
    phone = normalize_phone(row.get("phone") or row.get("telefone") or row.get("mobile"))
    if not phone:
        return None
    name = (row.get("name") or row.get("nome") or "").strip() or None
    company = (row.get("company") or row.get("empresa") or "").strip() or None
    email = (row.get("email") or "").strip() or None
    stage = (row.get("stage") or row.get("estagio") or "sdr").strip().lower()
    if stage not in ("sdr", "qualified", "closer", "followup", "won", "lost"):
        stage = "sdr"
    notes = (row.get("notes") or row.get("notas") or "").strip() or None
    source = (row.get("source") or row.get("origem") or "bulk_import").strip()
    out: dict[str, Any] = {
        "phone": phone,
        "name": name,
        "company": company,
        "email": email,
        "stage": stage,
        "source": source,
    }
    if notes:
        out["notes"] = notes
    # campos extras para metadata
    for k in ("title", "cargo", "linkedin", "domain", "domain_url"):
        if row.get(k):
            out[k] = str(row[k]).strip()
    return out


def import_leads_bulk(
    workspace_id: str,
    contacts: list[dict[str, Any]],
    *,
    default_stage: str = "sdr",
    source: str = "bulk_import",
    sync_twenty: bool = False,
    workspace_row: dict | None = None,
) -> dict[str, Any]:
    """Importa contatos. Retorna created/updated/skipped/errors."""
    from db import get_lead_by_phone, log_event, merge_metadata, upsert_lead

    created = 0
    updated = 0
    skipped = 0
    errors: list[dict[str, str]] = []
    leads_out: list[dict] = []

    seen_phones: set[str] = set()
    for i, raw in enumerate(contacts or []):
        if not isinstance(raw, dict):
            skipped += 1
            errors.append({"index": str(i), "error": "row not object"})
            continue
        row = dict(raw)
        if not row.get("stage") and default_stage:
            row["stage"] = default_stage
        if not row.get("source"):
            row["source"] = source
        contact = normalize_contact(row)
        if not contact:
            skipped += 1
            errors.append({"index": str(i), "error": "phone invalid or missing"})
            continue
        phone = contact["phone"]
        if phone in seen_phones:
            skipped += 1
            errors.append({"index": str(i), "phone": phone, "error": "duplicate in batch"})
            continue
        seen_phones.add(phone)

        existing = get_lead_by_phone(workspace_id, phone)
        fields: dict[str, Any] = {"stage": contact["stage"]}
        if contact.get("name"):
            fields["name"] = contact["name"]
        if contact.get("company"):
            fields["company"] = contact["company"]
        if contact.get("email"):
            fields["email"] = contact["email"]

        try:
            lead = upsert_lead(workspace_id, phone, **fields)
            meta_extra: dict[str, Any] = {
                "import_source": contact.get("source") or source,
            }
            if contact.get("notes"):
                meta_extra["import_notes"] = contact["notes"]
            if contact.get("title") or contact.get("cargo"):
                meta_extra["title"] = contact.get("title") or contact.get("cargo")
            if contact.get("linkedin"):
                meta_extra["linkedin_url"] = contact["linkedin"]
            if contact.get("domain") or contact.get("domain_url"):
                meta_extra["domain"] = contact.get("domain") or contact.get("domain_url")
            merge_metadata(workspace_id, phone, meta_extra)
            if existing:
                updated += 1
            else:
                created += 1
            leads_out.append(
                {
                    "id": lead.get("id"),
                    "phone": phone,
                    "name": lead.get("name") or contact.get("name"),
                    "company": lead.get("company") or contact.get("company"),
                    "stage": lead.get("stage") or contact["stage"],
                    "status": "updated" if existing else "created",
                }
            )
        except Exception as exc:
            errors.append({"index": str(i), "phone": phone, "error": str(exc)[:200]})
            skipped += 1

    log_event(
        "bulk_import",
        {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "source": source,
            "total_in": len(contacts or []),
        },
        workspace_id=workspace_id,
    )

    twenty_synced = 0
    if sync_twenty and workspace_row and leads_out:
        try:
            from twenty_client import sync_lead_to_twenty
            from workspace_context import WorkspaceContext

            ws_ctx = WorkspaceContext.from_row(workspace_row)
            if ws_ctx.twenty_api_url and ws_ctx.twenty_api_key:
                from db import get_lead_by_phone, merge_metadata

                for item in leads_out[:50]:  # hard cap por chamada
                    lead = get_lead_by_phone(workspace_id, item["phone"])
                    if not lead:
                        continue
                    result = sync_lead_to_twenty(
                        lead,
                        api_url=ws_ctx.twenty_api_url,
                        api_key=ws_ctx.twenty_api_key,
                    )
                    if result.get("person_id"):
                        merge_metadata(
                            workspace_id,
                            item["phone"],
                            {
                                "twenty_person_id": result.get("person_id"),
                                "twenty_opportunity_id": result.get("opportunity_id"),
                            },
                        )
                        twenty_synced += 1
        except Exception as exc:
            errors.append({"error": f"twenty_sync: {str(exc)[:200]}"})

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:50],
        "leads": leads_out[:100],
        "twenty_synced": twenty_synced,
        "total_in": len(contacts or []),
    }
