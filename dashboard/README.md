# ForceIA · Dashboard (Cliente)

Console premium para o **cliente** da ForceIA acompanhar a equipe de vendas com IA em tempo real.

> A ForceIA não é um CRM. O cliente não configura agentes, prompts ou automações — a operação é gerida pela equipe ForceIA. O Dashboard transmite: *“minha equipe de IA está trabalhando e eu acompanho tudo ao vivo.”*

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Lucide Icons
- Componentes no estilo shadcn/ui

## Design system

| Token        | Valor     |
|-------------|-----------|
| Background  | `#FBFAF8` |
| Cards       | `#FFFFFF` |
| Texto       | `#111111` |
| Bordas      | `#e5e2dd` |
| Azul        | `#05B5DB` |
| Verde       | `#0DA387` |
| Roxo IA     | `#9B95FE` |
| Laranja     | `#DD6539` |
| Amarelo     | `#F7CA63` |

## Rodar local

```bash
cd dashboard
npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

## Deploy na Vercel (obrigatório)

Este repositório é um **monorepo**. A aplicação Next.js do Painel Cliente fica em `dashboard/`.

Na Vercel, crie o projeto apontando para este repositório e configure:

| Campo | Valor |
|--------|--------|
| **Framework Preset** | Next.js |
| **Root Directory** | `dashboard` |
| **Install Command** | `npm install` |
| **Build Command** | `npm run build` |
| **Output Directory** | *deixar vazio* (Next.js gerencia `.next`) |
| **Node.js** | 20.x (recomendado) |

### Variáveis de ambiente

Nenhuma variável é obrigatória para o build atual (dados via `getDashboardData()` em memória).

Quando integrar a API ForceIA:

| Nome | Obrigatória no build? | Descrição |
|------|------------------------|-----------|
| `NEXT_PUBLIC_API_URL` | Não | Base URL da API admin/backend |

### Por que o deploy falhava em 1–2 segundos?

Se o **Root Directory** ficar na raiz do repositório (`/`), a Vercel não encontra `package.json` de Next.js e encerra imediatamente. O `package.json` do Dashboard está em `dashboard/package.json`.

## Dados / API

Toda a tela consome `getDashboardData()` em `lib/dashboard-data.ts`.

Tipos em `types/dashboard.ts`. Substitua a função por fetch à API quando disponível.

## Estrutura

```
dashboard/
├── app/
├── components/
│   ├── dashboard/
│   ├── layout/
│   └── ui/
├── lib/
├── types/
├── package.json
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── postcss.config.mjs
```
