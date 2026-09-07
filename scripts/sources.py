"""一次ソースの取得と、前回から増えた分の抽出。

モデルは使わない。ここはすべてプログラムで処理する。
モデルに渡すのは、ここで見つけた「新着分だけ」。
"""
import html
import json
import os
import re
import time

import requests

UA = {"User-Agent": "Mozilla/5.0 (compatible; shikei-kiroku/1.0; +https://ohashinatsuki.github.io/shikei-kiroku/)"}
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "state", "seen.json")

# この日より前の執行は扱わない（サイトの記録開始日）
MIN_DATE = "2026-08-15"


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            s = json.load(f)
    except (OSError, ValueError):
        s = {}
    s.setdefault("hengaw_urls", [])
    s.setdefault("dpic_rows", [])
    return s


def save_state(state):
    # 無制限に増えないように、直近ぶんだけ残す
    state["hengaw_urls"] = state["hengaw_urls"][-400:]
    state["dpic_rows"] = state["dpic_rows"][-400:]
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=45)
            if r.status_code == 200:
                r.encoding = r.apparent_encoding or "utf-8"
                return r.text
            last = "HTTP %s" % r.status_code
        except requests.RequestException as e:
            last = str(e)
        time.sleep(2 * (i + 1))
    print("  取得失敗 %s (%s)" % (url, last))
    return None


def to_text(markup):
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", markup)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|br)\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t ]+", " ", s)
    s = re.sub(r"\n[ \n]*\n+", "\n", s)
    return s.strip()


# ---------------- Hengaw（イラン） ----------------

HENGAW_INDEX = "https://hengaw.net/en/news"
HENGAW_LINK = re.compile(r"/en/news/\d{4}/\d{2}/[A-Za-z0-9\-]+")


def hengaw_new_articles(seen_urls, limit=25):
    """一覧ページから記事URLを集め、未読のものだけ本文を取ってくる。"""
    index = get(HENGAW_INDEX)
    if not index:
        return []
    urls = []
    for path in HENGAW_LINK.findall(index):
        u = "https://hengaw.net" + path
        if u not in urls:
            urls.append(u)
    fresh = [u for u in urls if u not in seen_urls][:limit]
    print("Hengaw: 一覧 %d件 / 未読 %d件" % (len(urls), len(fresh)))

    out = []
    for u in fresh:
        page = get(u)
        if not page:
            continue
        body = to_text(page)
        # 執行と関係ない記事はここで捨てる（モデルに渡す量を減らす）
        if not re.search(r"(?i)\b(execut|hanged|hanging|death sentence carried out)", body):
            print("  除外（執行の記事ではない） %s" % u)
            continue
        out.append({"url": u, "text": body[:6000]})
        time.sleep(1)
    print("Hengaw: モデルに渡す %d件" % len(out))
    return out


# ---------------- DPIC（米国） ----------------

DPIC_URL = "https://deathpenaltyinfo.org/executions/2026"
# 例: 9 / 1 / 2026 1678 FL Harold Gene Lucas 74 White 1 White Female Lethal Injection ...
DPIC_ROW = re.compile(
    r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(20\d{2})\s+\d{3,5}\s+([A-Z]{2})\s+"
    r"([A-Z][A-Za-z'\-\.]+(?:\s+[A-Z][A-Za-z'\-\.]+){0,4})\s+(\d{2})\s"
)


def dpic_new_rows(seen_rows, known_names=()):
    page = get(DPIC_URL)
    if not page:
        return []
    text = to_text(page).replace("​", "").replace("⁠", "")
    text = text.replace("‑", "-").replace("­", "")
    rows = []
    for mo, dy, yr, st, name, age in DPIC_ROW.findall(text):
        d = "%s-%02d-%02d" % (yr, int(mo), int(dy))
        key = "%s|%s|%s" % (d, st, " ".join(name.split()))
        rows.append({"key": key, "d": d, "state": st, "name": " ".join(name.split()), "age": int(age)})
    fresh = [
        r
        for r in rows
        if r["key"] not in seen_rows and r["d"] >= MIN_DATE and r["name"] not in known_names
    ]
    print("DPIC: 表 %d件 / 記録すべき未登録 %d件" % (len(rows), len(fresh)))
    return fresh
