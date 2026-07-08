# contributing

auraforge is its own repo. clone it standalone — do not depend on the parent `a6000` monorepo layout.

## setup

```bash
git clone https://github.com/DDVHegde100/auraforge.git
cd auraforge
chmod +x dev.sh
./dev.sh
```

open http://127.0.0.1:5173 (web) and http://127.0.0.1:8787/health (api).

## repo layout

```
packages/engine/   python image pipeline (fastapi + numpy/opencv)
packages/web/      vite + react local ui
data/looks/        grade + signature JSON recipes
tests/engine/      pytest suite
scripts/           showcase tile generator, sample fetcher
```

## making changes

1. edit engine code under `packages/engine/auraforge_engine/`
2. run `pytest tests/engine -q` from repo root (venv active)
3. edit web under `packages/web/src/`
4. keep commits small and lowercase (e.g. `sky mask soft`, `export dialog jpeg tiff`)

## split-repo note

this project may live nested under `/a6000/auraforge` during development but publishes to **https://github.com/DDVHegde100/auraforge** as an independent history. do not require `a6000_enhancer` at runtime.

optional bridge: enable the a6000 base profile in the editor when EXIF says ILCE-6000 — implemented locally in `auraforge_engine/profiles/a6000.py`.

## raw files

```bash
pip install -e "packages/engine[raw]"
```

## showcase tiles

```bash
./scripts/fetch_samples.sh   # optional demo images
python scripts/generate_showcase_tiles.py
```
