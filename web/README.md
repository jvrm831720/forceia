# ForceIA Admin Web (React + Vite)

Painel admin como **aplicação React**, não HTML puro.

## Desenvolvimento

```bash
# terminal 1 — API
cd agents && python admin_server.py   # :8100

# terminal 2 — UI
cd web && npm install && npm run dev  # :5173 (proxy /api → :8100)
```

Abra http://localhost:5173

## Produção

```bash
cd web && npm install && npm run build
# admin_server serve web/dist automaticamente em /
```

## Stack

- React 19 + TypeScript + Vite 8
- CSS moderno (grid ambient, shimmer, blur-fade, bento)
- Auth JWT via `/api/auth/login`
- Consome a API FastAPI existente
