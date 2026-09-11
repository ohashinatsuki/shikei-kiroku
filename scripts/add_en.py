# -*- coding: utf-8 -*-
"""data.json の各記録に英語版のフィールドを足す。

英語版サイト（/en/）で使う。翻訳ではなく、もとの出典が使っていた
英語表記に戻す作業。訳しなおしによる誤りを避けるため、対応表を
固定して機械的に置き換える。

    python scripts/add_en.py

足すフィールド:
    charge_en / method_en / place_en / extra_en / src_en
    name_en（日本の記録だけ。漢字の氏名をローマ字にする）

対応表にない語が出てきたら、その場で止めて一覧を出す。
勝手に推測して英語をでっち上げない。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

METHOD = {
    "絞首刑": "Hanging",
    "絞首": "Hanging",
    "非公表（サウジは通常、斬首）": "Not disclosed (Saudi Arabia generally uses beheading)",
    "薬物注射（3剤・エトミデート）": "Lethal injection (three-drug, etomidate)",
    "薬物注射（3剤）": "Lethal injection (three-drug)",
    "銃殺": "Firing squad",
}

PLACE = {
    "アルダビール中央刑務所": "Ardabil Central Prison",
    "アーデルアーバード刑務所（シーラーズ）": "Adelabad Prison, Shiraz",
    "イスファハーン中央刑務所": "Isfahan Central Prison",
    "イスファハーン中央（ダストゲルド）刑務所": "Isfahan Central (Dastgerd) Prison",
    "イーラーム中央刑務所": "Ilam Central Prison",
    "カラジ中央刑務所": "Karaj Central Prison",
    "ガルナダ軍事刑務所（シャハート、東部）": "Gharnada Military Prison, Shahhat (eastern Libya)",
    "ゲゼルヘサール刑務所（カラジ）": "Ghezel Hesar Prison, Karaj",
    "ゴム中央刑務所": "Qom Central Prison",
    "ゴルガーン刑務所（ゴレスターン州）": "Gorgan Prison, Golestan Province",
    "サナンダジ中央刑務所": "Sanandaj Central Prison",
    "シャフルード刑務所（セムナーン州）": "Shahrud Prison, Semnan Province",
    "サブゼヴァール中央刑務所": "Sabzevar Central Prison",
    "サーリー中央刑務所": "Sari Central Prison",
    "ザーヘダーン中央刑務所": "Zahedan Central Prison",
    "シーラーズ刑務所（ファールス州）": "Shiraz Prison, Fars Province",
    "ジーザーン州": "Jazan Province",
    "セピーダール刑務所（アフヴァーズ）": "Sepidar Prison, Ahvaz",
    "セムナーン中央刑務所": "Semnan Central Prison",
    "セムナーン刑務所（セムナーン州）": "Semnan Prison, Semnan Province",
    "タブリーズ中央刑務所": "Tabriz Central Prison",
    "タブーク州": "Tabuk Province",
    "チャンギ刑務所": "Changi Prison",
    "デズフール中央刑務所": "Dezful Central Prison",
    "デフダシュト中央刑務所": "Dehdasht Central Prison",
    "ハーイル州": "Ha'il Province",
    "バーボル中央刑務所": "Babol Central Prison",
    "フロリダ州立刑務所（スターク）": "Florida State Prison, Starke",
    "ホッラマーバード中央刑務所": "Khorramabad Central Prison",
    "ベフシャフル中央刑務所": "Behshahr Central Prison",
    "ボルージェルド刑務所": "Borujerd Prison",
    "マシュハド刑務所": "Mashhad Prison",
    "マークー中央刑務所": "Maku Central Prison",
    "メッカ州": "Mecca Province",
    "メディナ州": "Medina Province",
    "ヤズド中央刑務所": "Yazd Central Prison",
    "ラフサンジャン刑務所（ケルマーン州）": "Rafsanjan Prison, Kerman Province",
    "ラーカーン刑務所（ラシュト）": "Lakan Prison, Rasht",
    "リヤド州": "Riyadh Province",
    "ヴァキーラーバード刑務所（マシュハド）": "Vakilabad Prison, Mashhad",
    "仙台拘置支所": "Sendai Detention Branch",
    "名古屋拘置所": "Nagoya Detention House",
    "大阪拘置所": "Osaka Detention House",
    "広島拘置所": "Hiroshima Detention House",
    "東京拘置所": "Tokyo Detention House",
    "東部州": "Eastern Province",
    "東部（ハフタル支配地域）": "Eastern Libya (area under Haftar's control)",
    "福岡拘置所": "Fukuoka Detention House",
}

EXTRA = {
    "1977年死刑判決。判決から35年。フロリダ州で今年14件目":
        "Sentenced to death in 1977; 35 years from sentence to execution. The 14th execution in Florida this year.",
    "2008年死刑判決、2018年再判決。最後の言葉「事故だった。傷つけるつもりはなかった」":
        "Sentenced to death in 2008 and resentenced in 2018. Last words: “It was an accident. I never meant to hurt anyone.”",
    "2011年大阪地裁死刑、2016年2月最高裁で確定。2025年6月以来1年2か月ぶり、高市内閣で初":
        "Sentenced to death by the Osaka District Court in 2011; finalised by the Supreme Court in February 2016. The first execution in Japan in one year and two months, and the first under the Takaichi cabinet.",
    "2年11か月ぶりの執行だった。":
        "The first execution in Japan in two years and eleven months.",
    "この2日間で、オウム真理教事件の死刑確定者13人全員の刑が執行された。":
        "Over these two days, all thirteen people under sentence of death for the Aum Shinrikyo case were executed.",
    "アフガニスタン国籍。3年前の逮捕時に警察の銃撃を受けて歩行機能を失っており、車椅子に座ったまま執行された。":
        "Afghan national. He had lost the use of his legs after being shot by police during his arrest three years earlier, and was hanged while seated in his wheelchair.",
    "キサース（同害報復）による死刑判決。当局の発表はなく、人権団体が後日確認した。":
        "Sentenced to death under qisas (retribution in kind). The authorities made no announcement; the execution was confirmed later by human rights organisations.",
    "ゴンバデ・カーヴース出身。4人の子の父。":
        "From Gonbad-e Kavus. A father of four.",
    "サーヴェ出身。": "From Saveh.",
    "2026年1月の抗議行動で逮捕された。当局の発表はなく、遺体の即時引き渡しも拒まれた。":
        "He was arrested during the January 2026 protests. The authorities made no "
        "announcement, and the prison refused to hand his body over to his family "
        "immediately.",
    "夫を殺害したとして5年前に逮捕された。当局の発表はない。":
        "She had been arrested five years earlier in connection with the killing of "
        "her husband. The authorities made no announcement.",
    "母の交際相手を殺害したとして4年前に逮捕された。":
        "He had been arrested four years earlier on a charge of killing his mother's "
        "partner.",
    "出典により氏名の表記が異なる（HRANA: Ezzat Asgari Galugahi／Hengaw: Asgari Khalilshahr）。当局の発表はない。":
        "The sources render the name differently (HRANA: Ezzat Asgari Galugahi; "
        "Hengaw: Asgari Khalilshahr). The authorities made no announcement.",
    "イーラーンシャフル出身のバルーチ人。5人の子の父。":
        "A Baloch man from Iranshahr. A father of five.",
    "ナジャファーバード出身。3年前に逮捕された。":
        "From Najafabad. He was arrested three years earlier.",
    "バンダレ・アッバース出身。3人の子の父。":
        "From Bandar Abbas. A father of three.",
    "「ホッグ・トレイル連続殺人」と呼ばれた一連の事件の1件。フロリダ州で今年15件目。":
        "One of the series of killings known as the “Hog Trail Murders”. The 15th "
        "execution in Florida this year.",
    "シンガポール国籍。CNBの発表は年齢・国籍のみで、氏名は現地報道による":
        "Singaporean national. The Central Narcotics Bureau announced only age and nationality; the name comes from local reporting.",
    "マレーシア国籍。氏名は現地報道による":
        "Malaysian national. The name comes from local reporting.",
    "中国籍。": "Chinese national.",
    "再審請求中の執行だった。":
        "He was executed while a request for a retrial was pending.",
    "同じ事件でエジプト国籍の共犯者1人も同日に執行された。":
        "An Egyptian co-defendant in the same case was executed on the same day.",
    "同じ事件で共犯者1人も同日に執行された。":
        "A co-defendant in the same case was executed on the same day.",
    "同日10人。氏名非公表": "Ten people executed on this day. Names not disclosed.",
    "同日6人。氏名非公表": "Six people executed on this day. Names not disclosed.",
    "教団元代表。麻原彰晃を名乗った。":
        "Former leader of the cult, who went by the name Shoko Asahara.",
    "法務大臣は会見で「極めて残忍な事案」と述べたのみで、事件の詳細は公表しなかった。":
        "At the press conference the Minister of Justice described the case only as “extremely cruel” and did not disclose details.",
    "犯行時19歳。少年時の犯行で死刑が執行された数少ない例。":
        "He was 19 at the time of the crime — one of the few cases in Japan where a person has been executed for an offence committed as a minor.",
    "秋葉原無差別殺傷事件。": "The Akihabara massacre.",
}

SRC = {
    "Ajel（内務省発表）": "Ajel (Ministry of Interior announcement)",
    "Akhbarna（内務省発表）": "Akhbarna (Ministry of Interior announcement)",
    "Al-Wathaq（内務省発表）": "Al-Wathaq (Ministry of Interior announcement)",
    "Aqlam Al-Khabar（内務省発表）": "Aqlam Al-Khabar (Ministry of Interior announcement)",
    "Manbar News（内務省発表）": "Manbar News (Ministry of Interior announcement)",
    "Okaz（内務省発表）": "Okaz (Ministry of Interior announcement)",
    "Riyadh 24（内務省発表）": "Riyadh 24 (Ministry of Interior announcement)",
    "Slaati（内務省発表）": "Slaati (Ministry of Interior announcement)",
    "Yemen Window（内務省発表）": "Yemen Window (Ministry of Interior announcement)",
    "サウジ通信（SPA）": "Saudi Press Agency (SPA)",
    "CBS Miami／DPIC": "CBS Miami / DPIC",
    "WUSF／DPIC": "WUSF / DPIC",
    "WUSF（AP）": "WUSF (AP)",
    "Hands Off Cain（AP）": "Hands Off Cain (AP)",
    "HRANA": "HRANA (Human Rights Activists News Agency)",
    "Hengaw": "Hengaw",
    "Hengaw／Death Penalty News": "Hengaw / Death Penalty News",
    "IHRNGO": "Iran Human Rights (IHRNGO)",
    "IHRNGO／Death Penalty News": "Iran Human Rights (IHRNGO) / Death Penalty News",
    "Iran HRM": "Iran Human Rights Monitor",
    "NCRI": "NCRI",
    "NCRI／Death Penalty News": "NCRI / Death Penalty News",
    "Libya Observer（CIHRS）": "Libya Observer (CIHRS)",
    "中央麻薬取締局（CNB）発表": "Central Narcotics Bureau (CNB) announcement",
    "法務省（法務大臣臨時記者会見）": "Ministry of Justice (press conference by the Minister of Justice)",
    "時事通信／NHK": "Jiji Press / NHK",
    "アムネスティ日本／報道": "Amnesty International Japan / news reports",
}

# 氏名の英語表記。おもに日本の記録（漢字 → ローマ字）。英語版サイトで使う。
# 読みは執行時の英語報道（Japan Times, Kyodo, NHK World など）に合わせる。
# 表にない氏名が出てきたら止まるので、出典の英語表記を確認してから足すこと。
NAME_EN = {
    "加納 惠喜": "Keiki Kano",
    "小林 薫": "Kaoru Kobayashi",
    "金川 真大": "Masahiro Kanagawa",
    "宮城 吉英": "Yoshihide Miyagi",
    "濱崎 勝次": "Katsuji Hamasaki",
    "熊谷 徳久": "Tokuhisa Kumagai",
    "加賀山 領治": "Ryoji Kagayama",
    "藤島 光雄": "Mitsuo Fujishima",
    "川﨑 政則": "Masanori Kawasaki",
    "小林 光弘": "Mitsuhiro Kobayashi",
    "髙見澤 勤": "Tsutomu Takamizawa",
    "神田 司": "Tsukasa Kanda",
    "津田 寿美年": "Sumitoshi Tsuda",
    "若林 一行": "Kazuyuki Wakabayashi",
    "吉田 純子": "Junko Yoshida",
    "鎌田 安利": "Yasutoshi Kamata",
    "田尻 賢一": "Kenichi Tajiri",
    "住田 紘一": "Koichi Sumida",
    "西川 正勝": "Masakatsu Nishikawa",
    "松井 喜代司": "Kiyoshi Matsui",
    "関 光彦": "Teruhiko Seki",
    "中川 智正": "Tomomasa Nakagawa",
    "井上 嘉浩": "Yoshihiro Inoue",
    "土谷 正実": "Masami Tsuchiya",
    "新實 智光": "Tomomitsu Niimi",
    "早川 紀代秀": "Kiyohide Hayakawa",
    "松本 智津夫": "Chizuo Matsumoto",
    "遠藤 誠一": "Seiichi Endo",
    "岡崎 一明": "Kazuaki Okazaki",
    "広瀬 健一": "Kenichi Hirose",
    "林 泰男": "Yasuo Hayashi",
    "横山 真人": "Masato Yokoyama",
    "端本 悟": "Satoru Hashimoto",
    "豊田 亨": "Toru Toyoda",
    "岡本 啓三": "Keizo Okamoto",
    "末森 博也": "Hiroya Suemori",
    "庄子 幸一": "Koichi Shoji",
    "鈴木 泰徳": "Yasunori Suzuki",
    "魏 巍": "Wei Wei",
    "小野川 光紀": "Mitsunori Onogawa",
    "藤城 康孝": "Yasutaka Fujishiro",
    "高根沢 智明": "Tomoaki Takanezawa",
    "加藤 智大": "Tomohiro Kato",
    "白石 隆浩": "Takahiro Shiraishi",
    "高見 素直": "Sunao Takami",
    # 日本以外でも、氏名に日本語の注が付いている場合はここに足す
    "Mosayeb（姓は未報道）": "Mosayeb (surname not reported)",
}

from charges_en import CHARGE_EN as CHARGE


def need(table, value, field, entry, missing):
    if value in ("", None):
        return ""
    if value in table:
        return table[value]
    missing.setdefault(field, set()).add(value)
    return None


def main():
    p = "data.json"
    d = json.load(io.open(p, encoding="utf-8"))
    missing = {}
    for e in d["E"]:
        e["method_en"] = need(METHOD, e.get("method"), "method", e, missing)
        e["place_en"] = need(PLACE, e.get("place"), "place", e, missing)
        e["extra_en"] = need(EXTRA, e.get("extra"), "extra", e, missing)
        e["charge_en"] = need(CHARGE, e.get("charge"), "charge", e, missing)
        e["src_en"] = need(SRC, e.get("src"), "src", e, missing)
        # 日本の記録は必ず対応表を通す。日本以外は名前がもともとローマ字なので、
        # 対応表にあるときだけ置き換える（日本語の注が付いている場合など）
        nm = e.get("name") or ""
        if e["c"] == "Japan" and nm:
            e["name_en"] = need(NAME_EN, nm, "name", e, missing)
        else:
            e["name_en"] = NAME_EN.get(nm, nm)
    if missing:
        print("対応表にない語があります。翻訳を足してください。\n")
        for f, vals in missing.items():
            print("=== %s : %d件 ===" % (f, len(vals)))
            for v in sorted(vals):
                print("  " + v)
            print()
        sys.exit(1)
    d["E"].sort(key=lambda x: (x["d"], x["c"], x.get("name") or ""))
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    print("英語フィールドを追加しました: %d件" % len(d["E"]))


main()
