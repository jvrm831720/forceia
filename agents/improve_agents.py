"""
ForceIA - Job de auto-melhoria assistida (gate humano)

  python improve_agents.py --workspace default
  python improve_agents.py --workspace default --mode hybrid
  python improve_agents.py --workspace default --mode spin --export-prefs /tmp/prefs.json
  python improve_agents.py --apply <suggestion_id>
  python improve_agents.py --list-pending

Fluxo (STaR + SPIN):
  1) Amostra won/lost no Supabase
  2) Pares preferencia SPIN + racionalizacao STaR
  3) LLM coach gera insights + prompts sugeridos
  4) Grava prompt_suggestions (pending)
  5) Humano aprova e aplica (override ativo)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime

from db import (
    create_learning_run,
    finish_learning_run,
    get_messages_for_lead,
    get_prompt_suggestion,
    get_workspace_by_slug,
    insert_prompt_suggestion,
    list_active_workspaces,
    list_leads_by_stage,
    list_prompt_suggestions,
    update_prompt_suggestion,
    upsert_prompt_override,
)
from dotenv import load_dotenv
from learning import (
    AGENTS,
    collect_current_prompts,
    ensure_meta_protocol,
    export_preference_dataset,
    run_hybrid_learning,
    sample_outcomes,
)
from logging_config import get_logger
from openai import OpenAI
from workspace_context import WorkspaceContext, resolve_workspace

load_dotenv()
log = get_logger("forceia.learning")


def _client_for(ws: WorkspaceContext | None) -> OpenAI:
    key = (ws.openai_api_key if ws else None) or os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY ausente")
    return OpenAI(api_key=key)


def run_learning_for_workspace(
    ws: WorkspaceContext,
    per_outcome: int = 8,
    *,
    mode: str = "hybrid",
    export_prefs_path: str | None = None,
) -> dict:
    """
    mode: hybrid | spin | star | classic
      hybrid = SPIN pairs + STaR rationalization (recomendado)
      spin   = self-play preference pairs only
      star   = rationalize lost only
      classic = won/lost samples only (legado)
    """
    run = create_learning_run(ws.id)
    run_id = run.get("id")
    try:
        won, lost = sample_outcomes(
            list_leads_by_stage=list_leads_by_stage,
            get_messages_for_lead=get_messages_for_lead,
            workspace_id=ws.id,
            per_outcome=per_outcome,
        )
        if len(won) + len(lost) < 2:
            finish_learning_run(
                run_id,
                status="empty",
                won_sampled=len(won),
                lost_sampled=len(lost),
                summary="Amostras insuficientes (precisa de leads won/lost com historico).",
            )
            return {"status": "empty", "won": len(won), "lost": len(lost)}

        current = collect_current_prompts()
        client = _client_for(ws)
        model = ws.gpt_model or os.getenv("GPT_MODEL", "gpt-4o-mini")
        analyst_model = os.getenv("LEARNING_MODEL") or model

        analysis = run_hybrid_learning(
            client,
            model=analyst_model,
            won=won,
            lost=lost,
            current_prompts=current,
            mode=mode,
        )
        meta = analysis.pop("_meta", {}) or {}

        if export_prefs_path and mode in ("hybrid", "spin"):
            from learning import build_preference_pairs
            from pathlib import Path

            pairs = build_preference_pairs(won, lost, max_pairs=20)
            dataset = export_preference_dataset(pairs)
            Path(export_prefs_path).write_text(
                __import__("json").dumps(dataset, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.info("preference dataset exported", extra={"event": export_prefs_path})

        suggestions_out = []
        for sug in analysis.get("suggestions") or []:
            agent = (sug.get("agent") or "").strip().lower()
            if agent not in AGENTS:
                continue
            suggested = ensure_meta_protocol(sug.get("suggested_prompt") or "")
            if len(suggested) < 80:
                continue
            row = insert_prompt_suggestion(
                learning_run_id=run_id,
                workspace_id=ws.id,
                agent=agent,
                status="pending",
                title=sug.get("title") or f"Melhoria {agent}",
                rationale=sug.get("rationale") or "",
                insights=analysis.get("insights") or [],
                metrics={
                    "won_sampled": len(won),
                    "lost_sampled": len(lost),
                    "mode": mode,
                    "spin_pairs": meta.get("pairs"),
                    "star_rationalizations": meta.get("rationalizations"),
                    "spin_lessons": meta.get("spin_lessons"),
                    "source": sug.get("source") or mode,
                },
                current_prompt=current.get(agent, ""),
                suggested_prompt=suggested,
                diff_summary=sug.get("diff_summary") or "",
            )
            suggestions_out.append(row.get("id") or agent)

        summary = analysis.get("summary") or f"{len(suggestions_out)} sugestoes geradas"
        if meta:
            summary = f"[{mode}] {summary} | pairs={meta.get('pairs')} rat={meta.get('rationalizations')}"
        finish_learning_run(
            run_id,
            status="completed",
            won_sampled=len(won),
            lost_sampled=len(lost),
            summary=summary,
        )
        log.info(
            "learning completed",
            extra={
                "workspace": ws.slug,
                "event": f"mode={mode} suggestions={len(suggestions_out)}",
            },
        )
        return {
            "status": "completed",
            "run_id": run_id,
            "mode": mode,
            "won": len(won),
            "lost": len(lost),
            "meta": meta,
            "suggestions": suggestions_out,
            "summary": summary,
        }
    except Exception as exc:
        finish_learning_run(run_id, status="failed", error=str(exc))
        log.warning("learning failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


def approve(suggestion_id: str, note: str | None = None) -> dict:
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise SystemExit(f"Sugestao {suggestion_id} nao encontrada")
    return update_prompt_suggestion(
        suggestion_id,
        status="approved",
        reviewed_at=datetime.now(UTC).isoformat(),
        reviewed_note=note,
    )


def reject(suggestion_id: str, note: str | None = None) -> dict:
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise SystemExit(f"Sugestao {suggestion_id} nao encontrada")
    return update_prompt_suggestion(
        suggestion_id,
        status="rejected",
        reviewed_at=datetime.now(UTC).isoformat(),
        reviewed_note=note,
    )


def apply_suggestion(suggestion_id: str, *, also_write_file: bool = False) -> dict:
    """Ativa override no banco. Opcionalmente grava o arquivo .md (global)."""
    row = get_prompt_suggestion(suggestion_id)
    if not row:
        raise SystemExit(f"Sugestao {suggestion_id} nao encontrada")
    if row.get("status") not in ("approved", "pending"):
        if row.get("status") != "approved":
            raise SystemExit(
                f"Status atual={row.get('status')}. Aprove antes (--approve) ou use status approved."
            )

    agent = row["agent"]
    content = ensure_meta_protocol(row["suggested_prompt"])
    override = upsert_prompt_override(
        agent,
        content,
        workspace_id=row.get("workspace_id"),
        source_suggestion_id=suggestion_id,
    )

    if also_write_file and not row.get("workspace_id"):
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        path = root / "config" / "prompts" / f"{agent}.md"
        path.write_text(content, encoding="utf-8")
        print(f"Arquivo atualizado: {path}")

    update_prompt_suggestion(
        suggestion_id,
        status="applied",
        reviewed_at=datetime.now(UTC).isoformat(),
    )
    return override


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ForceIA auto-melhoria assistida (STaR + SPIN)"
    )
    parser.add_argument("--workspace", type=str, help="Slug do workspace")
    parser.add_argument("--all", action="store_true", help="Todos os workspaces")
    parser.add_argument("--per-outcome", type=int, default=8)
    parser.add_argument(
        "--mode",
        type=str,
        default="hybrid",
        choices=["hybrid", "spin", "star", "classic"],
        help="hybrid=SPIN+STaR (padrao) | spin | star | classic",
    )
    parser.add_argument(
        "--export-prefs",
        type=str,
        default=None,
        metavar="PATH",
        help="Exporta dataset preferencia SPIN (JSON) para auditoria/treino",
    )
    parser.add_argument("--list-pending", action="store_true")
    parser.add_argument("--approve", type=str, metavar="ID")
    parser.add_argument("--reject", type=str, metavar="ID")
    parser.add_argument("--apply", type=str, metavar="ID")
    parser.add_argument("--write-file", action="store_true", help="Com --apply, grava config/prompts")
    parser.add_argument("--note", type=str, default=None)
    args = parser.parse_args()

    if args.list_pending:
        rows = list_prompt_suggestions(status="pending")
        if not rows:
            print("Nenhuma sugestao pending.")
            return
        for r in rows:
            print(
                f"{r.get('id')} | {r.get('agent')} | {r.get('title')} | ws={r.get('workspace_id')}"
            )
        return

    if args.approve:
        row = approve(args.approve, note=args.note)
        print("Aprovado:", row.get("id"), row.get("agent"))
        return

    if args.reject:
        row = reject(args.reject, note=args.note)
        print("Rejeitado:", row.get("id"))
        return

    if args.apply:
        row = get_prompt_suggestion(args.apply)
        if row and row.get("status") == "pending":
            approve(args.apply, note=args.note or "auto-approve on apply")
        override = apply_suggestion(args.apply, also_write_file=args.write_file)
        print("Aplicado override:", override.get("agent"), override.get("id"))
        return

    workspaces: list[WorkspaceContext] = []
    if args.all:
        for r in list_active_workspaces():
            workspaces.append(WorkspaceContext.from_row(r))
    else:
        slug = args.workspace or os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
        ws = resolve_workspace(slug=slug)
        if not ws:
            row = get_workspace_by_slug(slug)
            if not row:
                print(f"Workspace '{slug}' nao encontrado")
                sys.exit(1)
            ws = WorkspaceContext.from_row(row)
        workspaces = [ws]

    for ws in workspaces:
        print(f"\n=== Learning [{args.mode}]: {ws.slug} ===")
        result = run_learning_for_workspace(
            ws,
            per_outcome=args.per_outcome,
            mode=args.mode,
            export_prefs_path=args.export_prefs,
        )
        print(result)


if __name__ == "__main__":
    main()
