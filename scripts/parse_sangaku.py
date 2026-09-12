# -*- coding: utf-8 -*-
r"""長野県警の「山岳遭難週報」PDFから、亡くなった方・行方不明の方の記録を取り出す。

    python scripts/parse_sangaku.py <週報のURL または PDFファイルのパス> [--all]

    --all を付けると、負傷・無事救出も含めて全件を表示する（確認用）。
    付けなければ 死亡 と 行方不明 だけを取り出す。これがサイトに載せる分。

出すもの: shibou.json に入れられる形の JSON を画面に表示する。
         追記は scripts/add_shibou.py が行う。

週報の表は次の並びになっている:
    日付 場所 性別 年齢 死傷別 態様 概要

名前は書かれていない。年代・性別・場所・態様・状況の文章だけ。
このサイトは「役所が名前を伏せて公表している死」だけを扱うので、この形がちょうどよい。
"""
import io
import json
import os
import re
import sys
import urllib.request

# 死傷別のうち、サイトに載せるもの
LOAD = ("死亡", "死者", "行方不明")

RESULTS = ("死亡", "死者", "行方不明", "負傷", "無事救出", "無事")

# 「9月6日」のような日付で行が始まる
RE_HEAD = re.compile(r"^(\d{1,2})月(\d{1,2})日\s*(.*)$")
# 「男 78 行方不明 不明 …」のように 性別・年齢・死傷別・態様 が並ぶ
RE_BODY = re.compile(r"(男|女)\s*(\d{1,3})\s*(" + "|".join(RESULTS) + r")\s*(\S+)\s*(.*)$")


def read_pdf(src):
    """URL でもローカルのパスでも受ける"""
    import pypdf
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=60).read()
        fh = io.BytesIO(raw)
    else:
        fh = io.open(src, "rb")
    r = pypdf.PdfReader(fh)
    return "\n".join((p.extract_text() or "") for p in r.pages)


def year_from(text, src):
    """令和8年 → 2026。見つからなければファイル名の先頭2桁から推測する"""
    # 統計表には前年（令和7年）の比較列があるので、出てくる中で一番新しい年を取る
    ys = [int(x) for x in re.findall(r"令和\s*(\d+)\s*年", text)]
    if ys:
        return 2018 + max(ys)
    m = re.search(r"/(\d{2})\d{4}-", src)
    if m:
        return 2018 + int(m.group(1))
    return None


def parse(text, year):
    """週報の本文から1件ずつ取り出す。
    表の行はPDFの都合で複数行に折り返されるので、日付で始まる行から次の日付までを1件とみなす。"""
    lines = [l.rstrip() for l in text.split("\n")]

    # 「先週の発生」の表が始まるあたりから、注意書きが始まる前までを見る
    start = 0
    for i, l in enumerate(lines):
        if "日付" in l and "場所" in l and "概要" in l:
            start = i + 1
            break
    end = len(lines)
    for i in range(start, len(lines)):
        if "先週の発生" in lines[i] or "アドバイス" in lines[i]:
            end = i
            break

    chunks = []
    cur = None
    for l in lines[start:end]:
        if not l.strip():
            continue
        m = RE_HEAD.match(l.strip())
        if m:
            if cur:
                chunks.append(cur)
            cur = {"mm": int(m.group(1)), "dd": int(m.group(2)), "rest": [m.group(3)]}
        elif cur:
            cur["rest"].append(l.strip())
    if cur:
        chunks.append(cur)

    out = []
    for c in chunks:
        blob = " ".join(x for x in c["rest"] if x)
        blob = re.sub(r"\s+", " ", blob).strip()
        m = RE_BODY.search(blob)
        if not m:
            continue
        place = blob[:m.start()].strip()
        sex, age, result, kind, desc = m.groups()
        desc = re.sub(r"\s+", "", desc).strip()
        place = re.sub(r"\s+", " ", place).strip()
        out.append({
            "kind": "山岳",
            "d": "%04d-%02d-%02d" % (year, c["mm"], c["dd"]),
            "pref": "長野県",
            "place": place,
            "sex": sex,
            "age": int(age),
            "result": "死亡" if result in ("死亡", "死者") else result,
            "type": kind,
            "desc": desc,
            "src": "長野県警察 山岳遭難週報",
            "url": "",
        })
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    src = args[0]
    text = read_pdf(src)
    year = year_from(text, src)
    if not year:
        print("年が読み取れませんでした。週報の年を確認してください。", file=sys.stderr)
        sys.exit(1)
    rows = parse(text, year)
    for r in rows:
        if src.startswith("http"):
            r["url"] = src
    if not show_all:
        rows = [r for r in rows if r["result"] in LOAD]
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print("\n-- %d件 --" % len(rows), file=sys.stderr)


if __name__ == "__main__":
    main()
