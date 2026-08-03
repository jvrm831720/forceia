# Auto-melhoria assistida — ForceIA (STaR + SPIN)

Os agentes **não** alteram produção sozinhos. O ciclo é:

```
won/lost
  → pares preferência SPIN (real=won vs generated=lost)
  → racionalização STaR (counterfactual nos lost)
  → análise LLM → sugestões (pending)
  → humano aprova → override ativo
```

Inspirado em:
- **STaR** (Zelikman et al., NeurIPS 2022) — *Bootstrapping Reasoning With Reasoning*: quando o agente erra, gera a resposta/raciocínio que *teria* funcionado e filtra por qualidade antes de usar como sinal.
- **SPIN** (Chen et al., ICML 2024) — *Self-Play Fine-Tuning*: o modelo joga contra a própria geração anterior; discrimina “real” (dado bom) de “generated” (própria saída fraca) sem labels humanos extras.

Na ForceIA isso vira **melhoria de prompt** (não fine-tune de pesos): usamos OpenAI como coach + gate humano.

## 1. Schema

No SQL Editor do Supabase:

```
supabase/learning.sql
```

Cria: `learning_runs`, `prompt_suggestions`, `agent_prompt_overrides`.

## 2. Modos

| Modo | O que faz | Custo LLM |
|------|-----------|-----------|
| `hybrid` (padrão) | Pares SPIN + racionalização STaR + coach | médio/alto |
| `spin` | Só self-play pairs + discriminator | médio |
| `star` | Só racionaliza lost filtrados | médio |
| `classic` | Só amostras won/lost (legado v1.2) | baixo |

```bash
cd agents
python improve_agents.py --workspace default
python improve_agents.py --workspace default --mode spin --per-outcome 12
python improve_agents.py --workspace default --mode star
python improve_agents.py --all --mode hybrid
```

Exportar dataset de preferência (schema SPIN/HF) para auditoria:

```bash
python improve_agents.py --workspace default --mode spin \
  --export-prefs /tmp/forceia_prefs.json
```

Variáveis:

```env
LEARNING_MODEL=gpt-4o   # modelo mais forte só para análise/racionalização
```

## 3. O que cada etapa produz

### SPIN — preference pairs
```json
{
  "real": { "content": "<transcript won>", "meta": { "outcome": "won" } },
  "generated": { "content": "<transcript lost>", "meta": { "outcome": "lost" } }
}
```
O discriminator extrai `win_signals`, `loss_signals` e uma `lesson` acionável.

### STaR — rationalization
Para cada lost (filtrado por `quality >= 0.45`):
```json
{
  "breakpoint": "onde a conversa morreu",
  "ideal_reply": "mensagem WhatsApp que deveria ter sido enviada",
  "principle": "principio de vendas em 1 frase",
  "agent": "sdr|closer|followup",
  "quality": 0.8
}
```

### Coach
Junta pares + racionalizações + prompts atuais → `prompt_suggestions` (pending).

## 4. Revisar / aprovar / aplicar

```bash
python improve_agents.py --list-pending
python improve_agents.py --approve <ID>
python improve_agents.py --reject <ID> --note "tom agressivo"
python improve_agents.py --apply <ID>
python improve_agents.py --apply <ID> --write-file   # grava config/prompts
```

API admin:

```bash
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/learning/suggestions

curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/learning/suggestions/<ID>/apply

curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  "http://localhost:8100/api/learning/run/default?per_outcome=8"
```

## 5. Runtime

`load_prompt(agent, workspace_id)`:

1. Override do workspace (`agent_prompt_overrides`)
2. Override global
3. Arquivo `config/prompts/{agent}.md`

Depois de `--apply`, as **próximas** conversas já usam o prompt novo.

## 6. Cron sugerido

```cron
# Domingo 3h — hybrid, só gera sugestões
0 3 * * 0 cd /opt/forceia/agents && .venv/bin/python improve_agents.py --all --mode hybrid >> /var/log/forceia-learning.log 2>&1
```

## 7. Boas práticas

- Mínimo ~5 won + 5 lost com histórico rico
- Leia `diff_summary` e o prompt antes de aplicar
- Prefira `LEARNING_MODEL` mais forte que o modelo de conversa
- Overrides por workspace = playbooks diferentes por cliente
- Use `--export-prefs` se for evoluir para DPO/SPIN off-policy no futuro
- `classic` é o fallback barato quando há poucas amostras
