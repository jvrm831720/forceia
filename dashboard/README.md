# ForceIA · Dashboard (Cliente)

Console premium para o **cliente** da ForceIA acompanhar a equipe de vendas com IA em tempo real.

> A ForceIA não é um CRM. O cliente não configura agentes, prompts ou automações — a operação é gerida pela equipe ForceIA. O Dashboard transmite: *“minha equipe de IA está trabalhando e eu acompanho tudo ao vivo.”*

## Stack

- Next.js 14.2.35 (App Router)
- TypeScript (strict)
- Tailwind CSS
- Lucide Icons
- Componentes no estilo shadcn/ui
- Node.js 24.x

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

## Instalar e rodar local

```bash
cd dashboard
npm ci          # preferível (lockfile versionado)
# ou: npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

### Build de produção local

```bash
cd dashboard
npm ci
npx tsc --noEmit
npm run build
npm run start
```

## Deploy na Vercel (obrigatório)

Este repositório é um **monorepo**. A aplicação Next.js do Painel Cliente fica em `dashboard/`.

Na Vercel, configure:

| Campo | Valor |
|--------|--------|
| **Framework Preset** | Next.js |
| **Root Directory** | `dashboard` |
| **Install Command** | `npm install` |
| **Build Command** | `npm run build` |
| **Output Directory** | *deixar vazio* (Next.js gerencia `.next`) |
| **Node.js** | **24.x** |

O arquivo `.nvmrc` e `package.json#engines.node` estão em `24`.

### Por que o deploy falhava em 1–2 segundos?

Se o **Root Directory** ficar na raiz do repositório (`/`), a Vercel não encontra `package.json` de Next.js e encerra imediatamente. O `package.json` do Dashboard está em `dashboard/package.json`.

## Variáveis de ambiente

Nenhuma variável é **obrigatória** para o build ou runtime atual (dados mock em memória).

Quando integrar a API ForceIA:

| Nome | Pública? | Obrigatória no build? | Obrigatória em runtime? | Descrição |
|------|----------|------------------------|--------------------------|-----------|
| `NEXT_PUBLIC_API_URL` | Sim | Não | Sim (após integração) | Base URL da API admin/backend |

Não coloque secrets com prefixo `NEXT_PUBLIC_`.

## Autenticação (mock)

Login e “esqueci minha senha” usam mocks isolados em:

- `lib/auth/login.ts`
- `lib/auth/request-password-reset.ts`

Em **produção** (`NODE_ENV === "production"`), o mock de demonstração é **desativado** e retorna erro de conexão até a API real ser conectada. Em desenvolvimento, e-mail qualquer + senha `forceia` autentica; `disabled@forceia.com` e `fail@forceia.com` simulam falhas.

Substitua o corpo das funções pela integração real (cookie httpOnly no servidor). **Não** persistir tokens em `localStorage`.

## Rotas existentes

| Rota | Descrição |
|------|-----------|
| `/` | Home / visão geral |
| `/conversas` | Inbox de conversas |
| `/login` | Login |
| `/esqueci-minha-senha` | Recuperação de senha |
| `/agenda` | Agenda (placeholder) |
| `/leads` | Leads (placeholder) |
| `/resultados` | Resultados (placeholder) |
| `/suporte` | Suporte (placeholder) |

## Dados / API

- Home: `getDashboardData()` em `lib/dashboard-data.ts`
- Conversas: `getConversations()` em `lib/getConversations.ts`
- Tipos: `types/dashboard.ts`, `types/conversation.ts`, `types/auth.ts`

Substitua as funções por fetch à API quando disponível.

## Estrutura

```
dashboard/
├── app/
├── components/
│   ├── auth/
│   ├── conversations/
│   ├── dashboard/
│   ├── layout/
│   └── ui/
├── lib/
│   └── auth/
├── types/
├── package.json
├── package-lock.json
├── .nvmrc
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── postcss.config.mjs
```
