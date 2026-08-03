"""
ForceIA - Job de sincronizacao em lote com Twenty CRM

  python sync_twenty_job.py
  python sync_twenty_job.py --limit 100
  python sync_twenty_job.py --dry-run
"""

from __future__ import annotations

import argparse

from db import get_client, log_event, merge_metadata
from twenty_client import enabled, sync_lead_to_twenty


def list_leads(limit: int = 100) -> list[dict]:
    client = get_client()
    result = (
        client.table("leads")
        .select("*")
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not enabled():
        print("Twenty nao configurado. Defina TWENTY_API_URL e TWENTY_API_KEY.")
        return

    leads = list_leads(limit=args.limit)
    print(f"Sync Twenty | leads={len(leads)} | dry_run={args.dry_run}")

    for lead in leads:
        phone = lead.get("phone")
        if args.dry_run:
            print(f"  {phone}: would_sync stage={lead.get('stage')}")
            continue
        try:
            result = sync_lead_to_twenty(lead)
            if result.get("person_id"):
                merge_metadata(
                    phone,
                    {
                        "twenty_person_id": result.get("person_id"),
                        "twenty_opportunity_id": result.get("opportunity_id"),
                    },
                )
                log_event(lead.get("id"), "twenty_synced", result)
            print(f"  {phone}: ok person={result.get('person_id')} opp={result.get('opportunity_id')}")
        except Exception as exc:
            log_event(lead.get("id"), "twenty_sync_error", {"error": str(exc)})
            print(f"  {phone}: error {exc}")


if __name__ == "__main__":
    main()
