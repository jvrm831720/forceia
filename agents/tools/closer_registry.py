"""
ForceIA P2 — Tools formais do Closer (estilo bind_tools via META).

O LLM não precisa de function-calling nativo: declara tool calls no META
(ex.: {"tools":[{"name":"schedule_meeting","args":{...}}]}) e o runtime executa.
"""

from __future__ import annotations

from typing import Any, Callable

ToolHandler = Callable[..., dict[str, Any]]

CLOSER_TOOLS: list[dict[str, Any]] = [
    {
        "name": "schedule_meeting",
        "description": "Agenda reunião no calendário (Composio/GCal) e devolve link.",
        "parameters": {
            "start_iso": "ISO-8601 início (obrigatório)",
            "end_iso": "ISO-8601 fim (opcional)",
            "title": "Título da reunião",
            "attendee_email": "Email do convidado",
        },
        "meta_aliases": ("schedule", "calendar_request", "schedule_meeting"),
    },
    {
        "name": "send_proposal",
        "description": "Gera link de proposta/pagamento alinhado ao playbook.",
        "parameters": {
            "plan": "Nome do plano",
            "amount": "Faixa ou valor",
        },
        "meta_aliases": ("proposal", "send_proposal", "payment_link"),
    },
    {
        "name": "request_handoff",
        "description": "Transfere a conversa para um humano (pausa o agente).",
        "parameters": {"reason": "Motivo do handoff"},
        "meta_aliases": ("handoff",),
    },
]


def list_closer_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        }
        for t in CLOSER_TOOLS
    ]


def tool_specs_for_prompt() -> str:
    lines = [
        "## Tools do Closer (declare no META quando for usar)",
        'Formato: "tools":[{"name":"schedule_meeting","args":{"start_iso":"..."}}]',
        "Disponíveis:",
    ]
    for t in CLOSER_TOOLS:
        params = ", ".join(f"{k}" for k in (t.get("parameters") or {}))
        lines.append(f"- {t['name']}({params}): {t['description']}")
    return "\n".join(lines)


def _run_schedule(
    *,
    workspace_id: str,
    workspace_slug: str,
    lead: dict,
    args: dict,
    playbook: dict | None,
) -> dict[str, Any]:
    from closer_tools import schedule_meeting

    start = args.get("start_iso") or args.get("start") or args.get("when")
    if not start:
        return {"success": False, "error": "start_iso obrigatório"}
    return schedule_meeting(
        workspace_id,
        title=args.get("title") or f"Reunião — {lead.get('name') or lead.get('phone')}",
        start_iso=str(start),
        end_iso=args.get("end_iso") or args.get("end"),
        attendee_email=args.get("attendee_email") or args.get("email") or lead.get("email"),
        description=args.get("description") or f"Lead {lead.get('phone')}",
    )


def _run_proposal(
    *,
    workspace_id: str,
    workspace_slug: str,
    lead: dict,
    args: dict,
    playbook: dict | None,
) -> dict[str, Any]:
    from closer_tools import generate_proposal_link

    return generate_proposal_link(
        workspace_slug=workspace_slug,
        lead=lead,
        playbook=playbook,
        plan=args.get("plan"),
        amount=args.get("amount"),
    )


def _run_handoff(
    *,
    workspace_id: str,
    workspace_slug: str,
    lead: dict,
    args: dict,
    playbook: dict | None,
) -> dict[str, Any]:
    return {
        "success": True,
        "handoff": True,
        "reason": args.get("reason") or "closer tool request_handoff",
    }


_HANDLERS: dict[str, ToolHandler] = {
    "schedule_meeting": _run_schedule,
    "send_proposal": _run_proposal,
    "request_handoff": _run_handoff,
}


def _legacy_meta_to_calls(meta: dict) -> list[dict[str, Any]]:
    """Converte META legado (schedule/proposal/handoff) em tool calls."""
    calls: list[dict[str, Any]] = []
    if not meta:
        return calls
    if isinstance(meta.get("tools"), list):
        for t in meta["tools"]:
            if isinstance(t, dict) and t.get("name"):
                calls.append(
                    {
                        "name": str(t["name"]),
                        "args": t.get("args") if isinstance(t.get("args"), dict) else {},
                    }
                )
    # aliases legados
    from closer_tools import parse_proposal_from_meta, parse_schedule_from_meta

    sched = parse_schedule_from_meta(meta)
    if sched and not any(c["name"] == "schedule_meeting" for c in calls):
        calls.append({"name": "schedule_meeting", "args": sched})
    prop = parse_proposal_from_meta(meta)
    if prop and not any(c["name"] == "send_proposal" for c in calls):
        calls.append(
            {
                "name": "send_proposal",
                "args": {"plan": prop.get("plan"), "amount": prop.get("amount")},
            }
        )
    if meta.get("handoff") and not any(c["name"] == "request_handoff" for c in calls):
        calls.append(
            {
                "name": "request_handoff",
                "args": {"reason": meta.get("notes") or meta.get("intent") or "meta.handoff"},
            }
        )
    return calls


def execute_tool_calls_from_meta(
    *,
    workspace_id: str,
    workspace_slug: str,
    lead: dict,
    meta: dict,
    playbook: dict | None = None,
) -> dict[str, Any]:
    """Executa tools declaradas no META (+ aliases legados)."""
    calls = _legacy_meta_to_calls(meta or {})
    results: list[dict[str, Any]] = []
    notes: list[str] = []
    handoff = False
    calendar = None
    proposal = None

    for call in calls:
        name = str(call.get("name") or "").strip()
        args = call.get("args") if isinstance(call.get("args"), dict) else {}
        handler = _HANDLERS.get(name)
        if not handler:
            results.append({"name": name, "success": False, "error": "unknown tool"})
            continue
        try:
            out = handler(
                workspace_id=workspace_id,
                workspace_slug=workspace_slug,
                lead=lead,
                args=args,
                playbook=playbook,
            )
        except Exception as exc:
            results.append({"name": name, "success": False, "error": str(exc)[:200]})
            continue
        results.append({"name": name, "success": bool(out.get("success", True)), "result": out})
        if name == "schedule_meeting":
            calendar = out
            if out.get("event_link"):
                notes.append(f"Link da reunião: {out['event_link']}")
        elif name == "send_proposal":
            proposal = out
            if out.get("url"):
                notes.append(f"Link da proposta/pagamento: {out['url']}")
            elif out.get("summary"):
                notes.append(str(out["summary"]))
        elif name == "request_handoff" and out.get("handoff"):
            handoff = True

    return {
        "calls": results,
        "calendar": calendar,
        "proposal": proposal,
        "notes_for_reply": notes,
        "handoff": handoff,
    }
