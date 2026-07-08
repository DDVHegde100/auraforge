# auraforge

Local aesthetic photo studio — scene analysis, pro develop, **30 camera emulations** with film-stock color science, 40 grades, 20 signatures.

```bash
chmod +x dev.sh
./dev.sh
```

Open **http://127.0.0.1:5173**

| route | purpose |
|-------|---------|
| `/` | editor (Lightroom-style studio UI) |
| `/showcase` | before/after look pairs |
| `/research` | algorithm notes |

## Deploy (Vercel + Railway)

- **Web** → Vercel (static SPA, see `vercel.json`)
- **API** → Railway or Docker (`Dockerfile`, `docker-compose.yml`)

Full steps in [`DEPLOY.md`](DEPLOY.md).

```bash
# self-host API
docker compose up --build
```

Set `VITE_API_BASE` on Vercel to your public API URL.

## Camera emulations

Pro cameras use a dedicated pipeline:

- **Film stock curves** — Portra, Ektar, CineStill, Velvia, Tri-X, Vision3, etc.
- **Lens profiles** — Zeiss, Summicron, cinema MTF falloff
- **Structured grain** — ISO-aware, shadow-weighted emulsion
- **Halation** — CineStill tungsten highlight bleed

Examples: Leica M6, Contax T2, Hasselblad 500C, ARRI Alexa, CineStill 800T, Phase One IQ4.

## Export

- Live preview via session API (upload once, tune many times)
- Full-res JPEG or 16-bit TIFF download
- Async export jobs for large images (`POST /process/export/async` → poll → download)

## Tests

```bash
cd packages/engine && pip install -e ".[dev]"
pytest tests/engine -q
```

100 tests passing.
