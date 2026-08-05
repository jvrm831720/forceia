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

## Deploy (Vercel)

```bash
cd dashboard && npx vercel
```

## Dados / API

Toda a tela consome `getDashboardData()` em `lib/dashboard-data.ts`.

Tipos em `types/dashboard.ts`.
