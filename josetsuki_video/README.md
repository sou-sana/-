# 70cm除雪機3機種比較(ショート+横動画)

ブログ「北海道の除雪機選び」の70cm比較記事へ人を送るための動画2本。

- ショート: 1080×1920 / 約43秒(`storyboard_short.json`)
- 横動画: 1920×1080 / 2分42秒(`storyboard_long.json`)

## 再生成
```sh
../genba_karute_shorts/setup_voicevox.sh   # VOICEVOX(剣崎雌雄)。vv は ../genba_karute_shorts/vv へのリンク
apt-get install -y fonts-noto-cjk
pip install pillow numpy scipy --break-system-packages
python3 prep_images.py                     # src/ → images/(V2の車エンブレム、V4の機体の文字をぼかす)
python3 build_short.py && python3 build_long.py   # → outputs/
python3 make_cards_60.py && python3 build_short.py storyboard_short_60.json   # ショート2本目(60cm)
python3 make_thumbnail.py                  # 横動画のサムネイル → outputs/thumbnail_横動画.jpg(1280×720)
```
`src/P1_photo.jpg`(素材サイトの写真・商用利用可を確認済み)は再配布を避けるためリポジトリに含めていない。手元に置いてから実行する。

## 素材
- C1〜C4: Canvaで作ったスライド(ショートでは縦画面の中央に置き、背景にV1をぼかして敷く)
- A1/A2: Canva生成画像、A4/A5/V1〜V4: ユーザーが他のAIで作成、P1: 素材サイトの写真
- 除雪機が写る場面には「※イメージ」、冒頭4秒に「PR」を表示
- 型番の読みはTTSで自然に読めるよう、ナレーションでは「エイチエスエス970」のようにカナで書いている(字幕・スライドは正式な型番)

## 投稿用メタ
**横動画タイトル**: 70cm除雪機3機種比較｜HSS970nJ・SXC1070H・YSF1070T 差額で何が変わる？【北海道】

**横動画の概要欄**:
```
※この動画にはアフィリエイト広告(PR)を含みます。

▼3機種の詳しい比較(販売ページへのリンクあり)
https://josetsuki-hokkaido.hateblo.jp/entry/2026/10/06/221430?utm_source=youtube&utm_medium=video&utm_campaign=70cm

▼最新の在庫・価格まとめ
https://josetsuki-hokkaido.hateblo.jp/entry/2026/10/05/210159?utm_source=youtube&utm_medium=video&utm_campaign=70cm

価格・在庫は2026年10月5日時点で除雪機ネットに掲載されていた情報です。購入前に販売ページで最新情報をご確認ください。

0:00 はじめに
0:25 3機種の比較表
0:51 HSS970nJ
1:12 SXC1070H
1:37 YSF1070T
2:00 差額で何が変わる?
2:17 選び方まとめ

音声:VOICEVOX:剣崎雌雄
```

**ショートタイトル**: 70cm除雪機 51万・58万・63万は何が違う？ #除雪機 #北海道

**ショートの説明欄**:
```
※この動画にはアフィリエイト広告(PR)を含みます。
価格・在庫は2026年10月5日時点の情報です。
詳しい比較は関連動画をご覧ください。
音声:VOICEVOX:剣崎雌雄
#除雪機 #北海道 #除雪
```
概要欄のリンク末尾の `?utm_source=...` は、YouTube経由の訪問をGoogleアナリティクスで見分けるための目印。
在庫まとめのURLは投稿日時(10/5 21:01:59)からの推定なので、実際のURLと一致するか確認する。

投稿順: 横動画 → ショート(ショートの「関連動画」に横動画を設定)

## BGM
今後の動画は YouTubeオーディオライブラリの「Sunny Days - Anno Domini Beats」(帰属表示不要)を使う。
storyboard に `"bgm": {"file": "sunny_days.mp3", "gain_db": -18}` と書き、曲は `music/sunny_days.mp3` に置く(再配布しないため git には入れていない)。
`file` がない storyboard は従来どおり合成BGM(ショート: make_bgm.py、横: make_piano_bgm.py)を使う。
