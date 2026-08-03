"""Sync Twenty multi-tenant."""

from __future__ import annotations

import argparse
import os

from db import get_client, list_active_workspaces, log_event, merge_metadata
from twenty_client import sync_lead_to_twenty
from workspace_context import WorkspaceContext, resolve_workspace


def list_leads(workspace_id: str, limit: int = 100) -> list[dict]:
    result = (
        get_client()
        .table("leads")
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def sync_ws(ws: WorkspaceContext, limit: int, dry_run: bool) -> None:
    if not ws.twenty_api_url or not ws.twenty_api_key:
        print(f"[{ws.slug}] Twenty nao configurado — skip")
        return
    leads = list_leads(ws.id, limit=limit)
    print(f"[{ws.slug}] leads={len(leads)} dry_run={dry_run}")
    for lead in leads:
        phone = lead.get("phone")
        if dry_run:
            print(f"  {phone}: would_sync stage={lead.get('stage')}")
            continue
        try:
            result = sync_lead_to_twenty(
                lead, api_url=ws.twenty_api_url, api_key=ws.twenty_api_key
            )
            if result.get("person_id"):
                merge_metadata(
                    ws.id,
                    phone,
                    {
                        "twenty_person_id": result.get("person_id"),
                        "twenty_opportunity_id": result.get("opportunity_id"),
                    },
                )
                log_event("twenty_synced", result, lead_id=lead.get("id"), workspace_id=ws.id)
            print(f"  {phone}: ok")
        except Exception as exc:
            log_event("twenty_sync_error", {"error": str(exc)}, lead_id=lead.get("id"), workspace_id=ws.id)
            print(f"  {phone}: error {exc}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.all:
        wss = [WorkspaceContext.from_row(r) for r in list_active_workspaces()]
    else:
        slug = args.workspace or os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
        ws = resolve_workspace(slug=slug)
        if not ws:
            print(f"Workspace '{slug}' nao encontrado")
            return
        wss = [ws]

    for ws in wss:
        sync_ws(ws, args.limit, args.dry_run)


if __name__ == "__main__":
    main()
