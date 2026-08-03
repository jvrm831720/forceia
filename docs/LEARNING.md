# Auto-melhoria assistida — ForceIA

Os agentes **não** alteram produção sozinhos. O ciclo é:

```
won/lost → análise LLM → sugestões (pending)
       → humano aprova → override ativo
```

## 1. Schema

No SQL Editor do Supabase:

```
supabase/learning.sql
```

Cria: `learning_runs`, `prompt_suggestions`, `agent_prompt_overrides`.

## 2. Rodar análise

Precisa de leads em `won` e/ou `lost` com histórico de mensagens.

```bash
cd agents
python improve_agents.py --workspace default
python improve_agents.py --workspace default --per-outcome 10
python improve_agents.py --all
```

Variáveis opcionais:

```env
LEARNING_MODEL=gpt-4o   # modelo mais forte só para análise (custo maior)
```

## 3. Revisar sugestões

```bash
python improve_agents.py --list-pending
```

Ou API admin:

```bash
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/learning/suggestions
```

## 4. Aprovar / rejeitar / aplicar

```bash
python improve_agents.py --approve <ID>
python improve_agents.py --reject <ID> --note "tom agressivo"
python improve_agents.py --apply <ID>
# global + gravar arquivo:
python improve_agents.py --apply <ID> --write-file
```

API:

```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/learning/suggestions/<ID>/apply
```

Disparar learning pelo admin:

```bash
curl -X POST -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/learning/run/default?per_outcome=8
```

## 5. Como o runtime usa o override

`load_prompt(agent, workspace_id)`:

1. Override do workspace (tabela `agent_prompt_overrides`)
2. Override global
3. Arquivo `config/prompts/{agent}.md`

Ou seja: depois de `--apply`, as **próximas** conversas já usam o prompt novo.

## 6. Cron sugerido

```cron
# Todo domingo 3h — só gera sugestões (não aplica)
0 3 * * 0 cd /opt/forceia/agents && .venv/bin/python improve_agents.py --all >> /var/log/forceia-learning.log 2>&1
```

## 7. Boas práticas

- Não aplique a primeira sugestão sem ler o `diff_summary` e o prompt
- Prefira `LEARNING_MODEL` melhor que o modelo de conversa
- Mínimo ~5 won + 5 lost com histórico rico para análise útil
- Overrides por workspace permitem playbooks diferentes por cliente
