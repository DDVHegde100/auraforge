# architecture — local-first web studio

goal: user clones repo → `npm`/`pip` install → opens `http://localhost:…` → picks **any local image** → enhance + looks → export. no cloud.

---

## monorepo (future separate github)

```
auraforge/
  docs/                 ← RESEARCH, LOOKS, PLAN (these files)
  packages/
    engine/             ← python image science core
    web/                ← local UI (vite + react)
  data/
    looks/              ← JSON recipes (60)
    samples/            ← optional libre demo imgs
  scripts/              ← showcase renders, fixtures
  README.md
```

while nested under `/a6000/auraforge`, treat as **independent git root** when published.

---

## engine (python)

```
engine/
  analysis/     scene_features.py, masks_sky.py, masks_skin.py, depth_proxy.py
  recipe/       accent.py, strength.py, constraints.py
  render/       develop.py, glow.py, grades.py, signatures.py
  io/           load.py, export.py, preview.py
  catalog/      registry.py   # loads JSON looks
```

pipeline:

```
load → analyze → build_recipe(mode) → apply_develop
     → apply_sky_optional → apply_grade_optional → apply_signature_optional
     → mix_by_strength → export/preview
```

reuse ideas from `../a6000_enhancer` (orton, bloom, denoise) via copy-or-import — keep auraforge publishable alone.

---

## web (local)

**stack pick (lightweight):**

- Vite + React + TypeScript
- FastAPI (or Starlette) on `localhost:8787` for process jobs
- Browser sends file as multipart OR file path via native file picker (no upload to third party)
- Preview: JPEG ≤ 1600px long edge returned base64 or object URL
- Export: download TIFF16 / JPEG from local response

UI panels:

1. open image  
2. **AI Enhance** slider + mode chips (natural / portrait / landscape / food / glow)  
3. **Grades** browser (40) with search by tag  
4. **Signatures** (20) with warning badge for experimental  
5. before/after scrubber  
6. showcase page  

---

## performance targets

| op | target |
|----|--------|
| preview 1200px enhance | < 1.5s CPU laptop |
| full 24MP JPEG export | < 8s CPU |
| optional onnx sky | +0.5–2s |

use downscale for analyze; upscale params to full-res render.

---

## privacy model

- zero telemetry by default  
- all processing on-device  
- optional “open folder watch” later  

---

## separation from a6000_enhancer

| | a6000_enhancer | auraforge |
|--|----------------|-----------|
| goal | RAW pre-Lightroom for Sony | aesthetic studio / neo-like |
| UI | tk + cli | local web |
| looks | few presets | 60 curated |
| enhance | camera develop | perception recipe + masks |

bridge: auraforge “camera pack” plugin that calls a6000 profile when EXIF says ILCE-6000.
