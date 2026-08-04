# Playbook por workspace — ForceIA

Cada cliente (workspace) tem um **playbook comercial** que vira contexto obrigatório
no system prompt do SDR, Closer e Follow-up.

Objetivo: a empresa sentir que tem o **melhor SDR e o melhor Closer para cada lead** —
especialistas no produto, ICP e tom dela, não um bot genérico.

## Schema

```json
{
  "version": 1,
  "company_name": "Clínica Sol",
  "product_summary": "…",
  "value_proposition": "…",
  "icp": {
    "industries": ["saúde", "clínicas"],
    "company_sizes": "10-200 funcionários",
    "roles": ["dono", "gerente comercial"],
    "geographies": "Brasil",
    "disqualifiers": ["só estudante", "sem CNPJ"]
  },
  "persona": {
    "buyer_titles": ["CEO", "Head de Vendas"],
    "pains": ["leads esfriando", "SDR caro"],
    "goals": ["mais reuniões qualificadas"]
  },
  "pricing": {
    "model": "assinatura mensal",
    "range": "R$ 997 a R$ 4.900",
    "notes": "piloto 14 dias no plano completo"
  },
  "cases": [{ "title": "Clínica XP", "result": "+40% reuniões", "segment": "saúde" }],
  "objections": [{ "objection": "está caro", "response": "compare com 1 SDR pleno…" }],
  "tone": {
    "style": "consultivo",
    "formality": "semi-formal",
    "do": ["usar exemplos do setor"],
    "dont": ["prometer ROI garantido"]
  },
  "faq": [{ "q": "Integra com RD?", "a": "Sim, via webhook." }],
  "script_notes": "Sempre oferecer 2 horários",
  "extra": ""
}
```

Coluna: `workspaces.playbook` (jsonb). Fallback: `metadata.playbook`.

Migration: `supabase/playbook.sql`

## Como é injetado

`build_system_prompt` em `intelligence.py` acrescenta o bloco
`format_playbook_for_prompt(...)` **antes** do contexto do lead e do protocolo META.

Ordem no system prompt:

1. Prompt base do agente (arquivo / override learning)
2. **Playbook do cliente**
3. Contexto deste lead (BANT, nome, empresa…)
4. Protocolo `---META---`

## API

```bash
# Ler
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8100/api/workspaces/default/playbook

# Salvar (merge normalizado)
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @playbook.json \
  http://localhost:8100/api/workspaces/default/playbook
```

Resposta inclui `completeness` (score 0–100 + checklist).

## Console

Aba **Playbook** no painel admin: formulário completo + score de prontidão.

## Completeness

| Score | Significado |
|------|------------|
| &lt; 50 | Agente ainda genérico — preencha ICP + produto + pricing |
| ≥ 50 | Pronto para produção (`ready: true`) |
| ≥ 80 | Especialista forte (cases + objeções + persona) |

## Boas práticas

- Preencha **antes** de ligar o WhatsApp do cliente
- Pricing e disqualifiers são guardrails — o modelo é instruído a não inventar
- Atualize cases e objeções com o learning (won/lost reais)
- Um playbook por workspace = multi-tenant real de vendas
