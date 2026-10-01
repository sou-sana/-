#!/bin/sh
# SVG → PNG(1080x1920) を headless Chromium で書き出す
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
for i in 1 2 3 4; do
  $CH --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=1080,2100 \
      --screenshot="$PWD/raw$i.png" "file://$PWD/img$i.svg" >/dev/null 2>&1
  convert raw$i.png -crop 1080x1920+0+0 +repage img$i.png && rm raw$i.png
done
