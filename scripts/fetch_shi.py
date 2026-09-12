# -*- coding: utf-8 -*-
r"""「日本の死」の数字を、役所の公表から取り込む。

    python scripts/fetch_shi.py traffic            交通事故の日報（前日分）を取り込む
    python scripts/fetch_shi.py traffic 2026-09-01 日付を指定して取り込む
    python scripts/fetch_shi.py traffic --back 30  過去30日ぶんをさかのぼって取り込む

取り込んだものは shi.json に入る。年次の数字（自殺・山岳・火災など）は
更新が年に1〜2回なので、`毎日の更新手順.md` の指示に従って手で入れる。

**載せるのは、死が確定したものだけ。**
けが人・救急搬送された人の数は入れない。行方不明者は死者と分けて持つ。
"""
import datetime
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHI = os.path.join(ROOT, "shi.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; shikei-kiroku/1.0)"}

# 交通事故死者日報。日付を入れ替えれば過去も取れる
ITARDA = "https://www.itarda.or.jp/report/%s"

# 日報の県名表記をそろえる（「札 幌」→「札幌」など全角空白を抜く）
def tidy(s):
    return re.sub(r"[\s　]+", "", s or "")


def num(s):
    """「-」「－」「…」「空」は 0 か None。数字なら int"""
    s = tidy(s)
    if s in ("", "-", "－", "…", "‥"):
        return None
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None


def load():
    if os.path.exists(SHI):
        return json.load(io.open(SHI, encoding="utf-8"))
    return {"traffic": {}, "yearly": {}}


def save(d):
    io.open(SHI, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))


# ---------------- 交通事故の日報 ----------------

def fetch_traffic(day):
    """day は 'YYYY-MM-DD'。全国合計と、都道府県別を返す。

    日報の表は列の位置が決まっている（14列。地方名が入る行だけ15列）。
        0 名前
        1 当日 本年 / 2 当日 前年
        3 月計 本年 / 4 月計 前年 / 5 増減数 / 6 増減率
        7 累計 本年 / 8 順位 / 9 累計 前年 / 10 増減数 / 11 順位 / 12 増減率 / 13 順位
    北海道は方面本部（札幌・函館・旭川・釧路・北見）に分かれ、「北海道計」で合算される。
    地方の「◯◯計」の行は、都道府県ではないので分けて持つ。
    """
    url = ITARDA % day
    req = urllib.request.Request(url, headers=UA)
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        tds = [tidy(re.sub(r"<[^>]+>", "", td))
               for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if tds:
            rows.append(tds)
    if not rows:
        raise RuntimeError("表が読み取れません: " + url)

    out = {"url": url, "pref": {}, "region": {},
           "total": None, "total_cum": None, "total_prev_cum": None}

    for tds in rows:
        # 15列の行は先頭が地方名。落として14列にそろえる
        if len(tds) == 15:
            cells = tds[1:]
        elif len(tds) == 14:
            cells = tds
        else:
            continue

        name = cells[0]
        if name in ("都道府県", "当日", "本年", "前年"):
            continue

        rec = {"day": num(cells[1]) or 0,
               "cum": num(cells[7]),
               "prev_cum": num(cells[9])}

        if name in ("合計", "全国", "総計"):
            out["total"] = rec["day"]
            out["total_cum"] = rec["cum"]
            out["total_prev_cum"] = rec["prev_cum"]
        elif name.endswith("計"):
            out["region"][name] = rec
        else:
            out["pref"][name] = rec

    return out


def run_traffic(days):
    d = load()
    got = 0
    for day in days:
        if day in d["traffic"]:
            print("skip", day)
            continue
        try:
            r = fetch_traffic(day)
        except Exception as e:
            print("FAILED", day, type(e).__name__, str(e)[:120])
            continue
        if r["total"] is None and not r["pref"]:
            print("中身なし", day)
            continue
        d["traffic"][day] = r
        got += 1
        print("%s  当日 %s人 ／ 累計 %s人 ／ 都道府県 %d件"
              % (day, r["total"], r["total_cum"], len(r["pref"])))
    save(d)
    print("\n%d日ぶん取り込みました → shi.json" % got)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    what = args[0]
    if what != "traffic":
        print("いまは traffic だけ対応しています。", file=sys.stderr)
        sys.exit(2)

    rest = args[1:]
    back = 1
    if "--back" in rest:
        i = rest.index("--back")
        back = int(rest[i + 1])
        rest = rest[:i] + rest[i + 2:]

    if rest:
        days = rest
    else:
        today = datetime.date.today()
        days = [(today - datetime.timedelta(days=i + 1)).isoformat()
                for i in range(back)]
        days.reverse()
    run_traffic(days)


if __name__ == "__main__":
    main()
