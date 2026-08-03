"""
ForceIA - Scheduler simples em processo (alternativa ao cron)

Roda o follow-up job em intervalo fixo.

  python scheduler.py
  python scheduler.py --hours 6 --days 5
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

from followup_job import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=6.0, help="Intervalo entre execucoes (horas)")
    parser.add_argument("--days", type=int, default=5, help="Dias de inatividade")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--once", action="store_true", help="Roda uma vez e sai")
    args = parser.parse_args()

    interval_sec = max(60.0, args.hours * 3600)

    while True:
        now = datetime.now(timezone.utc).isoformat()
        print(f"\n[{now}] Iniciando follow-up job...")
        try:
            run(days=args.days, limit=args.limit, dry_run=False)
        except Exception as exc:
            print(f"Erro no job: {exc}")
        if args.once:
            break
        print(f"Proxima execucao em {args.hours}h")
        time.sleep(interval_sec)


if __name__ == "__main__":
    main()
