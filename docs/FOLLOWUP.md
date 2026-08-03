# Jobs de Follow-up - ForceIA (multi-tenant)

Reativa leads parados, por workspace ou em lote.

## Como funciona

1. Busca leads do workspace com `last_message_at` > N dias
2. Estagios: `sdr`, `qualified`, `closer`, `followup`
3. Ignora se ja houve `followup_sent` nas ultimas N horas
4. Gera mensagem com agente **followup** e envia no WhatsApp

## Executar

```bash
cd agents

python followup_job.py --dry-run
python followup_job.py --workspace default
python followup_job.py --all

# Scheduler em processo
python scheduler.py --hours 6 --all
python scheduler.py --workspace default --once
```

## Config

Por workspace (colunas `followup_stale_days`, `followup_min_hours`) ou fallback no `.env`:

```env
FOLLOWUP_STALE_DAYS=5
FOLLOWUP_MIN_HOURS=48
```

## Cron

```cron
0 */6 * * * cd /opt/forceia/agents && .venv/bin/python followup_job.py --all >> /var/log/forceia-followup.log 2>&1
```
