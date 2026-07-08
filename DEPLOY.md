# Deploy auraforge

## Architecture

| Layer | Host | Notes |
|-------|------|-------|
| **Web** | [Vercel](https://vercel.com) | Static Vite SPA from `packages/web/dist` |
| **API** | Railway / Fly / Docker | Python FastAPI + OpenCV image engine |

The web app proxies `/api/*` to your hosted API in production (see `vercel.json`).

## 1. Deploy API (Railway recommended)

```bash
# From repo root — uses Dockerfile
railway up
```

Set environment variables on Railway:

- `AURAFORGE_CORS_ORIGINS` — your Vercel URL, e.g. `https://auraforge.vercel.app`
- `AURAFORGE_SESSION_DIR` — `/tmp/auraforge-sessions`
- `AURAFORGE_EXPORT_DIR` — `/tmp/auraforge-exports`
- `PORT` — `8787`

Health check: `GET /health`

## 2. Deploy Web (Vercel)

1. Import GitHub repo in Vercel
2. Root directory: `auraforge` (or repo root if monorepo)
3. Build: `cd packages/web && npm ci && npm run build`
4. Output: `packages/web/dist`
5. Update `vercel.json` rewrite destination to your Railway API URL
6. Optional: set `VITE_API_BASE=https://your-api.railway.app` to bypass rewrite

## 3. Local dev

```bash
./dev.sh
# web → http://127.0.0.1:5173
# api → http://127.0.0.1:8787
```

## 4. Docker (self-host)

```bash
docker compose up --build
# API on :8787
```

Point Vercel `VITE_API_BASE` at your public API URL.

## Limits

- Max upload default: 40 MB (set `AURAFORGE_MAX_UPLOAD_MB`)
- Sessions stored on disk with TTL (survives API restarts on Railway volume)
- Export jobs async for large files — poll `GET /jobs/{id}` then download
