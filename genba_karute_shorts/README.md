# げんばのカルテ 縦型ショート 自動生成

完成動画: `outputs/笑わなくなった_げんばのカルテ.mp4`(1080×1920 / 30fps / H.264 + AAC / 34.2秒)

## 再生成

```sh
apt-get install -y fonts-noto-cjk     # 字幕フォント(Noto Sans CJK JP Bold)
pip install pillow numpy scipy --break-system-packages
./setup_voicevox.sh                   # オフラインTTS(VOICEVOX CORE)一式を ./vv に取得
python3 make_images.py && ./render.sh # img1〜4.svg → img1〜4.png(差し替えるなら不要)
python3 build.py                      # storyboard.json → outputs/<title>.mp4(BGMも自動生成)
```

他の回を作るときは `storyboard.json`(ナレーション・字幕・画像番号)と `img1.png`〜`img4.png` を差し替えて `python3 build.py` を実行する。画像は1080×1920にcover配置されるので、縦長ならサイズは問わない。

## 差し替え集(episodes/)

`episodes/<回>/` に、1本分の `storyboard.json`・`img1〜4.svg/png`・`投稿用テキスト.txt`(題名/概要欄/固定コメント)・`timeline.json` が入っている。完成動画は `outputs/` に出力される。

| フォルダ | 完成動画(outputs/) | 尺 |
|---|---|---|
| kanjo3_yasumi | 休みの日に何もする気が起きなかった_げんばのカルテ.mp4 | 33.8秒 |
| kanjo4_namida | 些細なことで涙が出るようになった_げんばのカルテ.mp4 | 33.9秒 |
| kanjo5_ajike | 好きだったものが味気なく感じるようになった_げんばのカルテ.mp4 | 34.1秒 |
| tenshoku1_erabikata | 転職サイトは選び方で9割決まる_げんばのカルテ.mp4 | 44.1秒 |
| tenshoku2_yakin_nashi | 夜勤なしを本当に叶える看護師がやっていること_げんばのカルテ.mp4 | 37.2秒 |
| tenshoku3_koukai | 転職で後悔する看護師のたった1つの共通点_げんばのカルテ.mp4 | 39.8秒 |
| fukugyo1_tsugi_no_michi | 夜勤に疲れた看護師の次の道_げんばのカルテ.mp4 | 37.9秒 |
| fukugyo2_artmake | アートメイク看護師のリアル_げんばのカルテ.mp4 | 35.9秒 |

```sh
python3 episode_images.py kanjo3_yasumi            # img1〜4.svg を描く(省略で全回)
./render.sh episodes/kanjo3_yasumi                 # → img1〜4.png
python3 build.py episodes/kanjo3_yasumi/storyboard.json
```

`build.py` は `storyboard.json` と同じフォルダの `img1〜4.png` を使う。画像はプロンプトの方針に沿って `episode_images.py` が描いたSVGイラストで、Canva等で生成した画像に差し替える場合は同名のPNGを置いて `build.py` だけを再実行する。

## 仕様(build.py)

- カット尺 = ナレーション長 + 0.8秒(最終カットのみ +2.0秒の余韻を追加)
- 画像切り替えは0.3秒のクロスフェード。ズームなどの動きは入れていない
- 字幕: 全幅の濃紺(#0F2A3D)半透明帯 + 白文字、Noto Sans CJK JP Bold 60px、帯の中心 y=1540。0.2秒フェード
- 音声: VOICEVOX「剣崎雌雄(ノーマル)」、プリセット「げんばのカルテ」= 話速1.10・音高-0.03・抑揚0.81・音量1.00・開始/終了無音0.10(`storyboard.json` の `voice`)。-16 LUFSに正規化。「間の長さ」はVOICEVOX COREに項目がないが、値1.00は既定値なので結果は同じ
- BGM: `make_bgm.py` が合成するネイチャー系アンビエント(やわらかいパッド和音+小川/そよ風+まれなチャイム)。外部素材なし。ナレーション比 -16dB(単体で約 -32 LUFS)で敷く。`storyboard.json` の `bgm.gain_db` で調整、`bgm` を消せば無音
- `build/timeline.json` に各カットの開始/終了秒が出る

## 指示書との違い

- **TTS**: edge-tts の接続先 `speech.platform.bing.com` は、この環境のネットワークポリシーでブロック(403)された。代わりにオフラインで動く VOICEVOX を使っている。クレジット表記「VOICEVOX:剣崎雌雄」が必要(概要欄に入れる)。
- **画像**: Canva の画像生成で4枚を生成したが、`canva.com` もネットワークでブロックされており、フル解像度を取得できなかった(取得できたのは112×199のサムネイルのみ)。動画には、同じプロンプトの方針(輪郭線のみ・顔なし・白/青/緑の淡い配色・文字なし)で `make_images.py` が描いたSVGイラストを使っている。Canva版を使う場合は、下のリンクから1080×1920以上でダウンロードし、`img1.png`〜`img4.png` を置き換えて `python3 build.py` を実行する。
  - 画像1: https://www.canva.com/M/MAHWwzJPoCQ
  - 画像2: https://www.canva.com/M/MAHWw1BGT5o
  - 画像3: https://www.canva.com/M/MAHWw7POtIc
  - 画像4: https://www.canva.com/M/MAHWwwn4fb4

## 投稿用メタ

**題名**: 「笑わなくなったことに、気づいていなかった」ある看護師の話

**概要欄**:
```
笑わなくなるのは、疲れじゃなく心が省エネに入ったサインかもしれない。

心が職場から離れ始めるとき、人には共通のサインがあります。
このチャンネルでは、看護師の"辞めどき"と働き方を、心理学と行動経済学の視点から言葉にしています。

━━━━━━━━━━
▼無料の《辞めどきの4段階チェック》をLINEで
登録は【チャンネルのリンク】から(ショートは概要欄のリンクが押せないため)
※PCの方は下記からも → https://line.me/R/ti/p/@917mzprz

▼解説・本編「なぜ人は"辞めどき"を逃すのか」もチャンネルから
━━━━━━━━━━

音声:VOICEVOX:剣崎雌雄

#看護師 #看護師転職 #医療 #心理学 #行動経済学 #shorts
```

**固定コメント**:
```
「辞めどきの4段階チェック」を無料でお届けしています。
今の自分がどの段階にいるか、確かめてみてください。
▼LINEで受け取る
チャンネルページの【リンク】から登録できます(ショートはコメントのリンクが押せないため)
※PCの方はこちらからも → https://line.me/R/ti/p/@917mzprz
```
