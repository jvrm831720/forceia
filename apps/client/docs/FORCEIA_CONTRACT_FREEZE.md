# ForceIA — Contract Freeze

**Phase:** 1 — Semantic & Brand Foundation  
**Date:** 2026-08-07  
**Rule:** PRESERVE > ADAPT > REFACTOR > REWRITE

This document freezes the technical contracts inherited from the WaCRM foundation.
Phase 1 may only change branding, product language, navigation labels, metadata,
i18n strings, design tokens, and visible nomenclatures. **No schema, RLS, auth,
webhook, public API, automation engine, flows engine, or AI core may be modified.**

---

## Classification Legend

| Tag | Meaning |
|-----|---------|
| **IMMUTABLE** | Do not rename, reshape, or remove. Breaking this breaks production data, Meta integration, or multi-tenancy. |
| **EXTENDABLE** | May add columns, optional fields, or new related tables without changing existing shape or semantics. |
| **MIGRATION REQUIRED** | Any change needs an explicit, versioned migration and a backward-compatible rollout plan. |

---

## 1. Tenancy & Identity

| Contract | Classification | Notes |
|----------|----------------|-------|
| `accounts` table | IMMUTABLE | Tenancy root. `owner_user_id`, unique one-account-per-owner. |
| `profiles` (`user_id`, `account_id`, `account_role`) | IMMUTABLE | Membership is single-account-per-user via `profiles.account_id`. |
| `account_role_enum` (`owner` / `admin` / `agent` / `viewer`) | IMMUTABLE | Role semantics and privilege matrix in `src/lib/auth/roles`. |
| `account_invitations` | IMMUTABLE | Token-hash based invites; role cannot be `owner`. |
| `is_account_member(account_id [, min_role])` RPC | IMMUTABLE | SECURITY DEFINER helper used by nearly all RLS policies. |
| Auth session cookies / Supabase SSR clients | IMMUTABLE | Browser singleton + server cookie client + middleware refresh. |
| Middleware route protection + cookie propagation | IMMUTABLE | Including invite redirect and refresh-token handling. |

---

## 2. CRM Core

| Contract | Classification | Notes |
|----------|----------------|-------|
| `contacts` (+ phone uniqueness per account) | IMMUTABLE | Phone normalization and dedupe logic. |
| `tags`, `contact_tags`, `custom_fields`, `contact_custom_values`, `contact_notes` | IMMUTABLE | |
| `conversations` (account_id, contact_id uniqueness) | IMMUTABLE | Migration 036 dedup contract. |
| `messages` (+ content_type, status, message_id) | IMMUTABLE | |
| `message_reactions`, `quick_replies` | EXTENDABLE | |
| `pipelines`, `pipeline_stages`, `deals` | IMMUTABLE | Kanban / opportunity model. |

Visible product language may map contacts→Leads, deals→Oportunidades, pipelines→Pipeline.
**Internal names, columns, and types stay unchanged.**

---

## 3. Messaging / WhatsApp

| Contract | Classification | Notes |
|----------|----------------|-------|
| `whatsapp_config` (phone_number_id unique per account, encrypted token) | IMMUTABLE | |
| Meta webhook payload shape & signature verification | IMMUTABLE | `META_APP_SECRET`, HMAC-SHA256, fail-closed. |
| `/api/whatsapp/webhook` route contract | IMMUTABLE | Ordered dispatch: Flows → Automations → AI auto-reply. |
| Outbound send helpers / template format | IMMUTABLE | |
| Media download / storage paths | EXTENDABLE | |
| `ENCRYPTION_KEY` AES-256-GCM for tokens | IMMUTABLE | |

---

## 4. Automations & Flows

| Contract | Classification | Notes |
|----------|----------------|-------|
| `automations`, `automation_steps`, `automation_logs`, `automation_pending_executions` | IMMUTABLE | Engine in `src/lib/automations/`. |
| Trigger types and action shapes already in production | IMMUTABLE | New triggers/actions are EXTENDABLE. |
| `flows`, `flow_nodes`, `flow_runs`, `flow_run_events` | IMMUTABLE | Engine in `src/lib/flows/`. |
| Priority: Flows win over Automations and AI on inbound | IMMUTABLE | |

---

## 5. AI Foundation

| Contract | Classification | Notes |
|----------|----------------|-------|
| `ai_configs` | EXTENDABLE | New agent-related columns allowed later. |
| `ai_knowledge_documents`, `ai_knowledge_chunks` | EXTENDABLE | |
| `ai_usage_log` | EXTENDABLE | |
| Auto-reply eligibility gates & handoff flags on conversations | IMMUTABLE until Agent Core phase designs replacement | |
| Provider abstraction / BYOK | IMMUTABLE | |

Phase 1 does **not** implement SDR / Closer / Follow-up agents.

---

## 6. Platform

| Contract | Classification | Notes |
|----------|----------------|-------|
| `api_keys` (hashed, scoped) | IMMUTABLE | |
| Public API `/api/v1/*` shapes | IMMUTABLE | Documented in `docs/public-api.md`. |
| `webhook_endpoints` + signed delivery | IMMUTABLE | |
| `notifications`, `member_presence` | EXTENDABLE | |
| Storage buckets (avatars, chat media) policies | IMMUTABLE | |

---

## 7. Explicit Non-Goals of Phase 1

- No new migrations.
- No table/column renames.
- No RLS policy edits.
- No changes to service-role usage boundaries.
- No changes to Meta webhook verification or payload handling.
- No changes to public API request/response contracts.
- No changes to automation/flow engine execution semantics.
- No agent orchestration code.

---

## 8. Approval

This freeze is the binding baseline for Phase 1. Any future phase that needs to evolve an IMMUTABLE contract must open an explicit design review and produce a versioned migration plan before code lands.
