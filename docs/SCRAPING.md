# Scraping de vagas — ForceIA

Pipeline para **Hiring Signal Prospector**: coleta vagas públicas → analisa força do sinal → opener.

## O que NÃO fazemos

- **Não embutimos o código-fonte do Scrapy** no repo (é dependência pip).
- **Não scrapamos LinkedIn** (login wall / ToS).

## O que fazemos

| Fonte | Como |
|-------|------|
| Greenhouse board | API pública `boards-api.greenhouse.io` |
| Lever postings | API pública `api.lever.co/v0/postings/{company}` |
| Página HTML genérica | fallback com extração de título + texto |

Runtime: **httpx** (já no `requirements.txt`). Scrapy fica opcional para jobs pesados futuros.

## API

```bash
POST /api/workspaces/{slug}/skills/scrape-hiring
{
  "url": "https://boards.greenhouse.io/example",
  "role_filter": "SDR",
  "limit": 20
}
```

Resposta: lista de signals Strong/Medium/Soft com `suggested_opener`, `pain_point`, etc.

Para anexar a um lead e o SDR usar no prompt:

```bash
POST /api/workspaces/{slug}/skills/hiring-signal
{ "role": "...", "jd_snippet": "...", "lead_id": "...", "attach_to_lead": true }
```

## Módulos

```
agents/scrapers/
  job_boards.py       # fetch + parse
  hiring_pipeline.py  # scrape → analyze_hiring_signal
agents/scraper_routes.py
```

## Ética

- Só boards **públicos**
- User-Agent identificável
- Rate limit implícito (request sob demanda via API admin)
- Bloqueio de domínios sensíveis na rota
