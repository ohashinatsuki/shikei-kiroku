# -*- coding: utf-8 -*-
r"""shi.json から「日本の死」のページを作る。

    python scripts/build_shi.py

作るもの: shi.html（日本語のみ）

考え方:
  死因ごとに更新の速さも桁もばらばらなので、そのまま並べても読めない。
  すべてを「一日あたり何人」に直すと、初めて比べられる。
  毎日の実数が出るのは交通事故だけなので、そこを「今日」として大きく出す。

守ること:
  ・死が確定したものだけ。けが人・救急搬送された人の数は載せない
  ・すべての数字に「いつ時点の、どの定義か」を書く
  ・一日あたりの人数は計算値であることを明記する
"""
import datetime
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://shikei-kiroku.com"
GA = "G-CS3LBG96H8"
WD = ["月", "火", "水", "木", "金", "土", "日"]


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def n(x):
    return "{:,}".format(x) if isinstance(x, int) else "—"


def load():
    p = os.path.join(ROOT, "shi.json")
    if not os.path.exists(p):
        print("shi.json がありません。先に fetch_shi.py を走らせてください。", file=sys.stderr)
        sys.exit(1)
    return json.load(io.open(p, encoding="utf-8"))


def jdate(k):
    y, m, d = (int(x) for x in k.split("-"))
    t = datetime.date(y, m, d)
    return "%d年%d月%d日（%s）" % (y, m, d, WD[t.weekday()])


# ---------------- 今日 ----------------

def block_today(traffic):
    if not traffic:
        return ""
    k = max(traffic)
    t = traffic[k]
    prev = t.get("total_prev_cum")
    cmp_txt = ""
    if isinstance(t.get("total_cum"), int) and isinstance(prev, int):
        diff = t["total_cum"] - prev
        w = "多い" if diff > 0 else ("少ない" if diff < 0 else "同じ")
        cmp_txt = ("1月1日からの累計 <b>%s人</b>。前年同期は %s人で、%s人%s。"
                   % (n(t["total_cum"]), n(prev), n(abs(diff)), w)) if diff else \
                  ("1月1日からの累計 <b>%s人</b>。前年同期と同じです。" % n(t["total_cum"]))
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>いちばん新しい日</h2></div>
  <p class="lede">毎日の実数が出るのは交通事故だけです。ほかは月ごと・年ごとに更新されます。</p>
  <div class="today">
    <div class="d">%s</div>
    <div class="n">%s<small>人</small></div>
    <div class="k">交通事故で亡くなった方（全国）</div>
    <div class="def">
      事故から<b>24時間以内</b>に亡くなった方の数です。30日以内で数えると、これより多くなります。<br>
      %s
    </div>
  </div>
</div></section>
""" % (jdate(k), n(t.get("total")), cmp_txt)


# ---------------- 一日あたり ----------------

def block_perday(yearly):
    rows = sorted(yearly.get("causes", []), key=lambda c: -c["n"])
    if not rows:
        return ""
    top = rows[0]["n"] / 365.0
    out = []
    for c in rows:
        per = c["n"] / 365.0
        w = max(per / top * 100.0, 0.15)
        big = " big" if per < 100 else ""
        per_s = ("%.1f" % per) if per < 100 else n(int(round(per)))
        out.append(
            '<div class="row%s"><div class="nm">%s<em>%s %s人</em></div>'
            '<div class="v">%s<span>人</span></div>'
            '<div class="bar"><i style="width:%.3f%%"></i></div></div>'
            % (big, esc(c["name"]), esc(c["year"]), n(c["n"]), per_s, w))
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>一日あたり、何人</h2></div>
  <p class="lede">
    更新の速さも桁もばらばらなので、すべて「一日あたり」に直しました。こうすると比べられます。
    年間の公表値を365で割った<b>計算値</b>で、公表値そのものではありません。
  </p>
  <div class="rows">%s</div>
  <p class="lede" style="margin:26px 0 0">
    いちばん多いものを100として棒を引いています。上のいくつかと下のいくつかでは、桁が二つ違います。
    毎日ニュースになる死と、ならない死の差がこれです。
  </p>
</div></section>
""" % "".join(out)


# ---------------- 数字の奥にあるもの ----------------

def block_facts(yearly):
    """年次の資料に書かれている内訳。原典のPDFから直接読んだものだけを載せる。"""
    gs = yearly.get("facts", [])
    if not gs:
        return ""
    out = []
    for g in gs:
        tr = "".join(
            '<tr><td>%s</td><td class="n b">%s</td><td class="sub">%s</td></tr>'
            % (esc(a), esc(b), esc(c)) for a, b, c in g["rows"])
        out.append(
            '<div class="fact"><h3>%s<em>%s</em></h3>'
            '<div class="tblwrap"><table><tbody>%s</tbody></table></div>'
            '<p class="fsrc">%s</p></div>'
            % (esc(g["g"]), esc(g["year"]), tr, esc(g["src"])))
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>数字の奥にあるもの</h2></div>
  <p class="lede">
    役所の資料には、合計のほかに内訳が書かれています。そこだけを抜き出しました。
    書かれていないことは足していません。
  </p>
  %s
</div></section>
""" % "".join(out)


# ---------------- 都道府県 ----------------

ORDER = ["札幌", "函館", "旭川", "釧路", "北見",
         "青森", "岩手", "宮城", "秋田", "山形", "福島",
         "茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川", "新潟",
         "山梨", "長野", "静岡", "富山", "石川", "福井", "岐阜", "愛知", "三重",
         "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山",
         "鳥取", "島根", "岡山", "広島", "山口",
         "徳島", "香川", "愛媛", "高知",
         "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]


def block_pref(traffic):
    if not traffic:
        return ""
    k = max(traffic)
    t = traffic[k]
    pref = t.get("pref", {})
    if not pref:
        return ""
    names = [p for p in ORDER if p in pref] + \
            [p for p in sorted(pref) if p not in ORDER]
    tr = []
    for p in names:
        v = pref[p]
        day = v.get("day") or 0
        cum, prv = v.get("cum"), v.get("prev_cum")
        d_cls = "n hit" if day else "n z"
        diff = ""
        if isinstance(cum, int) and isinstance(prv, int):
            g = cum - prv
            diff = ('<span class="up">+%d</span>' % g if g > 0 else
                    ('<span class="dn">%d</span>' % g if g < 0 else "±0"))
        tr.append('<tr><td>%s</td><td class="%s">%s</td><td class="n">%s</td>'
                  '<td class="n sub">%s</td><td class="n sub">%s</td></tr>'
                  % (esc(p), d_cls, day if day else "—", n(cum), n(prv), diff))
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>都道府県別</h2></div>
  <p class="lede">交通事故で亡くなった方。%s の当日と、1月1日からの累計。
  北海道は方面本部ごとに分かれています。</p>
  <div class="tblwrap"><table>
    <thead><tr><th>都道府県</th><th class="r">当日</th><th class="r">今年</th>
      <th class="r">前年</th><th class="r">差</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
</div></section>
""" % (jdate(k), "".join(tr))


# ---------------- 推移 ----------------

def block_trend(traffic):
    days = sorted(traffic)[-30:]
    if len(days) < 5:
        return ""
    vals = [(d, traffic[d].get("total") or 0) for d in days]
    top = max(v for _, v in vals) or 1
    bars = "".join(
        '<div class="c"><i style="height:%.1f%%"></i><span>%s</span></div>'
        % (v / top * 100.0, d[8:10].lstrip("0"))
        for d, v in vals)
    tot = sum(v for _, v in vals)
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>この30日</h2></div>
  <p class="lede">交通事故で亡くなった方の、日ごとの人数。%s から %s まで。合計 %s人。</p>
  <div class="trend">%s</div>
</div></section>
""" % (jdate(days[0]), jdate(days[-1]), n(tot), bars)


# ---------------- 災害 ----------------

def block_saigai(saigai):
    """災害ごとの死者。消防庁の被害報から。日付の新しい順。"""
    if not saigai:
        return ""
    rows = sorted(saigai.values(), key=lambda r: r.get("date", ""), reverse=True)
    out = []
    for r in rows:
        dead = r.get("dead") or 0
        miss = r.get("missing") or 0
        if not dead and not miss:
            continue
        nums = '<b>%s</b>人' % n(dead) if dead else ""
        if miss:
            nums += ('　行方不明 %s人' % n(miss)) if nums else ('行方不明 <b>%s</b>人' % n(miss))
        bd = ""
        if r.get("breakdown"):
            bd = '<div class="bd">%s</div>' % "　".join(
                "%s %s人" % (esc(b["place"]), n(b["n"])) for b in r["breakdown"])
        meta = "第%s報" % r["report"] if r.get("report") else ""
        if r.get("asof"):
            meta += "（%s 時点）" % esc(r["asof"])
        if r.get("manual"):
            meta += "　被害報を読んで手で入力"
        out.append(
            '<div class="sg">'
            '<div class="sg-h"><div class="sg-n">%s</div><div class="sg-v">%s</div></div>'
            '<div class="sg-d">%s</div>%s'
            '<div class="sg-m">%s <a href="%s" target="_blank" rel="noopener">被害報</a></div>'
            '</div>'
            % (esc(r.get("name", "")), nums, esc(r.get("date", "")), bd,
               meta, esc(r.get("url", ""))))
    if not out:
        return ""
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>災害ごとの死</h2></div>
  <p class="lede">
    地震・台風・豪雨・大雪などで亡くなった方。消防庁が災害ごとに出す被害報から取りました。
    数字は速報で、あとから変わります。<b>何報の時点のものか</b>を各行に書いてあります。
    市区町村ごとの内訳は、被害報に書かれているものをそのまま載せています。
    古い災害は被害報の書式が違い、自動で読み取れないものがあります。
    その分は被害報を開いて手で入力しました。各行に印をつけてあります。
    読み取れなかったものは載せていません。推測では埋めません。
  </p>
  <div class="sgs">%s</div>
</div></section>
""" % "".join(out)


# ---------------- 載っていないもの ----------------

def block_gaps():
    """何を載せていないか、なぜ載せないかを書く。
    これを書かないと、読者はこのページを『日本の死の全部』だと思ってしまう。"""
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>このページに載っていないもの</h2></div>
  <p class="lede">
    このページは、日本の死の全部ではありません。載せていないものと、その理由を書いておきます。
  </p>
  <div class="gaps">
    <div class="gap">
      <h3>一人ひとりの記録</h3>
      <p>いつ、どこで、どんな人が、どう亡くなったか。それを全国分・一件ずつ集めた資料は、
      日本の役所にありません。労働災害の事例集は2018年で止まっており、
      一件ずつの山岳遭難を毎週出しているのは長野県警だけです。
      新聞から集めれば全国そろいますが、名前が入り、記事が消えると出典も消えます。
      このサイトは役所の公表だけを使うと決めているので、載せません。</p>
    </div>
    <div class="gap">
      <h3>けがをした方、運ばれた方</h3>
      <p>死が確定したものだけを載せます。負傷者数や、熱中症で救急車に運ばれた方の数は、
      死者数ではないので載せません。</p>
    </div>
    <div class="gap">
      <h3>殺人</h3>
      <p>逮捕された段階の事件は載せません。不起訴や無罪になることがあり、
      そのとき記録だけが残ってしまうためです。役所が出しているのは月ごとの件数で、
      一件ずつの内訳ではありません。</p>
    </div>
    <div class="gap">
      <h3>時点のそろっていない数字</h3>
      <p>公表の時期が死因ごとに違うため、この表の年はそろっていません。
      交通事故と自殺は2025年、火災は2023年です。年をまたいで足し算はできません。
      各行に年を書いてあります。</p>
    </div>
  </div>
</div></section>
"""


# ---------------- 出典 ----------------

def block_src(yearly, traffic):
    li = []
    if traffic:
        k = max(traffic)
        li.append('交通事故（日ごと・都道府県別）— 交通事故総合分析センター／'
                  '警察庁交通企画課まとめ <a href="%s" target="_blank" rel="noopener">'
                  '交通事故死者日報</a>（%s 分）' % (esc(traffic[k]["url"]), esc(k)))
    for s in yearly.get("sources", []):
        u = (' <a href="%s" target="_blank" rel="noopener">%s</a>'
             % (esc(s["url"]), esc(s.get("site", "出典"))) if s.get("url") else "")
        li.append("%s — %s%s" % (esc(s["name"]), esc(s["note"]), u))
    return """
<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>出典</h2></div>
  <p class="lede">このページは、役所が公表した数字だけを載せます。時点と定義を必ず書きます。</p>
  <ul class="src">%s</ul>
</div></section>
""" % "".join("<li>%s</li>" % x for x in li)


# ---------------- 組み立て ----------------

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>日本の死｜世界死刑執行記録</title>
<meta name="description" content="日本で、どんな死が、一日あたり何人あるか。交通事故・自殺・火災・山岳遭難・水難など、役所が公表した数字だけを、出典と時点を明記してまとめています。">
<link rel="canonical" href="{site}/shi.html">
<meta property="og:title" content="日本の死｜世界死刑執行記録">
<meta property="og:type" content="website">
<meta property="og:locale" content="ja_JP">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="style.css">
<style>
.today{{background:var(--surface); border:1px solid var(--rule); border-top:3px solid var(--executed);
  border-radius:3px; padding:26px; max-width:560px}}
.today .d{{font-family:var(--mono); font-size:12px; color:var(--muted); letter-spacing:.08em}}
.today .n{{font-family:var(--serif); font-size:clamp(40px,11vw,68px); font-weight:700;
  line-height:1.05; color:var(--executed); font-variant-numeric:tabular-nums}}
.today .n small{{font-family:var(--sans); font-size:18px; font-weight:500; color:var(--ink); margin-left:6px}}
.today .k{{font-size:15px; margin-top:4px}}
.today .def{{font-size:12.5px; color:var(--muted); margin-top:14px; padding-top:12px;
  border-top:1px solid var(--rule); line-height:1.9}}
.lede{{color:var(--muted); font-size:13px; margin:0 0 24px; max-width:640px; line-height:1.9}}
.rows{{display:flex; flex-direction:column; gap:2px; max-width:640px}}
.row{{display:grid; grid-template-columns:1fr auto; gap:10px; align-items:baseline;
  padding:11px 0; border-bottom:1px solid var(--rule)}}
.row .nm{{font-size:14.5px}}
.row .nm em{{font-style:normal; color:var(--muted); font-size:11.5px; display:block; margin-top:2px}}
.row .v{{font-family:var(--mono); font-size:16px; font-weight:600;
  font-variant-numeric:tabular-nums; white-space:nowrap}}
.row .v span{{font-family:var(--sans); font-size:11px; font-weight:400; color:var(--muted); margin-left:3px}}
.bar{{grid-column:1/-1; height:4px; background:var(--surface-2); border-radius:2px;
  overflow:hidden; margin-top:3px}}
.bar i{{display:block; height:100%; background:var(--accent)}}
.row.big .v{{color:var(--executed)}} .row.big .bar i{{background:var(--executed)}}
.tblwrap{{overflow-x:auto}}
.tblwrap table{{width:100%; border-collapse:collapse; font-size:13.5px; min-width:420px}}
.tblwrap th,.tblwrap td{{padding:7px 8px; border-bottom:1px solid var(--rule); text-align:left}}
.tblwrap th{{font-size:11px; color:var(--muted); font-weight:500; letter-spacing:.06em}}
.tblwrap th.r{{text-align:right}}
.tblwrap td.n{{font-family:var(--mono); text-align:right; font-variant-numeric:tabular-nums}}
.tblwrap td.n.z{{color:var(--muted)}}
.tblwrap td.n.hit{{color:var(--executed); font-weight:600}}
.tblwrap td.sub{{color:var(--muted); font-size:12px}}
.up{{color:var(--executed)}} .dn{{color:var(--accent)}}
.trend{{display:flex; align-items:flex-end; gap:3px; height:120px; max-width:640px;
  border-bottom:1px solid var(--rule-strong); padding-bottom:2px}}
.trend .c{{flex:1; display:flex; flex-direction:column; justify-content:flex-end;
  align-items:center; height:100%; min-width:0}}
.trend .c i{{display:block; width:100%; background:var(--executed); border-radius:1px 1px 0 0; min-height:2px}}
.trend .c span{{font-family:var(--mono); font-size:8.5px; color:var(--muted); margin-top:3px}}
.fact{{max-width:640px; margin-bottom:30px; padding-bottom:6px}}
.fact h3{{font-size:15px; margin-bottom:10px}}
.fact h3 em{{font-style:normal; font-family:var(--mono); font-size:11px;
  color:var(--muted); margin-left:8px; letter-spacing:.06em}}
.fact table{{min-width:0}}
.fact td{{padding:8px 8px 8px 0}}
.fact td.n{{font-family:var(--mono); text-align:right; white-space:nowrap;
  font-variant-numeric:tabular-nums}}
.fact td.n.b{{font-weight:600; color:var(--executed)}}
.fact td.sub{{color:var(--muted); font-size:11.5px; text-align:right}}
.sgs{{max-width:640px; display:flex; flex-direction:column; gap:2px}}
.sg{{padding:14px 0; border-bottom:1px solid var(--rule)}}
.sg-h{{display:flex; align-items:baseline; justify-content:space-between; gap:14px}}
.sg-n{{font-family:var(--serif); font-size:15.5px; font-weight:700; line-height:1.45}}
.sg-v{{font-family:var(--mono); font-size:13px; color:var(--ink-2); white-space:nowrap;
  font-variant-numeric:tabular-nums}}
.sg-v b{{font-size:17px; color:var(--executed)}}
.sg-d{{font-family:var(--mono); font-size:11px; color:var(--muted); margin-top:3px}}
.sg .bd{{font-size:12px; color:var(--ink-2); margin-top:7px; line-height:1.85;
  padding-left:11px; border-left:2px solid var(--rule)}}
.sg-m{{font-family:var(--mono); font-size:10.5px; color:var(--muted); margin-top:6px}}
.sg-m a{{color:var(--muted); border-bottom:1px solid var(--rule-strong)}}
.gaps{{max-width:640px; display:flex; flex-direction:column; gap:20px}}
.gap{{padding-left:14px; border-left:2px solid var(--rule-strong)}}
.gap h3{{font-size:14px; margin-bottom:5px}}
.gap p{{margin:0; font-size:13px; color:var(--ink-2); line-height:1.95}}
.fsrc{{font-size:11px; color:var(--muted); margin:8px 0 0}}
.src{{font-size:12.5px; color:var(--ink-2); max-width:640px; padding-left:1.2em}}
.src li{{margin-bottom:9px}}
.src a{{color:var(--accent)}}
</style>
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
    <div class="brand">世界死刑執行記録<small>WORLD EXECUTION RECORD</small></div>
    <div class="mm"><a class="lang" href="en/">English</a></div>
  </div>
</header>

<nav class="mainnav">
  <div class="wrap"><a href="./">世界の記録</a><a href="japan.html">日本の記録</a>\
<a href="shi.html" aria-current="page">日本の死</a><a href="archive.html">記録アーカイブ</a>\
<a href="yomimono.html">読み物</a><a href="about.html">編集方針</a>\
<a href="contact.html">お問い合わせ</a></div>
</nav>

<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>日本の死</h2></div>
  <p class="lede">
    日本で、どんな死が、どれくらいあるか。役所が公表した数字だけを集めています。
    <b>死が確定したものだけ</b>を載せます。けがをした方や、救急車で運ばれた方の数は載せません。
    人の名前は載りません。役所が名前を伏せて公表しているものだけを扱うためです。
  </p>
</div></section>
"""

FOOT = """
<div class="wrap">
<footer>
  <div class="nav"><a href="./">世界の記録</a><a href="japan.html">日本の記録</a>\
<a href="shi.html">日本の死</a><a href="archive.html">記録アーカイブ</a>\
<a href="yomimono.html">読み物</a><a href="about.html">編集方針</a>\
<a href="contact.html">お問い合わせ</a><a href="privacy.html">プライバシーポリシー</a></div>
  <b>世界死刑執行記録</b> — 掲載するのは出典で確認できた数字のみ。
</footer>
</div>

</body>
</html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    d = load()
    traffic = d.get("traffic", {})
    yearly = d.get("yearly", {})

    body = (block_today(traffic)
            + block_trend(traffic)
            + block_perday(yearly)
            + block_facts(yearly)
            + block_pref(traffic)
            + block_saigai(d.get("saigai", {}))
            + block_gaps()
            + block_src(yearly, traffic))

    out = HEAD.format(site=SITE, ga=GA) + body + FOOT
    p = os.path.join(ROOT, "shi.html")
    io.open(p, "w", encoding="utf-8", newline="\n").write(out)
    print("shi.html を作りました（%d日ぶんの交通事故、死因 %d種）"
          % (len(traffic), len(yearly.get("causes", []))))


if __name__ == "__main__":
    main()
