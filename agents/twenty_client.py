"""
ForceIA - Cliente Twenty CRM (GraphQL)

Sincroniza leads do Supabase com People + Opportunities no Twenty.
Documentacao API: https://docs.twenty.com
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

TWENTY_API_URL = (os.getenv("TWENTY_API_URL") or "").rstrip("/")
TWENTY_API_KEY = os.getenv("TWENTY_API_KEY") or ""

# Mapeamento ForceIA stage -> nome do stage no pipeline Twenty (ajuste no .env se necessario)
STAGE_MAP = {
    "sdr": os.getenv("TWENTY_STAGE_SDR", "NEW"),
    "qualified": os.getenv("TWENTY_STAGE_QUALIFIED", "SCREENING"),
    "closer": os.getenv("TWENTY_STAGE_CLOSER", "MEETING"),
    "followup": os.getenv("TWENTY_STAGE_FOLLOWUP", "SCREENING"),
    "won": os.getenv("TWENTY_STAGE_WON", "CUSTOMER"),
    "lost": os.getenv("TWENTY_STAGE_LOST", "REJECTED"),
}


def enabled() -> bool:
    return bool(TWENTY_API_URL and TWENTY_API_KEY)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {TWENTY_API_KEY}",
        "Content-Type": "application/json",
    }


def graphql(query: str, variables: dict[str, Any] | None = None) -> dict:
    if not enabled():
        raise RuntimeError("Twenty nao configurado (TWENTY_API_URL / TWENTY_API_KEY)")
    url = f"{TWENTY_API_URL}/graphql"
    payload = {"query": query, "variables": variables or {}}
    with httpx.Client(timeout=30) as client:
        r = client.post(url, json=payload, headers=_headers())
        r.raise_for_status()
        data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"Twenty GraphQL errors: {data['errors']}")
    return data.get("data") or {}


FIND_PERSON = """
query FindPerson($filter: PersonFilterInput) {
  people(filter: $filter, first: 1) {
    edges {
      node {
        id
        name { firstName lastName }
        emails { primaryEmail }
        phones { primaryPhoneNumber }
        jobTitle
        city
      }
    }
  }
}
"""

CREATE_PERSON = """
mutation CreatePerson($data: PersonCreateInput!) {
  createPerson(data: $data) {
    id
    name { firstName lastName }
    phones { primaryPhoneNumber }
  }
}
"""

UPDATE_PERSON = """
mutation UpdatePerson($id: ID!, $data: PersonUpdateInput!) {
  updatePerson(id: $id, data: $data) {
    id
    name { firstName lastName }
  }
}
"""

CREATE_OPPORTUNITY = """
mutation CreateOpportunity($data: OpportunityCreateInput!) {
  createOpportunity(data: $data) {
    id
    name
    stage
  }
}
"""

UPDATE_OPPORTUNITY = """
mutation UpdateOpportunity($id: ID!, $data: OpportunityUpdateInput!) {
  updateOpportunity(id: $id, data: $data) {
    id
    name
    stage
  }
}
"""

FIND_OPPORTUNITY = """
query FindOpportunity($filter: OpportunityFilterInput) {
  opportunities(filter: $filter, first: 5) {
    edges {
      node {
        id
        name
        stage
        pointOfContactId
      }
    }
  }
}
"""


def normalize_phone(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


def find_person_by_phone(phone: str) -> dict | None:
    phone_norm = normalize_phone(phone)
    # Twenty filtra por phones de formas diferentes conforme versao;
    # tentamos filter generico e fallback em listagem se necessario.
    try:
        data = graphql(
            FIND_PERSON,
            {
                "filter": {
                    "phones": {"primaryPhoneNumber": {"eq": phone_norm}}
                }
            },
        )
        edges = (data.get("people") or {}).get("edges") or []
        if edges:
            return edges[0]["node"]
    except Exception:
        pass

    # Fallback: busca por contains (algumas instalacoes)
    try:
        data = graphql(
            FIND_PERSON,
            {
                "filter": {
                    "phones": {"primaryPhoneNumber": {"ilike": f"%{phone_norm[-8:]}%"}}
                }
            },
        )
        edges = (data.get("people") or {}).get("edges") or []
        if edges:
            return edges[0]["node"]
    except Exception:
        pass
    return None


def create_person(
    phone: str,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
) -> dict:
    first = (name or "Lead").strip().split(" ")[0]
    last_parts = (name or "").strip().split(" ")[1:]
    last = " ".join(last_parts) if last_parts else "WhatsApp"

    data: dict[str, Any] = {
        "name": {"firstName": first, "lastName": last},
        "phones": {"primaryPhoneNumber": normalize_phone(phone), "primaryPhoneCountryCode": "BR"},
    }
    if email:
        data["emails"] = {"primaryEmail": email}
    if company:
        data["jobTitle"] = company  # fallback se nao houver company link

    result = graphql(CREATE_PERSON, {"data": data})
    return result.get("createPerson") or {}


def update_person(person_id: str, **fields: Any) -> dict:
    data: dict[str, Any] = {}
    if fields.get("name"):
        parts = str(fields["name"]).strip().split(" ")
        data["name"] = {
            "firstName": parts[0],
            "lastName": " ".join(parts[1:]) if len(parts) > 1 else "WhatsApp",
        }
    if fields.get("email"):
        data["emails"] = {"primaryEmail": fields["email"]}
    if not data:
        return {"id": person_id}
    result = graphql(UPDATE_PERSON, {"id": person_id, "data": data})
    return result.get("updatePerson") or {"id": person_id}


def upsert_person(phone: str, name: str | None = None, email: str | None = None, company: str | None = None) -> dict:
    existing = find_person_by_phone(phone)
    if existing:
        if name or email:
            return update_person(existing["id"], name=name, email=email)
        return existing
    return create_person(phone, name=name, email=email, company=company)


def find_open_opportunity(person_id: str) -> dict | None:
    try:
        data = graphql(
            FIND_OPPORTUNITY,
            {"filter": {"pointOfContactId": {"eq": person_id}}},
        )
        edges = (data.get("opportunities") or {}).get("edges") or []
        for edge in edges:
            node = edge["node"]
            stage = (node.get("stage") or "").upper()
            if stage not in ("CUSTOMER", "REJECTED", "WON", "LOST"):
                return node
        if edges:
            return edges[0]["node"]
    except Exception:
        return None
    return None


def create_opportunity(person_id: str, name: str, stage: str) -> dict:
    twenty_stage = STAGE_MAP.get(stage, STAGE_MAP["sdr"])
    data = {
        "name": name,
        "stage": twenty_stage,
        "pointOfContactId": person_id,
    }
    result = graphql(CREATE_OPPORTUNITY, {"data": data})
    return result.get("createOpportunity") or {}


def update_opportunity_stage(opportunity_id: str, stage: str) -> dict:
    twenty_stage = STAGE_MAP.get(stage, stage)
    result = graphql(
        UPDATE_OPPORTUNITY,
        {"id": opportunity_id, "data": {"stage": twenty_stage}},
    )
    return result.get("updateOpportunity") or {"id": opportunity_id}


def sync_lead_to_twenty(lead: dict) -> dict:
    """
    Sincroniza um lead ForceIA (Supabase) com Person + Opportunity no Twenty.
    Retorna ids criados/atualizados.
    """
    if not enabled():
        return {"skipped": True, "reason": "twenty_disabled"}

    phone = lead.get("phone") or ""
    name = lead.get("name")
    email = lead.get("email")
    company = lead.get("company")
    stage = lead.get("stage") or "sdr"

    person = upsert_person(phone, name=name, email=email, company=company)
    person_id = person.get("id")
    if not person_id:
        return {"error": "person_not_created", "person": person}

    opp_name = name or company or f"WhatsApp {normalize_phone(phone)[-8:]}"
    existing_opp = find_open_opportunity(person_id)

    if existing_opp:
        opp = update_opportunity_stage(existing_opp["id"], stage)
    else:
        # Cria opportunity a partir de qualified (ou sempre, se TWENTY_CREATE_OPP_ALWAYS=true)
        always = os.getenv("TWENTY_CREATE_OPP_ALWAYS", "true").lower() in ("1", "true", "yes")
        if always or stage in ("qualified", "closer", "followup", "won", "lost"):
            opp = create_opportunity(person_id, opp_name, stage)
        else:
            opp = {}

    return {
        "person_id": person_id,
        "opportunity_id": opp.get("id"),
        "stage": stage,
        "twenty_stage": STAGE_MAP.get(stage),
    }
