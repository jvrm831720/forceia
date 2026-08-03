"""
ForceIA - Grafo de agentes (LangGraph).

Substitui a orquestracao linear caseira por um StateGraph com:
- estado tipado do funil SDR → qualified → closer → followup → won/lost
- checkpoints por lead (thread_id = workspace:phone)
- retries no no de geracao (falhas de LLM/rede)

API publica:
  invoke_turn(workspace, phone, text, *, send=True, message_id=None) -> str

Requer: pip install langgraph langchain-core
Se langgraph nao estiver instalado, run_sdr cai no caminho legado.
"""

from __future__ import annotations

import operator
import os
from typing import Annotated, Any, TypedDict

from state_machine import STAGES, can_transition, next_agent_for_stage


class AgentState(TypedDict, total=False):
    workspace_id: str
    workspace_slug: str
    phone: str
    message_id: str | None
    send_whatsapp: bool
    stage: str
    agent: str
    new_stage: str
    user_message: str
    history: list[dict]
    lead: dict
    raw_reply: str
    visible_reply: str
    meta: dict
    error: str | None
    retry_count: int
    events: Annotated[list[str], operator.add]


def _langgraph_available() -> bool:
    try:
        import langgraph  # noqa: F401
        return True
    except ImportError:
        return False


def build_sales_graph(checkpointer: Any = None):
    from langgraph.graph import END, StateGraph
    try:
        from langgraph.types import RetryPolicy
    except ImportError:
        RetryPolicy = None  # type: ignore

    graph = StateGraph(AgentState)
    graph.add_node("prepare", _node_prepare)
    if RetryPolicy is not None:
        graph.add_node(
            "generate",
            _node_generate,
            retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0),
        )
    else:
        graph.add_node("generate", _node_generate)
    graph.add_node("parse", _node_parse)
    graph.add_node("route", _node_route)
    graph.add_node("persist", _node_persist)

    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "generate")
    graph.add_edge("generate", "parse")
    graph.add_edge("parse", "route")
    graph.add_edge("route", "persist")
    graph.add_edge("persist", END)

    compile_kwargs: dict[str, Any] = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer
    return graph.compile(**compile_kwargs)


def _default_checkpointer():
    try:
        from langgraph.checkpoint.memory import MemorySaver
    except ImportError:
        return None
    sqlite_path = os.getenv("FORCEIA_GRAPH_SQLITE", "").strip()
    if sqlite_path:
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
            import sqlite3
            conn = sqlite3.connect(sqlite_path, check_same_thread=False)
            return SqliteSaver(conn)
        except Exception:
            pass
    return MemorySaver()


_compiled = None


def get_compiled_graph():
    global _compiled
    if _compiled is None:
        if not _langgraph_available():
            raise RuntimeError("langgraph nao instalado. pip install 'langgraph>=0.2.0'")
        _compiled = build_sales_graph(checkpointer=_default_checkpointer())
    return _compiled


def _node_prepare(state: AgentState) -> dict:
    from db import get_history, get_lead_by_phone, log_event, upsert_lead
    workspace_id = state["workspace_id"]
    phone = state["phone"]
    lead = get_lead_by_phone(workspace_id, phone)
    events: list[str] = []
    if not lead:
        lead = upsert_lead(workspace_id, phone, stage="sdr", bant={})
        log_event("lead_created", {"phone": phone}, lead_id=lead.get("id"), workspace_id=workspace_id)
        events.append("lead_created")
    stage = lead.get("stage") or "sdr"
    if stage not in STAGES:
        stage = "sdr"
    agent = next_agent_for_stage(stage)
    if stage in ("won", "lost"):
        agent = "closer" if stage == "won" else "sdr"
    history_rows = get_history(lead["id"], limit=24)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]
    return {
        "lead": lead, "stage": stage, "agent": agent, "history": history,
        "meta": {}, "error": None, "retry_count": state.get("retry_count") or 0, "events": events,
    }


def _node_generate(state: AgentState) -> dict:
    from workspace_context import resolve_workspace
    from run_sdr import generate_reply
    ws = resolve_workspace(workspace_id=state["workspace_id"])
    if ws is None:
        ws = resolve_workspace(slug=state.get("workspace_slug") or "default")
    if ws is None:
        raise RuntimeError("workspace nao resolvido no no generate")
    raw = generate_reply(
        ws, state["agent"], state.get("history") or [], state["user_message"],
        lead=state.get("lead") or {},
    )
    return {"raw_reply": raw, "events": ["generated"]}


def _node_parse(state: AgentState) -> dict:
    from intelligence import (
        apply_meta_to_lead_fields, is_bant_qualified, split_reply_and_meta, stage_from_meta_or_tags,
    )
    from utils import strip_control_blocks
    raw = state.get("raw_reply") or ""
    visible, meta = split_reply_and_meta(raw)
    reply = strip_control_blocks(visible)
    lead = state.get("lead") or {}
    field_updates = apply_meta_to_lead_fields(lead, meta, state.get("user_message") or "")
    stage = state.get("stage") or "sdr"
    new_stage = stage_from_meta_or_tags(raw, meta, stage, can_transition)
    bant = field_updates.get("bant") or lead.get("bant")
    if stage == "sdr" and is_bant_qualified(bant) and new_stage == stage:
        if can_transition(stage, "qualified"):
            new_stage = "qualified"
    if meta.get("handoff"):
        if "vou te conectar" not in reply.lower() and "humano" not in reply.lower():
            reply = ((reply + "\n\n" if reply else "") + "Vou acionar alguém do time para te atender em seguida, combinado?").strip()
    updated_lead = dict(lead)
    for k, v in field_updates.items():
        if k == "metadata":
            meta_lead = dict(updated_lead.get("metadata") or {})
            meta_lead.update(v or {})
            updated_lead["metadata"] = meta_lead
        else:
            updated_lead[k] = v
    return {
        "visible_reply": reply, "meta": meta or {}, "new_stage": new_stage,
        "lead": updated_lead, "events": [f"parsed:{stage}->{new_stage}"],
    }


def _node_route(state: AgentState) -> dict:
    current = state.get("stage") or "sdr"
    target = state.get("new_stage") or current
    if target != current and not can_transition(current, target):
        return {"new_stage": current, "events": [f"blocked:{current}->{target}"]}
    return {"events": [f"routed:{target}"]}


def _node_persist(state: AgentState) -> dict:
    from db import (
        add_message, get_lead_by_phone, log_event, mark_message_processed,
        merge_metadata, set_stage, upsert_lead,
    )
    from intelligence import bant_score
    from workspace_context import resolve_workspace
    from run_sdr import send_whatsapp, sync_twenty

    workspace_id = state["workspace_id"]
    phone = state["phone"]
    lead = state.get("lead") or {}
    stage = state.get("stage") or "sdr"
    new_stage = state.get("new_stage") or stage
    reply = state.get("visible_reply") or ""
    agent = state.get("agent") or "sdr"
    user_message = state.get("user_message") or ""
    meta = state.get("meta") or {}
    events_out: list[str] = []
    lead_id = lead.get("id")
    if lead_id:
        add_message(lead_id, "user", user_message)
        add_message(lead_id, "assistant", reply, agent=agent)
    message_id = state.get("message_id")
    if message_id:
        mark_message_processed(workspace_id, message_id, lead_id=lead_id)
    if meta.get("handoff"):
        log_event("handoff_requested", {"phone": phone, "reason": meta.get("intent") or meta.get("notes")}, lead_id=lead_id, workspace_id=workspace_id)
        events_out.append("handoff")
    field_keys = ("name", "company", "email", "bant")
    upsert_kwargs = {k: lead[k] for k in field_keys if k in lead and lead[k] is not None}
    if lead.get("metadata"):
        merge_metadata(workspace_id, phone, lead["metadata"])
    ws = resolve_workspace(workspace_id=workspace_id) or resolve_workspace(slug=state.get("workspace_slug") or "default")
    if new_stage != stage:
        lead = set_stage(workspace_id, phone, new_stage)
        other = {k: v for k, v in upsert_kwargs.items() if k != "stage"}
        if other:
            lead = upsert_lead(workspace_id, phone, **other)
        log_event("stage_changed", {"from": stage, "to": new_stage, "bant_score": bant_score(lead.get("bant")), "source": "langgraph"}, lead_id=lead.get("id"), workspace_id=workspace_id)
        events_out.append(f"stage:{stage}->{new_stage}")
        if ws:
            sync_twenty(ws, lead)
    else:
        if upsert_kwargs:
            lead = upsert_lead(workspace_id, phone, **upsert_kwargs)
        else:
            upsert_lead(workspace_id, phone)
        meta_lead = (lead or {}).get("metadata") or {}
        if not meta_lead.get("twenty_person_id") and ws:
            lead = get_lead_by_phone(workspace_id, phone) or lead
            sync_twenty(ws, lead)
    if state.get("send_whatsapp") and reply and ws:
        try:
            send_whatsapp(ws, phone, reply)
            events_out.append("whatsapp_sent")
        except Exception as exc:
            log_event("whatsapp_send_error", {"error": str(exc)}, lead_id=lead.get("id") if lead else lead_id, workspace_id=workspace_id)
            events_out.append("whatsapp_error")
    return {"lead": lead, "visible_reply": reply, "events": events_out}


def thread_id_for(workspace_id: str, phone: str) -> str:
    return f"{workspace_id}:{phone}"


def invoke_turn(
    *,
    workspace_id: str,
    phone: str,
    text: str,
    workspace_slug: str = "default",
    send: bool = True,
    message_id: str | None = None,
) -> str:
    app = get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id_for(workspace_id, phone)}}
    initial: AgentState = {
        "workspace_id": workspace_id,
        "workspace_slug": workspace_slug,
        "phone": phone,
        "user_message": text,
        "message_id": message_id,
        "send_whatsapp": send,
        "events": [],
        "retry_count": 0,
    }
    final = app.invoke(initial, config)
    return final.get("visible_reply") or ""


def graph_enabled() -> bool:
    flag = os.getenv("FORCEIA_USE_GRAPH", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return _langgraph_available()
