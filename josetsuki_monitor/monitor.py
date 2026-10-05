"""除雪機ネットの商品一覧から在庫数・価格を取得し、前回との差分を報告する。

使い方:
    python monitor.py            # 取得して差分を report.md に書き、state.json を更新
    python monitor.py --dry-run  # state.json を更新しない

終了コード: 0=変化なし, 10=変化あり(report.md あり), 1=取得・解析の失敗
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).parent
CONFIG = HERE / "config.json"
STATE = HERE / "state.json"
REPORT = HERE / "report.md"
JST = timezone(timedelta(hours=9))
HEADERS = {"User-Agent": "josetsuki-stock-check/1.0 (daily, 1 request per page)"}


def fetch(session, url):
    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    time.sleep(2)  # 相手サーバーへの負荷を抑える
    return BeautifulSoup(r.content, "html.parser")


def find_link(soup, base, text):
    for a in soup.find_all("a", href=True):
        if text in a.get_text(strip=True):
            return urljoin(base, a["href"])
    return None


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)  # 商品名に含まれる生の<font>タグを除去
    return re.sub(r"\s+", " ", s).strip()


def parse_products(soup, base):
    """商品一覧の表の行から {id: {name, price, qty, url}} を作る。"""
    products = {}
    for tr in soup.find_all("tr"):
        if tr.find("tr"):
            continue  # 入れ子の外側の行は飛ばす
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 3:
            continue
        qty_text = tds[-1].get_text(strip=True)
        if not re.fullmatch(r"\d+", qty_text):
            continue
        link = tr.find("a", href=re.compile(r"products_id"))
        if not link:
            continue
        m = re.search(r"products_id[=/](\d+)", link["href"])
        if not m:
            continue
        prices = [int(p.replace(",", "")) for p in re.findall(r"([\d,]{4,})円", tr.get_text())]
        names = [clean(a.get_text(" ")) for a in tr.find_all("a", href=re.compile(r"products_id"))]
        name = max(names, key=len) if names else ""
        products[m.group(1)] = {
            "name": name,
            "price": prices[-1] if prices else None,
            "qty": int(qty_text),
            "url": urljoin(base, link["href"]),
        }
    return products


def parse_ranking(soup):
    lines = [l.strip() for l in soup.get_text("\n").splitlines() if l.strip()]
    ranking = {}
    for i, line in enumerate(lines):
        m = re.match(r"^(\d{1,2})位\.\s*(.*)$", line)
        if not m:
            continue
        name = m.group(2) or (lines[i + 1] if i + 1 < len(lines) else "")
        rank = int(m.group(1))
        if rank not in ranking:
            ranking[rank] = clean(name)
    return [ranking[k] for k in sorted(ranking)]


def collect(cfg):
    session = requests.Session()
    url = cfg.get("list_url") or cfg["start_url"]
    soup = fetch(session, url)
    if not cfg.get("list_url"):
        for step in cfg["nav"]:
            nxt = find_link(soup, url, step)
            if not nxt:
                raise RuntimeError(f"リンク「{step}」が {url} に見つかりません。config.json の list_url に一覧ページのURLを直接入れてください。")
            url = nxt
            soup = fetch(session, url)
    ranking = parse_ranking(soup)
    products = {}
    for _ in range(cfg.get("max_pages", 10)):
        products.update(parse_products(soup, url))
        nxt = find_link(soup, url, "次ページ")
        if not nxt or nxt == url:
            break
        url = nxt
        soup = fetch(session, url)
    if not products:
        raise RuntimeError("商品を1件も読み取れませんでした。サイトの構造が変わった可能性があります。")
    return products, ranking


def is_watched(name, watch):
    return any(re.search(re.escape(w) + r"(?![A-Za-z0-9-])", name) for w in watch)


def yen(v):
    return f"{v:,}円" if v is not None else "不明"


def diff(old, new, watch):
    watched, others = [], []
    old_p, new_p = old.get("products", {}), new["products"]
    for pid, p in new_p.items():
        o = old_p.get(pid)
        if o is None:
            msg = f"新商品: {p['name']}（{yen(p['price'])}・数量{p['qty']}）"
        else:
            parts = []
            if o["qty"] != p["qty"]:
                parts.append(f"数量 {o['qty']}→{p['qty']}" + ("（売り切れ）" if p["qty"] == 0 else ""))
            if o["price"] != p["price"]:
                parts.append(f"価格 {yen(o['price'])}→{yen(p['price'])}")
            if o["name"] != p["name"]:
                parts.append(f"表示変更「{o['name']}」→「{p['name']}」")
            if not parts:
                continue
            msg = f"{p['name']}: " + " / ".join(parts)
        (watched if is_watched(p["name"], watch) else others).append(f"- {msg}")
    for pid, o in old_p.items():
        if pid not in new_p:
            line = f"- 一覧から消えた: {o['name']}"
            (watched if is_watched(o["name"], watch) else others).append(line)
    rank_new = [n for n in new["ranking"] if n not in old.get("ranking", [])]
    return watched, others, rank_new


def snapshot_table(products, watch):
    rows = ["| 機種 | 価格 | 数量 |", "|---|---|---|"]
    for p in sorted(products.values(), key=lambda p: p["name"]):
        if is_watched(p["name"], watch):
            rows.append(f"| [{p['name']}]({p['url']}) | {yen(p['price'])} | {p['qty']} |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        products, ranking = collect(cfg)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    new = {"checked_at": now, "products": products, "ranking": ranking}
    first_run = not STATE.exists()
    old = {} if first_run else json.loads(STATE.read_text(encoding="utf-8"))

    watched, others, rank_new = ([], [], []) if first_run else diff(old, new, cfg["watch"])
    changed = first_run or watched or others or rank_new
    if changed:
        out = [f"確認日時: {now}（JST）", ""]
        if first_run:
            out += ["初回の取得結果です。下の表がサイトの表示と合っているか確認してください。", ""]
        if watched:
            out += ["## 追跡中の機種の変化", *watched, ""]
        if rank_new:
            out += ["## 人気ランキングに新しく入った商品", *[f"- {n}" for n in rank_new], ""]
        if others:
            out += ["## その他の商品の変化", *others, ""]
        out += ["## 追跡中の機種（現在）", snapshot_table(products, cfg["watch"]), "",
                f"一覧から読み取った商品数: {len(products)}"]
        REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(REPORT.read_text(encoding="utf-8"))
    else:
        print(f"{now} 変化なし（{len(products)}商品）")
    if not args.dry_run:
        STATE.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 10 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
