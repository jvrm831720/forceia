# Observabilidade — Langfuse

Cada mensagem do lead vira um **trace** `forceia.turn` com a árvore de decisão do agente.

```
forceia.turn
  ├─ prepare      (lead, stage, agent, histórico)
  ├─ generate     (span) + generation openai.{sdr|closer|followup}
  ├─ parse        (META, BANT, stage candidato)
  ├─ route        (transição válida ou bloqueada)
  └─ persist      (DB, WhatsApp, Twenty)
```

## Por que isso importa

- Ver **por que** o lead esfriou (objecção no META, stage stuck, reply fraca)
- Comparar won vs lost pelo mesmo `session_id` (`workspace:phone`)
- Auditar custo de tokens e modelo por workspace
- Debugar handoff humano e auto-qualify BANT

## Setup

1. Crie projeto em [cloud.langfuse.com](https://cloud.langfuse.com) **ou** suba self-host.
2. Copie as chaves:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=1
```

3. `pip install 'langfuse>=2.0.0'`

Sem chaves o runtime **não quebra** — traces viram no-op.

## Filtros úteis

| Filtro | Valor |
|--------|--------|
| Tag | `ws:{slug}` |
| Tag | `agent:sdr` / `closer` / `followup` |
| Session | `{workspace_id}:{phone}` |
| User | telefone do lead |

## Eventos

- `meta_extracted` — intent, objection, handoff, bant
- `transition` / `transition_blocked`
- `turn_error`

## Desligar

```env
LANGFUSE_ENABLED=0
```
