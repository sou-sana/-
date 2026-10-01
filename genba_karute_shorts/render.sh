#!/bin/sh
# SVG → PNG(1080x1920) を headless Chromium で書き出す
# usage: ./render.sh [フォルダ]   (省略時はカレント。img1〜4.svg → img1〜4.png)
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
DIR=$(cd "${1:-.}" && pwd)
for i in 1 2 3 4; do
  $CH --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=1080,2100 \
      --screenshot="$DIR/raw$i.png" "file://$DIR/img$i.svg" >/dev/null 2>&1
  convert "$DIR/raw$i.png" -crop 1080x1920+0+0 +repage "$DIR/img$i.png" && rm "$DIR/raw$i.png"
done
