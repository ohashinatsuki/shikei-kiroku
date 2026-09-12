# -*- coding: utf-8 -*-
r"""消防庁の災害情報から、災害ごとの死者・行方不明者を取り込む。

    python scripts/fetch_saigai.py 2026          その年の一覧を見て、被害報を読む
    python scripts/fetch_saigai.py 2026 --all    死者0の災害も含めて表示（確認用）

取り込んだものは shi.json の `saigai` に入る。

消防庁は災害（地震・台風・豪雨・大雪・林野火災など）ごとに「被害報」を出す。
第1報、第2報…と更新され、最後の報が確定に近い。
被害報には都道府県別・市町村別の死者数が書かれている。名前は書かれない。

**死者と行方不明者だけを取る。負傷者は取らない。**
数字は「速報であり今後も変わることがある」と但し書きがあるので、
何報の時点の数字かを必ず持っておく。
"""
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHI = os.path.join(ROOT, "shi.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; shikei-kiroku/1.0)"}
LIST = "https://www.fdma.go.jp/disaster/info/%s/"

# 林野火災・船舶火災など、死者が出ないことが多いものも一覧には並ぶ。
# 死者0なら載せないので、ここでは弾かない。


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    raw = urllib.request.urlopen(req, timeout=60).read()
    return raw if binary else raw.decode("utf-8", "replace")


def pdf_text(url):
    import pypdf
    r = pypdf.PdfReader(io.BytesIO(get(url, binary=True)))
    return "\n".join((p.extract_text() or "") for p in r.pages)


def z2h(s):
    """全角の数字を半角に"""
    return s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def list_disasters(year):
    """その年の災害の一覧。(日付, 名前, 何報か, 被害報のURL) を返す。

    一覧のHTMLはこの形:
      <li><a href="/disaster/info/items/xxx.pdf" ...>令和8年07月28日 令和８年熊本地震による
      被害及び消防機関等の対応状況（第64報・R8.9.9更新）<img ...></a></li>
    """
    html = get(LIST % year)
    out = []
    for m in re.finditer(
            r'<a\s+href="(/disaster/info/items/[^"]+\.pdf)"[^>]*>(.*?)</a>',
            html, re.S):
        href, label = m.groups()
        text = re.sub(r"<[^>]+>", "", label)
        text = text.replace("　", " ")
        text = re.sub(r"[\s]+", " ", text).strip()
        if not text:
            continue
        md = re.match(r"(令和\d+年\d+月\d+日|\d{4}年\d+月\d+日)\s*(.*)$", text)
        if md:
            date, name = md.group(1), md.group(2).strip()
        else:
            date, name = "", text
        hou = None
        mh = re.search(r"第\s*([0-9０-９]{1,3})\s*報", name)
        if mh:
            hou = int(z2h(mh.group(1)))
        # 「（第64報・R8.9.9更新）」や「による被害及び消防機関等の対応状況」を落として短くする
        name = re.sub(r"（[^（）]*報[^（）]*）\s*$", "", name).strip()
        name = re.sub(r"による被害及び消防機関等の対応状況$", "", name).strip()
        name = re.sub(r"の被害及び消防機関等の対応状況$", "", name).strip()
        out.append((date, name, hou, "https://www.fdma.go.jp" + href))

    seen, uniq = set(), []
    for row in out:
        if row[3] in seen:
            continue
        seen.add(row[3])
        uniq.append(row)
    return uniq


RE_HOU = re.compile(r"第\s*([0-9０-９]{1,3})\s*報")
RE_ASOF = re.compile(r"(令和\s*[0-9０-９]+\s*年\s*[0-9０-９]+\s*月\s*[0-9０-９]+\s*日)")
RE_UCHI = re.compile(
    r"≪死者の内訳≫(.{0,800}?)(?:⑵|[２3３]\s*[　 ]*(?:避難|消防|被害|都道府県)|$)", re.S)
# 内訳の中の「八代市２０人」「宇城市３人」
RE_CITY = re.compile(r"([一-龥ぁ-んァ-ヶ]{1,12}?[市区町村])\s*([0-9０-９]{1,4})\s*人")
# 「行方不明者◯人」と文章で書かれることがある
RE_MISS = re.compile(r"行方不明者?[^0-9０-９]{0,8}([0-9０-９]{1,5})\s*[人名]")


def read_report(url):
    """被害報PDFから、死者・行方不明・内訳・何報かを取り出す。

    注意: 人的被害は「表」で書かれており、PDFから文字にすると数字だけが並ぶ。
    「死者◯人」という文は無い。だから表からは読まず、
    **≪死者の内訳≫ に書かれた市区町村ごとの人数を合計する。**
    内訳が無い災害は、死者が確認できないものとして飛ばす（推測しない）。
    """
    t = pdf_text(url)

    hou = None
    m = RE_HOU.search(re.sub(r"[\s　]+", "", t))
    if m:
        hou = int(z2h(m.group(1)))

    asof = None
    m = RE_ASOF.search(t)
    if m:
        asof = re.sub(r"[\s　]+", "", m.group(1))

    dead = None
    detail = ""
    breakdown = []
    m = RE_UCHI.search(t)
    if m:
        detail = re.sub(r"[\s　]+", "", m.group(1))
        for c in RE_CITY.finditer(detail):
            breakdown.append({"place": c.group(1), "n": int(z2h(c.group(2)))})
        if breakdown:
            dead = sum(b["n"] for b in breakdown)
        detail = detail.replace("【", " 【").strip()

    miss = None
    m = RE_MISS.search(re.sub(r"[\s　]+", "", t))
    if m:
        v = int(z2h(m.group(1)))
        if v < 10000:
            miss = v

    return {"dead": dead, "missing": miss, "report": hou, "asof": asof,
            "detail": detail, "breakdown": breakdown, "url": url}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    year = args[0]

    d = json.load(io.open(SHI, encoding="utf-8")) if os.path.exists(SHI) else {}
    d.setdefault("saigai", {})

    rows = list_disasters(year)
    print("%s年の災害 %d件" % (year, len(rows)))
    got = 0
    for date, name, hou, url in rows:
        try:
            r = read_report(url)
        except Exception as e:
            print("  FAILED %s %s" % (name, type(e).__name__))
            continue
        dead = r["dead"] or 0
        miss = r["missing"] or 0
        if not show_all and dead == 0 and miss == 0:
            continue
        key = "%s|%s" % (date, name)
        r["date"] = date
        r["name"] = name
        if hou:
            r["report"] = hou
        d["saigai"][key] = r
        got += 1
        print("  %s %s … 死者%s 不明%s（第%s報 %s）"
              % (date, name[:26], dead, miss, r["report"], r["asof"] or ""))

    io.open(SHI, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))
    print("\n死者・行方不明者が出た災害 %d件 → shi.json" % got)


if __name__ == "__main__":
    main()
