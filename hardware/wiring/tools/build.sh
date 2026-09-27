#!/usr/bin/env bash
# Regenerate every output in hardware/wiring/ from its source and check it.
#
#   <build>.yml   --wireviz-->  <build>.svg, <build>.png, <build>.bom.tsv
#   system.dot    --dot------>  system_block_diagram.svg, .png
#   tools/pinout.py --------->  pinout.svg  --rsvg-convert|cairosvg-->  pinout.png
#   tools/check_wiring.py --->  checks the harnesses against tools/wiring_data.py
#                               (SPEC.md 3.1 pin map, colours, BOM jumper counts)
#                               and refreshes the generated tables in README.md
#
# Needs: WireViz 0.4.1 (pip install wireviz==0.4.1), Graphviz (dot), Python 3,
#        and rsvg-convert (librsvg2-bin) or cairosvg (pip install cairosvg).
# Usage: hardware/wiring/tools/build.sh          (from any directory)
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1   # keep tools/ free of __pycache__

WIRING="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WIRING"

BUILDS=(desktop_lcd stage_ht16k33 budget_tm1637 legacy_max7219)

need() { command -v "$1" >/dev/null 2>&1 || { echo "build.sh: '$1' not found. $2" >&2; exit 1; }; }
need python3 "Install Python 3."
need dot "Install Graphviz (e.g. sudo apt install graphviz)."
need wireviz "Install WireViz: pip install wireviz==0.4.1"

wv_version="$(wireviz -V 2>/dev/null | tr -d '\r' | awk '/WireViz/ {print $2}')"
if [[ "$wv_version" != "0.4.1" ]]; then
  echo "build.sh: warning: WireViz $wv_version found, the harnesses are written for 0.4.1" >&2
fi

svg2png() {  # svg2png <in.svg> <out.png> <width-px>
  if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w "$3" -b white -o "$2" "$1"
  elif python3 -c "import cairosvg" >/dev/null 2>&1; then
    python3 -c 'import sys, cairosvg; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=int(sys.argv[3]))' "$1" "$2" "$3"
  else
    echo "build.sh: need rsvg-convert (sudo apt install librsvg2-bin) or cairosvg (pip install cairosvg) for $2" >&2
    exit 1
  fi
}

echo "== WireViz harnesses"
for b in "${BUILDS[@]}"; do
  wireviz -f pst "$b.yml" >/dev/null
  rm -f "$b.gv" "$b.html" "$b.tmp.svg" "$b"   # intermediates / outputs we do not keep
  echo "   $b.yml -> $b.svg $b.png $b.bom.tsv"
done

echo "== System block diagram"
dot -Tsvg system.dot -o system_block_diagram.svg
dot -Tpng -Gdpi=150 system.dot -o system_block_diagram.png
echo "   system.dot -> system_block_diagram.svg system_block_diagram.png"

echo "== Pinout"
python3 tools/pinout.py -o pinout.svg >/dev/null
svg2png pinout.svg pinout.png 1800
echo "   tools/pinout.py -> pinout.svg pinout.png"

echo "== Checks"
python3 tools/check_wiring.py --update-readme

for f in "${BUILDS[@]/%/.svg}" "${BUILDS[@]/%/.png}" "${BUILDS[@]/%/.bom.tsv}" \
         system_block_diagram.svg system_block_diagram.png pinout.svg pinout.png; do
  [[ -s "$f" ]] || { echo "build.sh: missing output $f" >&2; exit 1; }
done
echo "build.sh: all outputs up to date in $WIRING"
