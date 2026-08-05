"""
ForceIA - Grafo de agentes (LangGraph) + traces Langfuse.

prepare → generate (retry) → parse → actions → route → persist
Checkpoints por lead; observabilidade em cada no.

P0 (wired):
- enrichment + intent + lead_score no prepare/parse
- guardrails no parse
- A/B de prompts no generate
- handoff completo no persist
- closer_tools (calendar/proposta) no actions
"""

from __future__ import annotations

import operator
import os
from contextlib import contextmanager
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
    action_results: list
    reply_suffix: str | None
    error: str | None
    retry_count: int
    events: Annotated[list[str], operator.add]
    _trace: Any
    # P0
    ab_variant: str
    base_prompt: str | None
    intent_info: dict
    score_info: dict
    handoff_done: bool


def _langgraph_available() -> bool:
    try:
        import langgraph  # noqa: F401
        return True
    except ImportError:
        return False


@contextmanager
def _nullspan():
    yield None


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
    graph.add_node("actions", _node_actions)
    graph.add_node("route", _node_route)
    graph.add_node("persist", _node_persist)

    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "generate")
    graph.add_edge("generate", "parse")
    graph.add_edge("parse", "actions")
    graph.add_edge("actions", "route")
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


def _apply_intent_to_lead(lead: dict, intent_info: dict) -> dict:
    out = dict(lead)
    meta = dict(out.get("metadata") or {})
    intent = (intent_info or {}).get("intent") or "unknown"
    conf = (intent_info or {}).get("confidence")
    meta["buying_intent"] = intent
    meta["intent_class"] = intent
    if conf is not None:
        meta["intent_confidence"] = conf
    meta["intent_signals"] = (intent_info or {}).get("signals") or []
    meta["intent_source"] = (intent_info or {}).get("source") or "lexical"
    out["metadata"] = meta
    return out


def _node_prepare(state: AgentState) -> dict:
    from db import get_history, get_lead_by_phone, log_event, merge_metadata, upsert_lead
    from ab_testing import ensure_lead_variant
    from enrichment import apply_enrichment_to_lead, enrich_lead
    from intent import detect_buying_intent
    from lead_score import apply_score_to_lead, compute_lead_score

    workspace_id = state["workspace_id"]
    phone = state["phone"]
    user_message = state.get("user_message") or ""
    lead = get_lead_by_phone(workspace_id, phone)
    events: list[str] = []

    if not lead:
        lead = upsert_lead(workspace_id, phone, stage="sdr", bant={})
        log_event("lead_created", {"phone": phone}, lead_id=lead.get("id"), workspace_id=workspace_id)
        events.append("lead_created")

    # --- A/B variant (estável por lead) ---
    ab_meta, ab_variant = ensure_lead_variant(lead, workspace_id)
    if ab_meta.get("ab_variant") != (lead.get("metadata") or {}).get("ab_variant"):
        merge_metadata(workspace_id, phone, {"ab_variant": ab_variant})
        lead = dict(lead)
        meta = dict(lead.get("metadata") or {})
        meta["ab_variant"] = ab_variant
        lead["metadata"] = meta
        events.append(f"ab_variant:{ab_variant}")

    # --- Enrichment pré-mensagem ---
    try:
        enr = enrich_lead(workspace_id, lead, user_text=user_message)
        if not enr.get("skipped") and enr.get("changed"):
            lead = apply_enrichment_to_lead(lead, enr)
            fields = enr.get("fields") or {}
            if fields:
                upsert_lead(workspace_id, phone, **{k: v for k, v in fields.items() if v})
            if enr.get("enrichment"):
                merge_metadata(
                    workspace_id,
                    phone,
                    {
                        "enrichment": enr["enrichment"],
                        "enrichment_status": "done",
                    },
                )
            events.append("enriched")
    except Exception:
        events.append("enrich_error")

    # --- Intent lexical (pré-LLM; META refine no parse) ---
    intent_info = detect_buying_intent(user_message, history=None, meta={})
    lead = _apply_intent_to_lead(lead, intent_info)

    # --- Lead score ---
    history_rows = get_history(lead["id"], limit=24) if lead.get("id") else []
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]
    score_info = compute_lead_score(lead, message_count=len(history_rows))
    lead = apply_score_to_lead(lead, score_info)

    stage = lead.get("stage") or "sdr"
    if stage not in STAGES:
        stage = "sdr"
    agent = next_agent_for_stage(stage)
    if stage in ("won", "lost"):
        agent = "closer" if stage == "won" else "sdr"

    # Intent ready_to_buy em qualified+ → preferir closer
    if intent_info.get("intent") == "ready_to_buy" and stage in ("qualified", "closer", "sdr"):
        if stage == "sdr" and score_info.get("score", 0) >= 60:
            pass  # auto-qualify no parse
        elif stage in ("qualified", "closer"):
            agent = "closer"

    trace = state.get("_trace")
    if trace is not None:
        try:
            with trace.span(
                "prepare",
                stage=stage,
                agent=agent,
                lead_id=lead.get("id"),
                history_len=len(history),
                ab_variant=ab_variant,
                intent=intent_info.get("intent"),
                score=score_info.get("score"),
            ):
                pass
            trace.update(
                metadata={
                    "stage": stage,
                    "agent": agent,
                    "lead_id": lead.get("id"),
                    "ab_variant": ab_variant,
                    "intent": intent_info.get("intent"),
                    "lead_score": score_info.get("score"),
                    "lead_tier": score_info.get("tier"),
                }
            )
        except Exception:
            pass

    return {
        "lead": lead,
        "stage": stage,
        "agent": agent,
        "history": history,
        "meta": {},
        "error": None,
        "retry_count": state.get("retry_count") or 0,
        "events": events,
        "ab_variant": ab_variant,
        "intent_info": intent_info,
        "score_info": score_info,
        "base_prompt": None,
        "handoff_done": False,
    }


def _node_generate(state: AgentState) -> dict:
    from workspace_context import resolve_workspace
    from run_sdr import generate_reply
    from ab_testing import ab_enabled, record_ab_exposure, resolve_prompt_for_variant
    from prompts import load_prompt

    ws = resolve_workspace(workspace_id=state["workspace_id"])
    if ws is None:
        ws = resolve_workspace(slug=state.get("workspace_slug") or "default")
    if ws is None:
        raise RuntimeError("workspace nao resolvido no no generate")

    agent = state.get("agent") or "sdr"
    ab_variant = (state.get("ab_variant") or "A").upper()
    base_prompt = state.get("base_prompt")
    prompt_source = "state"

    if base_prompt is None:
        if ab_enabled():
            base_prompt, prompt_source = resolve_prompt_for_variant(
                agent=agent,
                variant=ab_variant,
                workspace_id=state["workspace_id"],
                load_prompt_fn=load_prompt,
            )
        else:
            base_prompt = load_prompt(agent, workspace_id=state["workspace_id"])
            prompt_source = "control_A"

    lead = state.get("lead") or {}
    record_ab_exposure(
        workspace_id=state["workspace_id"],
        lead_id=lead.get("id"),
        variant=ab_variant,
        agent=agent,
        source=prompt_source,
    )

    trace = state.get("_trace")
    ctx = (
        trace.span("generate", agent=agent, stage=state.get("stage"), ab=ab_variant, source=prompt_source)
        if trace
        else _nullspan()
    )
    with ctx:
        raw = generate_reply(
            ws,
            agent,
            state.get("history") or [],
            state["user_message"],
            lead=lead,
            trace=trace,
            base_prompt=base_prompt,
        )
    return {
        "raw_reply": raw,
        "base_prompt": base_prompt,
        "events": [f"generated:{prompt_source}"],
    }


def _node_parse(state: AgentState) -> dict:
    from intelligence import (
        apply_meta_to_lead_fields,
        bant_score,
        is_bant_qualified,
        split_reply_and_meta,
        stage_from_meta_or_tags,
    )
    from utils import strip_control_blocks
    from guardrails import enforce_guardrails
    from intent import detect_buying_intent
    from lead_score import apply_score_to_lead, compute_lead_score
    from playbook import extract_playbook_from_workspace
    from workspace_context import resolve_workspace

    raw = state.get("raw_reply") or ""
    visible, meta = split_reply_and_meta(raw)
    reply = strip_control_blocks(visible)
    lead = state.get("lead") or {}
    stage = state.get("stage") or "sdr"
    user_message = state.get("user_message") or ""
    history = state.get("history") or []

    # --- Guardrails (preço/prazo) — alinhado ao fluxo legado ---
    playbook = None
    try:
        ws = resolve_workspace(workspace_id=state["workspace_id"]) or resolve_workspace(
            slug=state.get("workspace_slug") or "default"
        )
        if ws is not None:
            playbook = extract_playbook_from_workspace(ws.raw)
    except Exception:
        playbook = None

    guard_events: list[str] = []
    try:
        guarded = enforce_guardrails(reply, playbook=playbook, strict=True)
        if guarded.get("modified"):
            reply = guarded["reply"]
            guard_events.append("guardrail_enforced")
            if guarded.get("has_price_risk"):
                guard_events.append("guardrail_price")
            if guarded.get("has_deadline_risk"):
                guard_events.append("guardrail_deadline")
    except Exception:
        guard_events.append("guardrail_error")

    field_updates = apply_meta_to_lead_fields(lead, meta, user_message)
    new_stage = stage_from_meta_or_tags(raw, meta, stage, can_transition)
    bant = field_updates.get("bant") or lead.get("bant")

    # Auto-qualify por BANT clássico
    if stage == "sdr" and is_bant_qualified(bant) and new_stage == stage:
        if can_transition(stage, "qualified"):
            new_stage = "qualified"

    # Intent refinado (META + lexical + histórico)
    intent_info = detect_buying_intent(
        user_message,
        history=history,
        meta=meta,
    )

    updated_lead = dict(lead)
    for k, v in field_updates.items():
        if k == "metadata":
            meta_lead = dict(updated_lead.get("metadata") or {})
            meta_lead.update(v or {})
            updated_lead["metadata"] = meta_lead
        else:
            updated_lead[k] = v

    updated_lead = _apply_intent_to_lead(updated_lead, intent_info)

    # Score pós-META
    score_info = compute_lead_score(updated_lead, message_count=len(history))
    updated_lead = apply_score_to_lead(updated_lead, score_info)

    # Auto-qualify por score/intent (P0)
    if stage == "sdr" and new_stage == stage:
        hot = bool(score_info.get("hot"))
        ready = intent_info.get("intent") == "ready_to_buy"
        high_score = score_info.get("score", 0) >= 70
        if (hot or ready or high_score) and is_bant_qualified(bant, min_score=50):
            if can_transition(stage, "qualified"):
                new_stage = "qualified"
        elif ready and score_info.get("score", 0) >= 55 and can_transition(stage, "qualified"):
            new_stage = "qualified"

    if meta.get("handoff"):
        if "vou te conectar" not in reply.lower() and "humano" not in reply.lower():
            reply = (
                (reply + "\n\n" if reply else "")
                + "Vou acionar alguém do time para te atender em seguida, combinado?"
            ).strip()

    # Intent ready → empurrar closer se já qualified
    if intent_info.get("intent") == "ready_to_buy" and new_stage == "qualified":
        if can_transition("qualified", "closer"):
            # não pula stage automaticamente; deixa closer no próximo turno
            pass

    trace = state.get("_trace")
    if trace is not None:
        try:
            with trace.span(
                "parse",
                stage_from=stage,
                stage_to=new_stage,
                handoff=bool(meta.get("handoff")),
                bant_score=bant_score(bant),
                intent=intent_info.get("intent"),
                lead_score=score_info.get("score"),
                guardrail=bool(guard_events),
            ):
                pass
            trace.event(
                "meta_extracted",
                stage=new_stage,
                intent=intent_info.get("intent") or meta.get("intent"),
                objection=meta.get("objection"),
                handoff=bool(meta.get("handoff")),
                bant=bant or {},
                lead_score=score_info.get("score"),
                lead_tier=score_info.get("tier"),
            )
        except Exception:
            pass

    return {
        "visible_reply": reply,
        "meta": meta or {},
        "new_stage": new_stage,
        "lead": updated_lead,
        "intent_info": intent_info,
        "score_info": score_info,
        "events": [f"parsed:{stage}->{new_stage}"] + guard_events,
    }


def _node_actions(state: AgentState) -> dict:
    """Calendar / proposta / e-mail / Slack a partir do META + closer_tools."""
    from integrations.actions import run_agent_actions
    from playbook import extract_playbook_from_workspace
    from workspace_context import resolve_workspace

    meta = state.get("meta") or {}
    lead = state.get("lead") or {}
    agent = state.get("agent") or "sdr"
    stage = state.get("new_stage") or state.get("stage") or "sdr"
    reply = state.get("visible_reply") or ""
    intent_info = state.get("intent_info") or {}
    events: list[str] = []

    # Integrações genéricas (calendar via META meeting, notify handoff parcial)
    out = run_agent_actions(
        workspace_id=state["workspace_id"],
        agent=agent,
        stage=stage,
        meta=meta,
        lead=lead,
        visible_reply=reply,
    )
    suffix_parts: list[str] = []
    if out.get("reply_suffix"):
        suffix_parts.append(out["reply_suffix"])

    lead_meta = dict(lead.get("metadata") or {})
    lead_meta.update(out.get("lead_metadata") or {})

    # --- closer_tools: calendar + proposta (P0) ---
    try:
        from closer_tools import execute_closer_actions

        ws = resolve_workspace(workspace_id=state["workspace_id"]) or resolve_workspace(
            slug=state.get("workspace_slug") or "default"
        )
        playbook = extract_playbook_from_workspace(ws.raw) if ws else {}
        slug = (ws.slug if ws else None) or state.get("workspace_slug") or "default"

        # Se ready_to_buy e ainda sem schedule no META, marcar wants_meeting
        if intent_info.get("intent") == "ready_to_buy" and stage in ("qualified", "closer", "sdr"):
            if not meta.get("schedule") and not meta.get("calendar_request") and not meta.get("meeting"):
                lead_meta["wants_meeting"] = True
                events.append("intent_wants_meeting")

        closer_out = execute_closer_actions(
            state["workspace_id"],
            slug,
            lead,
            meta,
            playbook=playbook,
        )
        if closer_out.get("calendar"):
            events.append("closer_calendar")
            cal = closer_out["calendar"]
            lead_meta["last_meeting"] = {
                "event_link": cal.get("event_link"),
                "start": cal.get("start"),
                "end": cal.get("end"),
                "provider": cal.get("provider"),
            }
        if closer_out.get("proposal"):
            events.append("closer_proposal")
            prop = closer_out["proposal"]
            lead_meta["last_proposal"] = {
                "url": prop.get("url"),
                "plan": prop.get("plan"),
                "amount": prop.get("amount"),
            }
        for note in closer_out.get("notes_for_reply") or []:
            if note and note not in suffix_parts:
                suffix_parts.append(note)
    except Exception:
        events.append("closer_tools_error")

    new_reply = reply
    if suffix_parts:
        suffix = "\n\n".join(suffix_parts)
        new_reply = (reply.rstrip() + "\n\n" + suffix).strip()

    lead = {**lead, "metadata": lead_meta}

    events.extend([f"action:{a.get('type')}" for a in (out.get("actions") or [])])
    trace = state.get("_trace")
    if trace is not None:
        try:
            with trace.span("actions", count=len(out.get("actions") or []) + len(events)):
                for a in out.get("actions") or []:
                    r = a.get("result") or {}
                    trace.event(
                        "integration_action",
                        type=a.get("type"),
                        success=bool(r.get("success")),
                        error=r.get("error"),
                    )
        except Exception:
            pass

    return {
        "visible_reply": new_reply,
        "lead": lead,
        "action_results": out.get("actions") or [],
        "reply_suffix": "\n\n".join(suffix_parts) if suffix_parts else None,
        "events": events,
    }


def _node_route(state: AgentState) -> dict:
    current = state.get("stage") or "sdr"
    target = state.get("new_stage") or current
    blocked = False
    if target != current and not can_transition(current, target):
        blocked = True
        target = current
    trace = state.get("_trace")
    if trace is not None:
        try:
            with trace.span("route", from_stage=current, to_stage=target, blocked=blocked):
                pass
            if blocked:
                trace.event("transition_blocked", from_stage=current, attempted=state.get("new_stage"))
            elif target != current:
                trace.event("transition", from_stage=current, to_stage=target)
        except Exception:
            pass
    if blocked:
        return {"new_stage": current, "events": [f"blocked:{current}->{state.get('new_stage')}"]}
    return {"events": [f"routed:{target}"]}


def _node_persist(state: AgentState) -> dict:
    from db import (
        add_message,
        get_lead_by_phone,
        log_event,
        mark_message_processed,
        merge_metadata,
        set_stage,
        upsert_lead,
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
    intent_info = state.get("intent_info") or {}
    score_info = state.get("score_info") or {}
    events_out: list[str] = []
    lead_id = lead.get("id")
    handoff_done = False

    if lead_id:
        add_message(lead_id, "user", user_message)
        add_message(lead_id, "assistant", reply, agent=agent)
    message_id = state.get("message_id")
    if message_id:
        mark_message_processed(workspace_id, message_id, lead_id=lead_id)

    # Persistir score/intent no metadata do lead
    score_meta = {
        "buying_intent": intent_info.get("intent") or (lead.get("metadata") or {}).get("buying_intent"),
        "intent_confidence": intent_info.get("confidence"),
        "lead_score": score_info.get("score"),
        "lead_score_parts": score_info.get("parts"),
        "lead_tier": score_info.get("tier"),
        "is_hot": score_info.get("hot"),
    }
    score_meta = {k: v for k, v in score_meta.items() if v is not None}
    if score_meta:
        merge_metadata(workspace_id, phone, score_meta)

    # --- Handoff completo (pause + notify) — alinhado ao legado ---
    if meta.get("handoff"):
        log_event(
            "handoff_requested",
            {"phone": phone, "reason": meta.get("intent") or meta.get("notes")},
            lead_id=lead_id,
            workspace_id=workspace_id,
        )
        events_out.append("handoff")
        try:
            from handoff import execute_handoff

            ws_row = resolve_workspace(workspace_id=workspace_id) or resolve_workspace(
                slug=state.get("workspace_slug") or "default"
            )
            workspace_dict = (
                ws_row.raw
                if ws_row and isinstance(getattr(ws_row, "raw", None), dict)
                else {
                    "id": workspace_id,
                    "name": getattr(ws_row, "name", None) or "ForceIA",
                    "slug": state.get("workspace_slug") or "default",
                    "metadata": getattr(ws_row, "raw", {}) if ws_row else {},
                }
            )
            if not isinstance(workspace_dict.get("metadata"), dict):
                workspace_dict = {
                    **workspace_dict,
                    "metadata": (workspace_dict.get("metadata") or {})
                    if isinstance(workspace_dict.get("metadata"), dict)
                    else {},
                }
            # Garantir id/slug
            workspace_dict.setdefault("id", workspace_id)
            workspace_dict.setdefault("slug", state.get("workspace_slug") or "default")

            execute_handoff(
                workspace=workspace_dict,
                lead=lead,
                reason=str(meta.get("intent") or meta.get("notes") or "agente solicitou handoff"),
                notify=True,
                by="agent",
            )
            handoff_done = True
            events_out.append("handoff_executed")
        except Exception as exc:
            log_event(
                "handoff_error",
                {"error": str(exc)[:300]},
                lead_id=lead_id,
                workspace_id=workspace_id,
            )
            events_out.append("handoff_error")

    field_keys = ("name", "company", "email", "bant")
    upsert_kwargs = {k: lead[k] for k in field_keys if k in lead and lead[k] is not None}
    if lead.get("metadata"):
        # metadata já mesclado parcialmente; merge residual sem sobrescrever handoff
        residual = {
            k: v
            for k, v in (lead.get("metadata") or {}).items()
            if k
            not in (
                "buying_intent",
                "intent_confidence",
                "lead_score",
                "lead_score_parts",
                "lead_tier",
                "is_hot",
            )
        }
        if residual:
            merge_metadata(workspace_id, phone, residual)

    ws = resolve_workspace(workspace_id=workspace_id) or resolve_workspace(
        slug=state.get("workspace_slug") or "default"
    )

    if new_stage != stage and not handoff_done:
        lead = set_stage(workspace_id, phone, new_stage)
        other = {k: v for k, v in upsert_kwargs.items() if k != "stage"}
        if other:
            lead = upsert_lead(workspace_id, phone, **other)
        log_event(
            "stage_changed",
            {
                "from": stage,
                "to": new_stage,
                "bant_score": bant_score(lead.get("bant")),
                "lead_score": score_info.get("score"),
                "intent": intent_info.get("intent"),
                "source": "langgraph",
            },
            lead_id=lead.get("id"),
            workspace_id=workspace_id,
        )
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

    if state.get("send_whatsapp") and reply and ws and not handoff_done:
        # Ainda envia a mensagem de handoff ao lead; se handoff_done, reply já inclui aviso
        try:
            send_whatsapp(ws, phone, reply)
            events_out.append("whatsapp_sent")
        except Exception as exp:
            log_event(
                "whatsapp_send_error",
                {"error": str(exp)},
                lead_id=lead.get("id") if lead else lead_id,
                workspace_id=workspace_id,
            )
            events_out.append("whatsapp_error")
    elif state.get("send_whatsapp") and reply and ws and handoff_done:
        # Envia última msg ao lead mesmo após pause (aviso de handoff)
        try:
            send_whatsapp(ws, phone, reply)
            events_out.append("whatsapp_sent")
        except Exception as exp:
            log_event(
                "whatsapp_send_error",
                {"error": str(exp)},
                lead_id=lead.get("id") if lead else lead_id,
                workspace_id=workspace_id,
            )
            events_out.append("whatsapp_error")

    trace = state.get("_trace")
    if trace is not None:
        try:
            with trace.span(
                "persist",
                stage=new_stage,
                whatsapp=("whatsapp_sent" in events_out),
                handoff=handoff_done,
                events=events_out,
            ):
                pass
        except Exception:
            pass

    return {
        "lead": lead,
        "visible_reply": reply,
        "events": events_out,
        "handoff_done": handoff_done,
    }


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
    from observability import start_turn_trace, flush as lf_flush
    from db import (
        add_message,
        get_lead_by_phone,
        is_agent_paused,
        log_event,
        mark_message_processed,
        upsert_lead,
    )

    trace = start_turn_trace(
        workspace_id=workspace_id,
        workspace_slug=workspace_slug,
        phone=phone,
        user_message=text,
        session_id=thread_id_for(workspace_id, phone),
        tags=["langgraph", "p0"],
    )

    lead0 = get_lead_by_phone(workspace_id, phone)
    if lead0 and is_agent_paused(lead0):
        add_message(lead0["id"], "user", text)
        if message_id:
            mark_message_processed(workspace_id, message_id, lead_id=lead0["id"])
        log_event(
            "agent_skipped_paused",
            {"phone": phone, "text": (text or "")[:200]},
            lead_id=lead0["id"],
            workspace_id=workspace_id,
        )
        upsert_lead(workspace_id, phone)
        try:
            trace.end(output={"reply": "", "paused": True})
        except Exception:
            pass
        lf_flush()
        return ""

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
        "_trace": trace,
        "handoff_done": False,
    }
    try:
        final = app.invoke(initial, config)
        reply = final.get("visible_reply") or ""
        trace.end(
            output={"reply": reply[:2000], "stage": final.get("new_stage") or final.get("stage")},
            metadata={
                "events": final.get("events") or [],
                "agent": final.get("agent"),
                "stage": final.get("new_stage") or final.get("stage"),
                "ab_variant": final.get("ab_variant"),
                "intent": (final.get("intent_info") or {}).get("intent"),
                "lead_score": (final.get("score_info") or {}).get("score"),
                "handoff_done": final.get("handoff_done"),
            },
        )
        return reply
    except Exception as exc:
        try:
            trace.event("turn_error", error=str(exc)[:500])
            trace.end(metadata={"error": str(exc)[:500]})
        except Exception:
            pass
        raise
    finally:
        lf_flush()


def graph_enabled() -> bool:
    flag = os.getenv("FORCEIA_USE_GRAPH", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return _langgraph_available()
