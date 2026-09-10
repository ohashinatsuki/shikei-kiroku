# -*- coding: utf-8 -*-
"""data.json から、日本語版と英語版のページをまとめて作る。

    python scripts/build_site.py

作るもの:
  日本語  index.html        今日と直近21日
          archive.html      全記録（月別）
          japan.html        日本の記録
  English en/index.html     Today and the last 21 days
          en/archive.html   All records by month
          en/japan.html     Executions in Japan
          en/about.html     About / editorial policy
          en/privacy.html   Privacy policy
  共通    sitemap.xml

なぜ静的に作るのか:
  以前は data.json をブラウザ側で読んで組み立てていたが、その形だと
  検索エンジンに記録の中身が見えにくい。ここで書き出しておけば、
  1件ずつがそのままHTMLとして読まれる。
"""
import datetime
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://shikei-kiroku.com"
GA = "G-CS3LBG96H8"
WD_JA = ["月", "火", "水", "木", "金", "土", "日"]
WD_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MON_EN = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
WINDOW = 21          # トップに出す日数
MIN_DATE = "2026-08-15"   # 日々の記録の開始日（これ以前は日本の過去分だけ）


def esc(s):
    return html.escape(str(s or ""), quote=True)


# ---------------- データ ----------------

def load():
    d = json.load(io.open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
    ja = {c["en"]: c["ja"] for c in d["C"]}
    libya = d.get("LIBYA_N", {})
    for e in d["E"]:
        e["_n"] = libya.get(e["d"], 1) if (e["c"] == "Libya" and not e.get("name")) else 1
        e["_jst"], e["_time"] = to_jst(e)
    return d, ja


def to_jst(e):
    """日本時間の日付と時刻に直す。時刻が非公表なら現地の日付をそのまま使う。"""
    if not e.get("t") or e.get("off") is None:
        return e["d"], None
    y, m, dd = (int(x) for x in e["d"].split("-"))
    hh, mm = (int(x) for x in e["t"].split(":"))
    dt = datetime.datetime(y, m, dd, 0, 0) + datetime.timedelta(hours=hh - e["off"] + 9, minutes=mm)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")


def jdate(k, lang):
    y, m, d = (int(x) for x in k.split("-"))
    w = datetime.date(y, m, d).weekday()
    if lang == "ja":
        return "%d年%d月%d日（%s）" % (y, m, d, WD_JA[w])
    return "%s, %d %s %d" % (WD_EN[w], d, MON_EN[m - 1], y)


def jmonth(k, lang):
    y, m = (int(x) for x in k.split("-"))
    return "%d年%d月" % (y, m) if lang == "ja" else "%s %d" % (MON_EN[m - 1], y)


# ---------------- 見た目 ----------------

NAV_JA = [("./", "世界の記録"), ("japan.html", "日本の記録"), ("archive.html", "記録アーカイブ"),
          ("yomimono.html", "読み物"), ("about.html", "編集方針"),
          ("contact.html", "お問い合わせ")]
NAV_EN = [("./", "Today"), ("japan.html", "Japan"), ("archive.html", "Archive"),
          ("about.html", "About"), ("contact.html", "Contact")]


def page(lang, title, desc, path, body, current="", alt=None):
    """path はサイト直下からの相対パス（例 "archive.html" / "en/index.html"）"""
    base = "../" if path.startswith("en/") else ""
    nav = NAV_EN if lang == "en" else NAV_JA
    cur = path.split("/")[-1]
    items = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if
                                   (h == cur or (h == "./" and cur == "index.html") or h == current)
                                   else "", t)
        for h, t in nav)
    switch = ('<a class="lang" href="%sen/">English</a>' % base if lang == "ja"
              else '<a class="lang" href="%s">日本語</a>' % base)
    # index.html は URL に出さない（/ と /en/ に統一。/en/index.html と二重に見られないため）
    cpath = path[:-len("index.html")] if path.endswith("index.html") else path
    canon = "%s/%s" % (SITE, cpath)
    alts = ""
    if alt:
        alts = ('<link rel="alternate" hreflang="ja" href="%s/%s">\n'
                '<link rel="alternate" hreflang="en" href="%s/%s">\n'
                '<link rel="alternate" hreflang="x-default" href="%s/%s">\n'
                % (SITE, alt[0], SITE, alt[1], SITE, alt[0]))
    brand = ("世界死刑執行記録" if lang == "ja" else "World Execution Record")
    sub = ("WORLD EXECUTION RECORD" if lang == "ja" else "SEKAI SHIKEI SHIKKO KIROKU")
    foot = ("掲載するのは出典で確認できた執行のみ。"
            if lang == "ja" else
            "Only executions confirmed by a cited source are listed.")
    return """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
{alts}<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{locale}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{base}style.css">
<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{ga}', {{ anonymize_ip: true }});
</script>
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <div class="brand">{brand}<small>{sub}</small></div>
    <div class="mm">{switch}</div>
  </div>
</header>

<nav class="mainnav">
  <div class="wrap">{items}</div>
</nav>

{body}

<div class="wrap">
<footer>
  <div class="nav">{items2}</div>
  <b>{brand}</b> — {foot}
</footer>
</div>

</body>
</html>
""".format(lang=lang, title=esc(title), desc=esc(desc), canon=canon, alts=alts,
           locale="ja_JP" if lang == "ja" else "en_US", base=base, ga=GA,
           brand=brand, sub=sub, switch=switch, items=items, body=body,
           items2=items + ('<a href="%sprivacy.html">%s</a>'
                           % (base if lang == "en" else "",
                              "プライバシーポリシー" if lang == "ja" else "Privacy")),
           foot=foot)


# ---------------- 記録の描画 ----------------

def person(e, lang):
    ja = lang == "ja"
    if e.get("name"):
        nm = esc(e["name"] if ja else (e.get("name_en") or e["name"])) + ('<small>%s</small>' % (("%d歳" % e["age"]) if ja else ("aged %d" % e["age"]))
                               if e.get("age") else "")
    else:
        nm = ("氏名非公表<small>%d人</small>" % e["_n"] if ja
              else "Name not disclosed<small>%d people</small>" % e["_n"])
    charge = e.get("charge_en") if not ja else e.get("charge")
    method = e.get("method_en") if not ja else e.get("method")
    place = e.get("place_en") if not ja else e.get("place")
    extra = e.get("extra_en") if not ja else e.get("extra")
    sep = '<span class="sep">%s</span>' % ("｜" if ja else "|")
    dt = esc(charge) + sep + '<span class="m">%s</span>' % esc(method)
    if place:
        dt += sep + '<span class="pl">%s</span>' % esc(place)
    meta = ('<span class="t">%s JST</span>' % e["_time"] if e["_time"] else "")
    src = e.get("src_en") if not ja else e.get("src")
    meta += '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(e["url"]), esc(src))
    return ('<div class="p"><div class="nm">%s</div><div class="dt">%s</div>'
            '<div class="meta">%s</div>%s</div>'
            % (nm, dt, meta,
               '<div class="ex">%s</div>' % esc(extra) if extra else ""))


def day_block(entries, lang, ja_names):
    groups = {}
    for e in entries:
        groups.setdefault(e["c"], []).append(e)
    order = sorted(groups, key=lambda c: -sum(x["_n"] for x in groups[c]))
    total, html_ = 0, ""
    for c in order:
        n = sum(x["_n"] for x in groups[c])
        total += n
        label = ja_names.get(c, c) if lang == "ja" else c
        cnt = "%d人" % n if lang == "ja" else ("%d person" % n if n == 1 else "%d people" % n)
        html_ += ('<div class="country"><div class="c-head"><h3>%s</h3>'
                  '<span class="cn">%s</span></div>%s</div>'
                  % (esc(label), cnt, "".join(person(e, lang) for e in groups[c])))
    return html_, total, order, groups


def by_day(E):
    d = {}
    for e in E:
        d.setdefault(e["_jst"], []).append(e)
    return d


# ---------------- 各ページ ----------------

def build_index(d, ja_names, lang, today):
    days = by_day(d["E"])
    tkey = today.isoformat()
    head = ('<div class="date">%s<small>%s</small></div>'
            % ((("%d年%d月%d日" % (today.year, today.month, today.day)) if lang == "ja"
                else "%s %d, %d" % (MON_EN[today.month - 1], today.day, today.year)),
               (WD_JA[today.weekday()] + "曜日") if lang == "ja" else WD_EN[today.weekday()]))
    head += ('<div class="q">今日、世界のどこで、誰が死刑を執行されたか</div>' if lang == "ja"
             else '<div class="q">Who was executed in the world today</div>')
    if tkey in days:
        h, total, order, groups = day_block(days[tkey], lang, ja_names)
        line = (("<b>%d人</b>の執行を確認　" % total) if lang == "ja"
                else ("<b>%d</b> executions confirmed — " % total))
        line += "・".join("%s %d" % (ja_names.get(c, c) if lang == "ja" else c,
                                     sum(x["_n"] for x in groups[c])) for c in order)
        today_html = head + '<div class="ans">%s</div>' % line + h
    else:
        hint = ("各国の発表や人権団体の確認には数時間から数日の遅れがあります。"
                "米国の執行は現地の夕方（日本の翌朝）に行われます。確認でき次第、ここに追加します。"
                if lang == "ja" else
                "Governments and human rights organisations often take hours or days to "
                "confirm an execution. Executions in the United States take place in the "
                "local evening, which is the following morning in Japan. Records are added "
                "as soon as they are confirmed.")
        today_html = (head + '<div class="ans">%s</div><div class="hint">%s</div>'
                      % ("まだ確認されていません" if lang == "ja" else "None confirmed yet", hint))

    out = ""
    cur = today - datetime.timedelta(days=1)
    for _ in range(WINDOW):
        k = cur.isoformat()
        if k in days:
            h, total, _o, _g = day_block(days[k], lang, ja_names)
            out += ('<section class="day" id="d-%s"><div class="day-head"><h2>%s</h2>'
                    '<span class="n">%s</span></div>%s</section>'
                    % (k, jdate(k, lang), ("%d人" % total) if lang == "ja" else str(total), h))
        else:
            out += ('<div class="day empty"><span class="d">%s</span><span class="z">%s</span></div>'
                    % (jdate(k, lang), "なし" if lang == "ja" else "none"))
        cur -= datetime.timedelta(days=1)

    more = ('<p class="more"><a href="archive.html">これより前の記録をすべて見る →</a></p>'
            if lang == "ja" else
            '<p class="more"><a href="archive.html">See all earlier records →</a></p>')
    body = """
<main>
<div class="wrap"><section class="today">{t}</section></div>
<div class="wrap">{days}{more}</div>
</main>
""".format(t=today_html, days=out, more=more)
    title = ("世界死刑執行記録 — 今日、世界のどこで、誰が死刑を執行されたか" if lang == "ja"
             else "World Execution Record — who was executed in the world today")
    desc = ("今日、世界のどこで、誰が死刑を執行されたかを日本時間で毎日記録する資料サイト。"
            "国ごとに氏名・罪状・執行方法を出典つきで掲載しています。" if lang == "ja" else
            "A daily record of who has been executed around the world. Every entry gives the "
            "name, charge, method and place of execution, with a link to the source.")
    p = "index.html" if lang == "ja" else "en/index.html"
    return p, page(lang, title, desc, p, body, alt=("", "en/"))


def build_archive(d, ja_names, lang):
    days = by_day(d["E"])
    months = {}
    for k, v in days.items():
        months.setdefault(k[:7], []).append(k)
    keys = sorted(months, reverse=True)
    nav = "".join('<a href="#m-%s">%s<span>%d</span></a>'
                  % (m, jmonth(m, lang), sum(len(days[k]) for k in months[m])) for m in keys)
    secs = ""
    for m in keys:
        inner = ""
        for k in sorted(months[m], reverse=True):
            h, total, _o, _g = day_block(days[k], lang, ja_names)
            inner += ('<section class="day" id="d-%s"><div class="day-head"><h2>%s</h2>'
                      '<span class="n">%s</span></div>%s</section>'
                      % (k, jdate(k, lang), ("%d人" % total) if lang == "ja" else str(total), h))
        secs += ('<section class="mon" id="m-%s"><h2 class="monh">%s</h2>%s</section>'
                 % (m, jmonth(m, lang), inner))
    lead = ("これまでに記録したすべての執行です。出典で確認できたものだけを載せています。"
            "日付は日本時間です。" if lang == "ja" else
            "Every execution recorded on this site so far. Only records confirmed by a cited "
            "source are listed. Dates are given in Japan Standard Time.")
    body = """
<main class="wrap">
<article>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
  <p class="count">{cnt}</p>
  <div class="gyonav">{nav}</div>
  {secs}
</article>
</main>
""".format(h1="記録アーカイブ" if lang == "ja" else "Archive",
           lead=lead,
           cnt=("全 %d件 ／ %s 〜 %s" % (len(d["E"]), min(days), max(days))) if lang == "ja"
               else ("%d records — %s to %s" % (len(d["E"]), min(days), max(days))),
           nav=nav, secs=secs)
    title = ("記録アーカイブ — 世界死刑執行記録" if lang == "ja"
             else "Archive — World Execution Record")
    desc = ("これまでに記録した世界の死刑執行をすべて月別に並べたページです。"
            if lang == "ja" else
            "All executions recorded on this site, arranged by month, with sources.")
    p = "archive.html" if lang == "ja" else "en/archive.html"
    return p, page(lang, title, desc, p, body, alt=("archive.html", "en/archive.html"))


def build_japan(d, ja_names, lang):
    jp = [e for e in d["E"] if e["c"] == "Japan"]
    days = {}
    for e in jp:
        days.setdefault(e["d"], []).append(e)
    keys = sorted(days, reverse=True)
    secs = ""
    for k in keys:
        secs += ('<section class="day" id="d-%s"><div class="day-head"><h2>%s</h2>'
                 '<span class="n">%s</span></div>%s</section>'
                 % (k, jdate(k, lang),
                    ("%d人" % len(days[k])) if lang == "ja" else str(len(days[k])),
                    "".join(person(e, lang) for e in days[k])))
    if lang == "ja":
        lead = ("日本で死刑が執行された人の記録です。法務大臣が執行のたびに開く臨時記者会見の"
                "発表を出典としています。法務省が氏名を公表するようになったのは2007年12月からで、"
                "このページはそのうち<b>2013年2月以降のすべての執行</b>を収めています。"
                "手続きの流れは <a href=\"japan-tetsuzuki.html\">日本の死刑執行はどう決まり、"
                "どう行われるか</a> で説明しています。")
        note = ("日本の死刑は<b>絞首</b>により、東京・大阪・名古屋・広島・福岡・仙台・札幌の各"
                "拘置所で執行されます。執行は当日の朝に本人へ告知され、事前の予告はありません。"
                "執行後、法務大臣が記者会見を開き、氏名・年齢・執行場所を公表します。<br><br>"
                "<b>年齢や執行場所が空欄の記録は、出典で確認できなかったものです。</b>"
                "推測では埋めていません。")
    else:
        lead = ("A record of people executed in Japan. The source for each entry is the press "
                "conference the Minister of Justice holds on the day of an execution. The Ministry "
                "of Justice began releasing the names of executed prisoners in December 2007; this "
                "page covers <b>every execution carried out since February 2013</b>.")
        note = ("Executions in Japan are carried out by <b>hanging</b>, at the detention houses in "
                "Tokyo, Osaka, Nagoya, Hiroshima, Fukuoka, Sendai and Sapporo. The prisoner is told "
                "on the morning of the execution; there is no advance notice. Afterwards the "
                "Minister of Justice holds a press conference and releases the name, age and place "
                "of execution.<br><br><b>Where the age or place is blank, it could not be confirmed "
                "from the source.</b> Nothing has been filled in by guesswork.")
    body = """
<main class="wrap">
<article>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
  <div class="note">{note}</div>
  <p class="count">{cnt}</p>
  {secs}
</article>
</main>
""".format(h1="日本の死刑執行記録" if lang == "ja" else "Executions in Japan",
           lead=lead, note=note,
           cnt=("記録 %d人 ／ 執行日 %d日 ／ %s 〜 %s" % (len(jp), len(keys), keys[-1], keys[0]))
               if lang == "ja" else
               ("%d people — %d execution dates — %s to %s" % (len(jp), len(keys), keys[-1], keys[0])),
           secs=secs)
    title = ("日本の死刑執行記録 — 世界死刑執行記録" if lang == "ja"
             else "Executions in Japan — World Execution Record")
    desc = ("日本で死刑が執行された人の記録。2013年2月以降のすべての執行を、氏名・事件・執行場所・"
            "法務省の発表を出典として日付順に掲載しています。" if lang == "ja" else
            "A record of people executed in Japan since February 2013, with the name, case, place "
            "of execution and the Ministry of Justice announcement as the source.")
    p = "japan.html" if lang == "ja" else "en/japan.html"
    return p, page(lang, title, desc, p, body, alt=("japan.html", "en/japan.html"))


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(path) else None
    io.open(full, "w", encoding="utf-8", newline="\n").write(text)


def build_sitemap(extra_pages):
    urls = ["", "japan.html", "archive.html", "yomimono.html", "about.html",
            "contact.html", "privacy.html",
            "en/", "en/japan.html", "en/archive.html", "en/about.html",
            "en/contact.html", "en/privacy.html"] + extra_pages
    rows = "".join(
        '  <url><loc>%s/%s</loc><changefreq>%s</changefreq><priority>%s</priority></url>\n'
        % (SITE, u, "daily" if u in ("", "en/") else "weekly", "1.0" if u in ("", "en/") else "0.7")
        for u in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % rows)


JP_CHARS = re.compile(u"[぀-ヿ一-鿿！-～]")


def check_en_pages():
    """英語ページに日本語が1文字も残っていないか確認する。残っていれば止める。
    言語切り替えリンクの「日本語」だけは意図した表示なので除外する。"""
    bad = []
    for fn in sorted(os.listdir(os.path.join(ROOT, "en"))):
        if not fn.endswith(".html"):
            continue
        text = io.open(os.path.join(ROOT, "en", fn), encoding="utf-8").read()
        text = text.replace('>日本語</a>', '></a>')
        for i, line in enumerate(text.split("\n"), 1):
            for m in JP_CHARS.finditer(line):
                bad.append("en/%s %d行目: …%s…" % (fn, i, line[max(0, m.start() - 20):m.start() + 20]))
                break
    if bad:
        sys.exit("英語ページに日本語が残っています:\n  " + "\n  ".join(bad))


def main():
    d, ja_names = load()
    missing = [e for e in d["E"] if e.get("charge_en") is None]
    if missing:
        sys.exit("英語データが入っていない記録が %d件あります。先に scripts/add_en.py を実行してください。"
                 % len(missing))
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    today = today.date()
    for lang in ("ja", "en"):
        for fn in (build_index, build_archive, build_japan):
            if fn is build_index:
                p, t = fn(d, ja_names, lang, today)
            else:
                p, t = fn(d, ja_names, lang)
            write(p, t)
            print("  " + p)
    yomi = ["kiroku-no-yomikata.html", "sekai-no-ima.html", "iran.html", "saudi.html",
            "usa.html", "japan-tetsuzuki.html", "mayaku.html", "enzai.html", "yougo.html",
            "miseinen.html", "josei.html", "haishi.html", "kokuren.html",
            "saishin-muzai.html", "usa-jinshu.html", "lynch.html", "muzai-shikko.html"]
    build_sitemap(yomi)
    print("  sitemap.xml")
    check_en_pages()
    print("  英語ページに日本語なし: OK")
    print("生成完了: 記録 %d件 / 日本時間 %s 時点" % (len(d["E"]), today))


main()
