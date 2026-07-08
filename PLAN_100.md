# 100-commit development plan

path: empty folder → fully working **local web** auraforge  
assumes informal commit style when publishing the standalone repo; here IDs are ordered scopes.

legend: `[engine]` `[looks]` `[web]` `[docs]` `[test]` `[showcase]`

---

## milestone 0 — repo skeleton (commits 001–008)

| # | commit intent | delivers |
|---|---------------|----------|
| 001 | init python package layout | `packages/engine` pyproject |
| 002 | init vite react local app | `packages/web` |
| 003 | root readme + install script | one-command `./dev.sh` |
| 004 | gitignore + license mit | publishable |
| 005 | shared types for look json | schema.ts / schema.py |
| 006 | look registry stub | load empty catalog |
| 007 | sample libre image download script | optional samples |
| 008 | smoke test harness | pytest + vitest wired |

**exit:** `dev.sh` starts api+ui blank shell.

---

## milestone 1 — io + preview (009–018)

| # | intent |
|---|--------|
| 009 | load jpeg/png |
| 010 | load tiff 8/16 |
| 011 | raw via rawpy (optional dep) |
| 012 | export jpeg |
| 013 | export tiff16 |
| 014 | preview downscale helper |
| 015 | fastapi `/process/preview` |
| 016 | web drag-drop open file |
| 017 | before canvas only |
| 018 | roundtrip test fixtures |

**exit:** open local file, see it in UI, download same-ish jpeg.

---

## milestone 2 — scene analysis (019–030)

| # | intent |
|---|--------|
| 019 | luminance histogram features |
| 020 | lab mean / contrast / sat stats |
| 021 | wb grey-world + white-patch |
| 022 | noise flat-patch estimate |
| 023 | center saliency proxy |
| 024 | exposure class enum |
| 025 | content guess: portrait/land/food heuristics |
| 026 | sky score v0 (color+position) |
| 027 | face/skin score v0 (hsv skin) |
| 028 | `analyze()` returns JSON to UI |
| 029 | debug overlay panel in web |
| 030 | analysis golden tests |

**exit:** UI shows “scene: portrait, sky:0.2, exposure:flat…” for any image.

---

## milestone 3 — develop ops + recipe (031–045)

| # | intent |
|---|--------|
| 031 | exposure stops |
| 032 | shadow lift luminosity |
| 033 | highlight recovery |
| 034 | contrast midtone |
| 035 | vibrance / sat |
| 036 | clarity / local contrast |
| 037 | warmth / temp tint |
| 038 | mild denoise |
| 039 | dehaze lite |
| 040 | vignette |
| 041 | recipe mapper from analysis |
| 042 | strength 0–100 mixer |
| 043 | modes: natural/portrait/land/food/glow |
| 044 | `/enhance` api |
| 045 | enhance slider live preview (debounced) |

**exit:** **AI Enhance** slider works like neo accent (explicit recipe).

---

## milestone 4 — masks (046–055)

| # | intent |
|---|--------|
| 046 | soft algorithmic sky mask |
| 047 | sky mask feather |
| 048 | sky enhancer tone |
| 049 | skin soft mask |
| 050 | skin protect constraint |
| 051 | subject lightness from skin/center |
| 052 | mask debug view toggle |
| 053 | onnx sky option stub (optional) |
| 054 | combine enhance + sky |
| 055 | mask unit tests |

**exit:** sky pops without frying trees; portraits keep skin.

---

## milestone 5 — glow / light / detail stack (056–065)

| # | intent |
|---|--------|
| 056 | orton glow |
| 057 | highlight bloom |
| 058 | soft haze / atmosphere |
| 059 | floating light gradient |
| 060 | rim / edge light |
| 061 | multi-scale detail |
| 062 | film grain |
| 063 | split tone engine |
| 064 | false-color (thermal map) |
| 065 | channel offset / creative fringe |

**exit:** creative primitives ready for 20 signatures.

---

## milestone 6 — 40 color grades (066–075)

| # | intent |
|---|--------|
| 066 | grade json schema + loader |
| 067 | portrait grades 1–5 |
| 068 | portrait grades 6–10 |
| 069 | food grades 1–6 |
| 070 | landscape grades 1–8 |
| 071 | street + wedding grades |
| 072 | cinema + still grades |
| 073 | grade browser ui (filters by tag) |
| 074 | grade + enhance stacking order |
| 075 | grade perceptual QA notes in LOOKS |

**exit:** all **40** selectable; stacking with enhance.

---

## milestone 7 — 20 signature looks (076–085)

| # | intent |
|---|--------|
| 076 | signature registry |
| 077 | floating light + halo dawn + velvet |
| 078 | prism + thermal + infrared |
| 079 | neon noir + liquid sun + godray |
| 080 | porcelain + cinema fog + ember |
| 081 | arctic + biolume + paper print |
| 082 | hyper clarity + moon milk + spectrum |
| 083 | golden dust + editorial chrome |
| 084 | experimental badge + pro-safe clamp |
| 085 | signature gallery thumbs in ui |

**exit:** all **20** unique looks render distinctly.

---

## milestone 8 — polish local web (086–093)

| # | intent |
|---|--------|
| 086 | before/after scrubber |
| 087 | history undo (session) |
| 088 | export dialog jpeg/tiff |
| 089 | batch folder mode (local paths) |
| 090 | keyboard shortcuts |
| 091 | dark editor chrome (lightweight css) |
| 092 | performance: preview cache |
| 093 | offline error states |

**exit:** usable daily driver for local files.

---

## milestone 9 — showcase + docs ship (094–100)

| # | intent |
|---|--------|
| 094 | `/showcase` route |
| 095 | generate before/after tiles script |
| 096 | research summary page in app |
| 097 | a6000 bridge optional profile |
| 098 | CONTRIBUTING + split-repo instructions |
| 099 | release v0.1.0 changelog |
| 100 | “ready for public github” checklist pass |

**exit criterion for commit 100:**

1. clone (as own repo) + `./dev.sh`  
2. open any local portrait/food/landscape image  
3. AI Enhance slider transforms perceptually  
4. pick any of 40 grades + any of 20 signatures  
5. see showcase page  
6. export works offline  

---

## effort estimate

| milestone | approx calendar (solo part-time) |
|-----------|----------------------------------|
| 0–1 | 3–7 days |
| 2–3 | 1–2 weeks |
| 4–5 | 1–2 weeks |
| 6–7 | 2–3 weeks |
| 8–9 | 1 week |

total: **~6–10 weeks** to commit 100 local MVP (not full neo generative suite).

---

## out of scope until after 100

- cloud SaaS / accounts  
- gen erase / gen expand diffusion  
- mobile apps  
- full Lightroom catalog replacement  
- training large aesthetic nets on AVA (may use AVA *insights*; training is post-100)

---

## commit messaging when this becomes its own repo

keep short + lowercase, e.g. `sky mask soft`, `portrait grades`, `enhance slider` — same vibe as a6000-enhancer history, but **real incremental implementations** (not backdated theater unless you explicitly want timeline craft again).

---

## next action after this plan

start **001–008** when you say “build auraforge” — scaffold packages and `dev.sh` without touching a6000_enhancer’s public history unless you choose to.
