"""今日（日本時間）に必要な確認・更新を判定し、Issue本文を reminders/ に書き出す。

ルールは .claude/skills/josetsuki/references/operations.md と同じ。変えたら両方直す。
usage: python josetsuki_reminders/remind.py [YYYY-MM-DD]
出力: josetsuki_reminders/out/<番号>.md（1行目がタイトル）。何もない日は出力なし
"""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "out"
WD = "月火水木金土日"

SEND = "\n**このチャット（Claude）に送るもの**：上の画面のスクリーンショット。数字の読み取りと、直す記事・次の企画はこちらで決めます。\n"

WEEKLY = """## 確認する（10〜15分）
- [ ] Search Console「検索パフォーマンス」（直近7日）：表示回数・クリック・平均掲載順位、「クエリ」と「ページ」のタブ
- [ ] Search Console「ページ」：未登録の記事がないか（あれば URL検査 →「インデックス登録をリクエスト」）
- [ ] GA4「集客」：youtube / video・comment・channel の流入
- [ ] GA4「エンゲージメント」→「イベント」→ click（除雪機ネットへのクリック）
- [ ] はてなブログ「アクセス解析」：今週のアクセス数と参照元
- [ ] 除雪機ネットのアフィリエイト管理画面：訪問者数・販売件数
- [ ] YouTube Studio アナリティクス（直近7日）：横動画の再生、ショートの視聴を継続

## 更新する
- [ ] 在庫まとめ記事の「最終更新」日付（在庫に変化がなくても更新）
- [ ] 戦略メモの数字（Claudeが更新）
"""

WEATHER = """
## 季節の確認（10〜12月）
- [ ] 札幌管区気象台・気象庁：週間予報で大雪・初雪の予報がないか（あれば「大雪の前に」企画をすぐ作る）
"""

MONTHLY = """## 確認する
- [ ] メーカー公式（Honda・ヤマハ・Willbe・Wado）の新製品・仕様変更・お知らせ（Claudeが検索）
- [ ] 自治体の除雪機購入補助（札幌市など。2026年度の受付時期と条件）
- [ ] 競合・参考サイトの上位5つ（「除雪機 おすすめ」「除雪機 北海道」で検索。気になったページはこのチャットに貼る）
- [ ] YouTubeコメント・Yahoo!知恵袋で多い質問

## 更新する
- [ ] 各記事の仕様と「最終更新」の見直し
- [ ] 制作キューの並べ替え（反応の良かった型を優先）
- [ ] 参考サイトの分析を戦略メモ9章に追記
"""

SEASONAL = {
    (11, 1): ("11月の企画：安全・補助金", """- [ ] 「除雪機の事故を防ぐ5つのNG」記事＋ショート（素材 Q7）
- [ ] 補助金：2026年度の札幌市などの条件を確認して記事化
- [ ] 11〜12月は週次チェックを月・木の週2回に（自動で木曜にも届きます）
"""),
    (12, 1): ("12月の企画：大雪・故障・点検", """- [ ] 「エンジンがかからない・雪が詰まる」など故障の記事＋ショート
- [ ] 「大雪の前に点検するところ」ショート（素材 Q6）
- [ ] 在庫まとめ：年末年始の配送・納期の注意を追記
"""),
    (3, 1): ("3月の企画：保管・買い替え", """- [ ] 「シーズンオフの保管」記事＋ショート
- [ ] 「古い除雪機、修理か買い替えか」（素材 Q9）
- [ ] 来シーズンに向けて、今季の数字を戦略メモにまとめる
"""),
}


def posts_due(today):
    data = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    items = []
    for p in data["posts"]:
        d = dt.date.fromisoformat(p["date"])
        if today - d == dt.timedelta(days=1):
            items.append(f"- [ ] 「{p['title']}」（{p['date']}投稿）のコメントを見る。誤りの指摘・質問はこのチャットに貼る")
        if today - d == dt.timedelta(days=2):
            items.append(f"- [ ] 「{p['title']}」（{p['date']}投稿）の分析：再生回数・**視聴を継続**・維持率グラフ・平均視聴時間をスクショで送る")
    return items


def todos_due(today):
    """posts.json の todos（日付つきの予定）から今日の分を返す。"""
    data = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    items = []
    for t in data.get("todos", []):
        if dt.date.fromisoformat(t["date"]) == today:
            items += [f"- [ ] {x}" for x in t["items"]]
    return items


def build(today):
    label = f"{today.isoformat()}（{WD[today.weekday()]}）"
    issues = []
    m, wd = today.month, today.weekday()
    if wd == 0 or (wd == 3 and m in (11, 12)):
        body = WEEKLY + (WEATHER if m in (10, 11, 12) else "") + SEND
        issues.append((f"【週次チェック】{label}", body))
    if today.day == 1:
        issues.append((f"【月次チェック】{label}", MONTHLY + SEND))
    if (m, today.day) in SEASONAL:
        name, body = SEASONAL[(m, today.day)]
        issues.append((f"【{name}】{label}", body + "\n企画を始めるときは、このチャットに「始めて」と送ってください。\n"))
    todo = todos_due(today)
    if todo:
        issues.append((f"【今日の予定】{label}", "\n".join(todo) + "\n\n終わったら、このチャット（Claude）に知らせてください。\n"))
    due = posts_due(today)
    if due:
        issues.append((f"【投稿後チェック】{label}", "\n".join(due) + "\n" + SEND))
    return issues


def main():
    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else \
        dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.md"):
        f.unlink()
    for i, (title, body) in enumerate(build(today)):
        (OUT / f"{i}.md").write_text(title + "\n" + body, encoding="utf-8")
        print(title)


if __name__ == "__main__":
    main()
