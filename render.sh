#!/bin/bash
# Renderiza cada img/*.svg (tema claro, a fonte) em PNG 2x no tema escuro da dash, pelo
# tema_escuro.py, com o Chrome headless carregando a DM Sans do Google Fonts. Fora do painel
# arredondado o PNG é transparente, para não parecer recortado no tema claro do Metabase.
# Uso: bash render.sh   (rodar depois de python3 gerar.py)
set -euo pipefail
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP="$(mktemp -d)"
for svg in img/*.svg; do
  name="$(basename "$svg" .svg)"
  read -r W H < <(python3 -c "import re,sys; s=open(sys.argv[1]).read(); m=re.search(r'viewBox=\"0 0 (\d+) (\d+)\"', s); print(m.group(1), m.group(2))" "$svg")
  {
    echo '<!doctype html><html><head><meta charset="utf-8">'
    echo '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=block" rel="stylesheet">'
    echo '<style>html,body{margin:0;padding:0;overflow:hidden;background:transparent}svg{display:block}</style></head><body>'
    python3 tema_escuro.py "$svg"
    echo '</body></html>'
  } > "$TMP/$name.html"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --default-background-color=00000000 \
    --window-size="$W,$H" --virtual-time-budget=8000 --screenshot="$PWD/img/$name.png" \
    "file://$TMP/$name.html" >/dev/null 2>&1
  echo "$name.png"
done
rm -rf "$TMP"
