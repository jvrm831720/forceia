"""
ForceIA - Validacao / smoke test do MVP

Checa imports, schema esperado, workspace e (opcional) OpenAI/Supabase.

  cd agents
  python validate_mvp.py
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# Garante que agents/ esta no path e .env da raiz e carregado
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
load_dotenv()

OK = 0
WARN = 0
FAIL = 0


def ok(msg: str) -> None:
    global OK
    OK += 1
    print(f"  [OK]   {msg}")


def warn(msg: str) -> None:
    global WARN
    WARN += 1
    print(f"  [WARN] {msg}")


def fail(msg: str) -> None:
    global FAIL
    FAIL += 1
    print(f"  [FAIL] {msg}")


def check_imports() -> None:
    print("\n== Imports ==")
    modules = [
        "db",
        "prompts",
        "state_machine",
        "workspace_context",
        "run_sdr",
        "webhook_server",
        "followup_job",
        "scheduler",
        "twenty_client",
        "sync_twenty_job",
        "create_workspace",
    ]
    for name in modules:
        try:
            importlib.import_module(name)
            ok(f"import {name}")
        except Exception as exc:
            fail(f"import {name}: {exc}")


def check_env() -> None:
    print("\n== Ambiente ==")
    if os.getenv("SUPABASE_URL") and (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    ):
        ok("SUPABASE_URL + key definidos")
    else:
        fail("Falta SUPABASE_URL e/ou SUPABASE_SERVICE_ROLE_KEY no .env")

    if os.getenv("OPENAI_API_KEY"):
        ok("OPENAI_API_KEY definido")
    else:
        warn("OPENAI_API_KEY ausente (agentes nao geram resposta)")

    if os.getenv("TWENTY_API_URL") and os.getenv("TWENTY_API_KEY"):
        ok("Twenty global configurado")
    else:
        warn("Twenty global nao configurado (opcional; pode ser por workspace)")

    if os.getenv("EVOLUTION_API_KEY"):
        ok("EVOLUTION_API_KEY definido")
    else:
        warn("EVOLUTION_API_KEY ausente (fallback forceia-dev-key)")


def check_supabase() -> None:
    print("\n== Supabase ==")
    if not os.getenv("SUPABASE_URL"):
        warn("Skip — sem SUPABASE_URL")
        return
    try:
        from db import get_client, list_active_workspaces

        client = get_client()
        for table in ("workspaces", "leads", "messages", "events"):
            try:
                client.table(table).select("*", count="exact").limit(1).execute()
                ok(f"tabela {table} acessivel")
            except Exception as exc:
                fail(f"tabela {table}: {exc}")

        wss = list_active_workspaces()
        if wss:
            ok(f"{len(wss)} workspace(s) ativo(s): " + ", ".join(w.get("slug", "?") for w in wss))
        else:
            warn("Nenhum workspace ativo — rode: python create_workspace.py --name Default --slug default")
    except Exception as exc:
        fail(f"conexao Supabase: {exc}")


def check_state_machine() -> None:
    print("\n== State machine ==")
    from state_machine import can_transition, detect_stage_from_reply, next_agent_for_stage

    assert next_agent_for_stage("sdr") == "sdr"
    assert next_agent_for_stage("qualified") == "closer"
    assert next_agent_for_stage("followup") == "followup"
    assert can_transition("sdr", "qualified")
    assert detect_stage_from_reply("Lead [QUALIFICADO] ok", "sdr") == "qualified"
    assert detect_stage_from_reply("sem tag", "sdr") == "sdr"
    ok("transicoes e tags basicas")


def check_prompts() -> None:
    print("\n== Prompts ==")
    from prompts import load_prompt

    for agent in ("sdr", "closer", "followup"):
        text = load_prompt(agent)
        if text and len(text) > 20:
            ok(f"prompt {agent} ({len(text)} chars)")
        else:
            fail(f"prompt {agent} vazio")


def main() -> None:
    print("ForceIA MVP — validacao")
    check_imports()
    check_env()
    check_state_machine()
    check_prompts()
    check_supabase()
    print(f"\n== Resultado: {OK} ok, {WARN} warn, {FAIL} fail ==")
    if FAIL:
        sys.exit(1)
    print("Pronto para teste manual (run_sdr / webhook).")


if __name__ == "__main__":
    main()
