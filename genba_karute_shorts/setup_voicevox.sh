#!/bin/sh
# VOICEVOX CORE(オフラインTTS)一式を ./vv に用意する。
# 4.vvm = 玄野武宏・剣崎雌雄(ノーマル=style 21)。他の声を使うなら該当 .vvm を追加する。
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q \
  https://github.com/VOICEVOX/voicevox_core/releases/download/0.16.2/voicevox_core-0.16.2-cp310-abi3-manylinux_2_34_x86_64.whl
mkdir -p vv/models
cd vv
[ -d onnxruntime ] || { curl -sSL https://github.com/VOICEVOX/onnxruntime-builder/releases/download/voicevox_onnxruntime-1.17.3/voicevox_onnxruntime-linux-x64-1.17.3.tgz | tar xz && mv voicevox_onnxruntime-linux-x64-1.17.3 onnxruntime; }
[ -d dict ] || { curl -sSL https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-1.11.tar.gz | tar xz && mv open_jtalk_dic_utf_8-1.11 dict; }
[ -f models/4.vvm ] || curl -sSLf -o models/4.vvm https://github.com/VOICEVOX/voicevox_vvm/releases/download/0.16.2/4.vvm
echo "VOICEVOX ready"
