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

## 3. WhatsApp Integration

| Contract | Classification | Notes |
|----------|----------------|-------|
| `whatsapp_config` | IMMUTABLE | Per-account Meta credentials and phone number ID. |
| Webhook verify + inbound/outbound handlers | IMMUTABLE | Signature validation, message status callbacks. |
| Public API surface for messaging | IMMUTABLE | |

---

## 4. Automations, Flows & AI

| Contract | Classification | Notes |
|----------|----------------|-------|
| Automations engine + tables | IMMUTABLE | Trigger/action model. |
| Flows engine + editor | IMMUTABLE | Graph storage and runtime. |
| AI agent configs / tools | EXTENDABLE | May add agent personas/skills without changing existing runtime contracts. |

---

## Phase 1 scope reminder

Allowed: branding, product language, navigation labels, metadata, i18n, design tokens, visible nomenclatures.
Forbidden: schema/migrations, RLS, auth, webhook, public API, automation/flows engines, AI core changes.
