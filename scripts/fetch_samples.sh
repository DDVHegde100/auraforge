#!/usr/bin/env bash
# download a few libre (cc0/public domain) sample images for local demos
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/samples"
mkdir -p "$OUT"

# wikimedia / public domain stills (small set)
declare -a URLS=(
  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/640px-Cat03.jpg|portrait_cat.jpg"
  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Solem_sunset.jpg/640px-Solem_sunset.jpg|landscape_sunset.jpg"
)

echo "fetching samples into $OUT"
for entry in "${URLS[@]}"; do
  url="${entry%%|*}"
  name="${entry##*|}"
  dest="$OUT/$name"
  if [[ -f "$dest" ]]; then
    echo "  skip $name"
    continue
  fi
  if curl -fsSL "$url" -o "$dest"; then
    echo "  ok  $name"
  else
    echo "  fail $name (network?) — continue"
    rm -f "$dest"
  fi
done

cat > "$OUT/README.md" <<'EOF'
optional demo images. licensed as noted on their source pages (wikimedia).
not required to run auraforge — open any local photo instead.
EOF

echo "done"
