"""
ForceIA - Scheduler multi-tenant (alternativa ao cron)

  python scheduler.py
  python scheduler.py --hours 6 --all
  python scheduler.py --workspace default --once
"""

from __future__ import annotations

import argparse
import os
import time
from datetime import datetime, timezone

from db import list_active_workspaces
from followup_job import run_for_workspace
from workspace_context import WorkspaceContext, resolve_workspace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=6.0, help="Intervalo entre execucoes (horas)")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--once", action="store_true", help="Roda uma vez e sai")
    parser.add_argument("--all", action="store_true", help="Todos os workspaces ativos")
    parser.add_argument("--workspace", type=str, help="Slug do workspace")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    interval_sec = max(60.0, args.hours * 3600)

    while True:
        now = datetime.now(timezone.utc).isoformat()
        print(f"\n[{now}] Iniciando follow-up job...")

        workspaces: list[WorkspaceContext] = []
        try:
            if args.all:
                workspaces = [WorkspaceContext.from_row(r) for r in list_active_workspaces()]
            else:
                slug = args.workspace or os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
                ws = resolve_workspace(slug=slug)
                if not ws:
                    print(f"Workspace '{slug}' nao encontrado")
                else:
                    workspaces = [ws]

            for ws in workspaces:
                run_for_workspace(ws, limit=args.limit, dry_run=args.dry_run)
        except Exception as exc:
            print(f"Erro no job: {exc}")

        if args.once:
            break
        print(f"Proxima execucao em {args.hours}h")
        time.sleep(interval_sec)


if __name__ == "__main__":
    main()
