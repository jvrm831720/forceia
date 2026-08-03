# Jobs de Follow-up - ForceIA

Reativa automaticamente leads que pararam de responder.

## Como funciona

1. Consulta no Supabase leads com `last_message_at` mais antigo que N dias
2. Filtra estagios ativos: `sdr`, `qualified`, `closer`, `followup`
3. Ignora se ja houve evento `followup_sent` nas ultimas 48h (configuravel)
4. Gera mensagem com o agente **followup**
5. Atualiza stage para `followup`, grava mensagem e envia no WhatsApp
6. Registra evento `followup_sent`

## Configuracao (.env)

```env
FOLLOWUP_STALE_DAYS=5          # dias sem mensagem
FOLLOWUP_MIN_HOURS=48          # intervalo minimo entre follow-ups do mesmo lead
```

## Executar uma vez

```bash
cd agents
python followup_job.py
python followup_job.py --days 3
python followup_job.py --dry-run   # so simula
```

## Agendar

### Opcao A - Cron (recomendado em VPS)

```cron
# A cada 6 horas
0 */6 * * * cd /opt/forceia/agents && /opt/forceia/.venv/bin/python followup_job.py >> /var/log/forceia-followup.log 2>&1
```

### Opcao B - Processo Python

```bash
python scheduler.py --hours 6 --days 5
```

### Opcao C - Supabase Edge Function + pg_cron (avancado)

Voce pode chamar um endpoint HTTP seu que dispara o job, ou usar um worker na mesma maquina do webhook.

## Boas praticas

- Comece com `--dry-run` e confira os candidatos
- Use 3–7 dias de inatividade conforme o ciclo de venda
- `FOLLOWUP_MIN_HOURS=48` evita spam
- Leads em `won` / `lost` nao entram no job

## Eventos no Supabase

| type | Significado |
|------|-------------|
| `followup_sent` | Mensagem de follow-up enviada |
| `followup_send_error` | Falha no WhatsApp |
| `stage_changed` | Stage alterado (inclui source `followup_job`) |
