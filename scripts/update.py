# -*- coding: utf-8 -*-
"""毎日1回、新しく確認できた死刑執行を data.json に追記する。

方針（CLAUDE.md と同じ）:
  - 執行が確認された事例のみ。判決、恩赦、執行の危険がある人は載せない。
  - 出典で確認できた最少数。推測で水増ししない。
  - 記事の公開日ではなく、実際に執行が行われた日を記録する。

3つの経路で集める:
  1. Hengaw（イラン）  … 一覧から新着記事だけを取得。世界の執行の約8割。
  2. 世界の巡回        … ウェブ検索で、それ以外の国を毎日さがす。
                         これがないとイランと米国しか載らなくなる。
  3. DPIC（米国）      … 表を機械的に読み、未登録の行だけ詳しく調べる。
"""
import datetime
import json
import os
import sys
from typing import List, Optional

import anthropic
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data.json")
MODEL = "claude-opus-5"
MAX_US_LOOKUPS = 3   # 1回の実行で調べる米国の件数の上限（費用のふた）
SWEEP_DAYS = 10      # 世界の巡回でさかのぼる日数

# 近年、実際に執行を行っている国。毎日ここを見に行く。
WATCH = """イラク、サウジアラビア、エジプト、イエメン、ソマリア、シリア、
アフガニスタン、パレスチナ（ガザ）、クウェート、バーレーン、ヨルダン、
アラブ首長国連邦、リビア、スーダン、南スーダン、ナイジェリア、
バングラデシュ、パキスタン、インド、シンガポール、マレーシア、
インドネシア、タイ、ベトナム、台湾、北朝鮮、中国、日本、
ベラルーシ、キューバ、ミャンマー、ボツワナ、エチオピア"""

RULES = """あなたは「世界死刑執行記録」という資料サイトの編集者です。
人権報道の記録として、事実だけを淡々と日本語で記述します。

絶対の規則:
- 実際に執行が行われたと出典が述べている事例だけを記録する。
  死刑判決が出ただけ、執行の危険がある、執行が迫っている、恩赦・停止された、
  という記事は一件も記録しない。
- 日付は記事の公開日ではなく、実際に執行が行われた日を書く。
  記事が「9月6日に報じた、9月2日の夜明けに執行された」と述べているなら
  2026-09-02 とする。
- 出典に書かれていないことを補わない。年齢、罪状、刑務所名が書かれて
  いなければ空にする。
- 1人につき1件。複数人がまとめて執行された記事は、人数分に分ける。
- 氏名は出典のローマ字表記のまま（日本語に訳さない）。氏名非公表なら null。
- 罪状・執行方法・場所は日本語で書く。
  罪状の例: 殺人 / 麻薬犯罪 / 覚醒剤の密売 / 強盗殺人 / 国家反逆
  執行方法の例: 絞首 / 斬首 / 薬物注射（3剤）/ 銃殺
  場所の例: ラーカーン刑務所（ラシュト） / セムナーン刑務所（セムナーン州）
- extra には、出典が伝えている重要な事情だけを1〜2文で日本語で書く。
  例: 国籍、当局の発表がなかったこと、判決からの年数、特筆すべき状況。
  書くことがなければ空文字にする。
"""


class Entry(BaseModel):
    c: str = Field(description="国名の英語表記。例: Iran, Iraq, Egypt, United States")
    d: str = Field(description="執行が行われた現地の日付 YYYY-MM-DD")
    name: Optional[str] = Field(description="氏名のローマ字表記。非公表なら null")
    age: Optional[int] = Field(description="年齢。不明なら null")
    charge: str = Field(description="罪状（日本語）")
    method: str = Field(description="執行方法（日本語）")
    place: str = Field(description="執行場所（日本語）。不明なら空文字")
    extra: str = Field(description="補足（日本語）。なければ空文字")
    src: str = Field(description="出典の名前。例: Hengaw, DPIC, Hands Off Cain")
    url: str = Field(description="出典のURL")
    t: Optional[str] = Field(description="現地の死亡宣告時刻 HH:MM。不明なら null")
    tz: Optional[str] = Field(description="タイムゾーン略号。例: EDT, CDT。不明なら null")
    off: Optional[int] = Field(description="UTCオフセット（時間）。EDTなら -4。不明なら null")


class Extraction(BaseModel):
    entries: List[Entry]


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    data["E"].sort(key=lambda e: (e["d"], e["c"], e.get("name") or ""))
    with open(DATA_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def key_of(e):
    return (e["c"], (e.get("name") or "").strip().lower(), e["d"])


def parse_entries(client, prompt):
    r = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
        output_format=Extraction,
    )
    return list(r.parsed_output.entries)


def search_text(client, ask, max_uses):
    """ウェブ検索をさせて、本文だけ取り出す。"""
    res = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": max_uses}],
        messages=[{"role": "user", "content": ask}],
    )
    if res.stop_reason == "refusal":
        return ""
    return "\n".join(b.text for b in res.content if b.type == "text").strip()


# ---------------- 1. イラン ----------------

def extract_iran(client, articles):
    blocks = ["=== 出典URL: %s ===\n%s" % (a["url"], a["text"]) for a in articles]
    prompt = (
        RULES
        + """
以下はイランの人権団体 Hengaw の新着記事です。
執行が行われたと述べている記事だけから、執行を1人ずつ取り出してください。
c は必ず Iran、src は Hengaw、url はその記事の出典URLにしてください。
イランは時刻が公表されないため t / tz / off はすべて null にしてください。
該当がなければ entries を空の配列にしてください。

"""
        + "\n\n".join(blocks)
    )
    return parse_entries(client, prompt)


# ---------------- 2. 世界の巡回 ----------------

def sweep_world(client, since, recent_summary):
    """決まったソースだけでは国が偏るので、毎日ウェブ検索で世界をさがす。"""
    ask = """{since} 以降に世界のどこかで実際に行われた死刑執行を、ウェブ検索で
調べてください。

とくに次の国を確認してください。イランと米国は別の仕組みで取得しているので、
大きな見落としがあるときだけ報告してください。

{watch}

確認先の例: Hands Off Cain (handsoffcain.info)、Death Penalty News
(deathpenaltynews.blogspot.com)、Amnesty International、Human Rights Watch、
Reprieve、各国の国営通信社と報道機関。

重要な条件:
- 実際に執行されたと報じられた事例だけ。死刑判決、執行の危険、執行が迫って
  いるという記事は報告しない。
- 記事の公開日ではなく、執行が行われた日を書く。
- 中国・北朝鮮・ベトナムのように執行を公表しない国は、個別に確認できる報道が
  あるときだけ報告する。年間推定値は書かない。
- 氏名が公表されていない場合は人数を書く。
- 出典のURLを必ず添える。

すでに記録済みのもの（重複して報告しないでください）:
{recent}

見つかった執行を、国ごとに、日付・氏名・年齢・罪状・執行方法・場所・出典URL
の形で箇条書きにしてください。新しいものが何も見つからなければ「なし」と
だけ書いてください。""".format(since=since, watch=WATCH, recent=recent_summary or "（なし）")

    findings = search_text(client, ask, 14)
    print("世界の巡回: 調査結果 %d字" % len(findings))
    if not findings or findings.strip().rstrip("。") == "なし":
        return []

    prompt = (
        RULES
        + """
以下は、世界各国の死刑執行についての調査結果です。実際に執行されたと確認
できたものだけを記録にしてください。
c は国名の英語表記（Iraq, Egypt, Saudi Arabia, Japan など）にしてください。
時刻が明記されている場合のみ t / tz / off を埋め、なければすべて null に
してください。
確実に執行と確認できないものは含めないでください。

調査結果:
"""
        + findings
    )
    return parse_entries(client, prompt)


# ---------------- 3. 米国 ----------------

def research_us(client, row):
    ask = """米国で行われた死刑執行について調べてください。
日付: {d} / 州: {st} / 氏名: {name} / 年齢: {age}

ウェブ検索を使い、次を確認してください。
1. 死亡宣告の現地時刻（何時何分か）とタイムゾーン略号
2. 有罪となった事件の内容（いつ、どこで、何が起きたか）
3. 執行方法（薬物注射なら薬剤も）
4. 執行が行われた刑務所の名前と所在地
5. 死刑判決が出た年

確認できたことだけを箇条書きで書いてください。確認できなかった項目は
不明と書き、推測しないでください。最後に、根拠にした記事のURLを並べて
ください。""".format(d=row["d"], st=row["state"], name=row["name"], age=row["age"])

    findings = search_text(client, ask, 6)
    if not findings:
        print("  調査できず（%s）" % row["name"])
        return []

    prompt = (
        RULES
        + """
以下は、米国で行われた死刑執行についての調査結果です。これを1件の記録に
してください。
c は United States、src は 地元報道／DPIC、url は調査結果に出てくる報道記事の
URL（なければ https://deathpenaltyinfo.org/executions/2026 ）にしてください。
死亡宣告の時刻がわかった場合のみ t / tz / off を埋めてください
（夏時間: EDT=-4, CDT=-5, MDT=-6, PDT=-7）。わからなければ null。
日付は {d}、氏名は {name}、年齢は {age} です。

調査結果:
{findings}""".format(d=row["d"], name=row["name"], age=row["age"], findings=findings)
    )
    return parse_entries(client, prompt)


# ---------------- 本体 ----------------

def main(sweep_days=SWEEP_DAYS):
    data = load_data()
    state = sources.load_state()
    existing = {key_of(e) for e in data["E"]}
    us_names = {e.get("name") for e in data["E"] if e["c"] == "United States"}
    known_countries = {c["en"] for c in data["C"]}
    client = anthropic.Anthropic()
    today = datetime.date.today().isoformat()

    found = []

    # 1. イラン
    articles = sources.hengaw_new_articles(state["hengaw_urls"])
    if articles:
        try:
            found += extract_iran(client, articles)
        except Exception as e:
            print("イランの抽出でエラー: %s" % e)
        else:
            state["hengaw_urls"] += [a["url"] for a in articles]

    # 2. 世界の巡回
    since = (datetime.date.today() - datetime.timedelta(days=sweep_days)).isoformat()
    if since < sources.MIN_DATE:
        since = sources.MIN_DATE
    recent = "\n".join(
        "%s %s %s" % (e["d"], e["c"], e.get("name") or "氏名非公表")
        for e in sorted(data["E"], key=lambda x: x["d"])
        if e["d"] >= since
    )
    try:
        found += sweep_world(client, since, recent)
    except Exception as e:
        print("世界の巡回でエラー: %s" % e)

    # 3. 米国
    rows = sources.dpic_new_rows(state["dpic_rows"], known_names=us_names)
    for row in rows[:MAX_US_LOOKUPS]:
        try:
            found += research_us(client, row)
        except Exception as e:
            print("米国の調査でエラー(%s): %s" % (row["name"], e))
        else:
            state["dpic_rows"].append(row["key"])

    added, unknown = [], set()
    for e in found:
        rec = e.model_dump()
        if rec["d"] < sources.MIN_DATE or rec["d"] > today:
            print("  日付が範囲外のため見送り: %s %s" % (rec["d"], rec.get("name")))
            continue
        if key_of(rec) in existing:
            print("  既出のため見送り: %s %s %s" % (rec["d"], rec["c"], rec.get("name")))
            continue
        if rec["c"] not in known_countries:
            unknown.add(rec["c"])
        existing.add(key_of(rec))
        data["E"].append(rec)
        added.append(rec)

    if added:
        save_data(data)
    sources.save_state(state)

    lines = ["追加 %d件" % len(added)]
    for a in added:
        lines.append(
            "- %s / %s / %s / %s / %s"
            % (a["d"], a["c"], a.get("name") or "氏名非公表", a["charge"], a["src"])
        )
    if unknown:
        lines.append("")
        lines.append("※ 国名リスト C に未登録の国: " + "、".join(sorted(unknown)))
    report = "\n".join(lines)
    print()
    print(report)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")


if __name__ == "__main__":
    days = SWEEP_DAYS
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        days = int(sys.argv[1])   # 例: python scripts/update.py 30
    main(days)
