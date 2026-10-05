#!/bin/sh
# imgNN.svg → imgNN.png(1920x1080)。imgNN.png を別途用意した番号は上書きしない(KEEP_PNG=1 のとき)
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
for f in img*.svg; do
  n=${f%.svg}
  [ "$KEEP_PNG" = 1 ] && [ -f "$n.png" ] && continue
  $CH --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=1920,1300 \
      --screenshot="$PWD/raw_$n.png" "file://$PWD/$f" >/dev/null 2>&1
  convert "raw_$n.png" -crop 1920x1080+0+0 +repage "$n.png" && rm "raw_$n.png"
done
