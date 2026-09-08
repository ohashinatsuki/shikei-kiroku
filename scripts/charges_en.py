# -*- coding: utf-8 -*-
"""罪状（charge）の日本語 → 英語の対応表。

英語版サイト用。翻訳ではなく、もとの出典が使っていた英語表現に戻す作業。
新しい罪状が出てきたら、ここに1行足す。add_en.py が自動で拾う。
"""

CHARGE_EN = {
    # --- 決まり文句 ---
    "麻薬犯罪": "Drug offences",
    "殺人": "Murder",
    "殺人等": "Murder and related offences",
    "殺人（キサース）": "Murder (qisas)",
    "麻薬密売（規制薬物）": "Drug trafficking (controlled substances)",
    "覚醒剤の密売": "Trafficking in methamphetamine",
    "テロ関連の罪": "Terrorism-related offences",
    "口論の末に銃で殺害（キサース）":
        "Shot and killed a man following an argument (qisas)",
    "殺人（キサース）※Hengawは麻薬犯罪と報告":
        "Murder (qisas). Hengaw reported the charge as a drug offence",
    "1994年の松本サリン事件、1995年の地下鉄サリン事件など一連のオウム真理教事件による殺人等":
        "Murder and related offences in the Aum Shinrikyo case, including the "
        "1994 Matsumoto sarin attack and the 1995 Tokyo subway sarin attack",

    # --- 米国 ---
    "1976年8月、フロリダ州ボニータスプリングスで交際を断られた16歳の少女を射殺し、友人2人に重傷":
        "Shot dead a 16-year-old girl who had rejected him and seriously wounded "
        "two of her friends in Bonita Springs, Florida, in August 1976",
    "2006年、オーランド近郊で別居中の妻を射殺し、義母に重傷":
        "Shot dead his estranged wife and seriously wounded his mother-in-law "
        "near Orlando in 2006",

    # --- 日本 ---
    "1988年1月、大阪市で投資顧問会社の社長ら2人を殺害し現金を強奪、遺体をコンクリート詰めにして遺棄":
        "Killed the president of an investment advisory firm and one other person "
        "in Osaka in January 1988, robbed them of cash, and disposed of the bodies "
        "encased in concrete",
    "1991年から1992年にかけて、近畿地方でスナックの経営者ら4人を殺害":
        "Killed four people, including bar proprietors, in the Kinki region "
        "between 1991 and 1992",
    "1992年3月、千葉県市川市で一家4人を殺害":
        "Killed a family of four in Ichikawa, Chiba Prefecture, in March 1992",
    "2001年5月、青森県弘前市の消費者金融店舗に放火し、従業員5人を殺害、4人に傷害":
        "Set fire to a consumer finance branch in Hirosaki, Aomori Prefecture, "
        "in May 2001, killing five employees and injuring four",
    "2001年、神奈川県大和市で女性2人を殺害":
        "Killed two women in Yamato, Kanagawa Prefecture, in 2001",
    "2003年6月、福岡市で一家4人を殺害":
        "Killed a family of four in Fukuoka in June 2003",
    "2003年、群馬県のパチンコ店店長ら2人を殺害":
        "Killed two people, including a pachinko parlour manager, in Gunma "
        "Prefecture in 2003",
    "2004年11月、奈良市で小学1年の女児を誘拐して殺害":
        "Abducted and killed a first-grade schoolgirl in Nara in November 2004",
    "2004年8月、兵庫県加古川市で親族7人を殺害":
        "Killed seven relatives in Kakogawa, Hyogo Prefecture, in August 2004",
    "2004年、福岡市で女性3人を殺害":
        "Killed three women in Fukuoka in 2004",
    "2004年と2011年、熊本県内で民家に侵入して金品を奪う目的で女性2人を殺害、男性1人に重傷を負わせた":
        "Broke into homes in Kumamoto Prefecture in 2004 and 2011 to steal money "
        "and valuables, killing two women and seriously injuring one man",
    "2007年8月、名古屋市で帰宅途中の女性を車内に監禁して金品を奪い、窒息死させて遺棄":
        "Confined a woman on her way home in a car in Nagoya in August 2007, "
        "robbed her, suffocated her and dumped the body",
    "2007年、香川県坂出市で義理の姉とその孫2人の計3人を刺殺し、死体を遺棄":
        "Stabbed to death his sister-in-law and her two grandchildren — three "
        "people in all — in Sakaide, Kagawa Prefecture, in 2007, and disposed of "
        "the bodies",
    "2008年3月、茨城県土浦市で通行人ら8人を殺傷し、1人を殺害":
        "Attacked eight people in Tsuchiura, Ibaraki Prefecture, in March 2008, "
        "killing one of them",
    "2008年6月8日、東京・秋葉原の歩行者天国にトラックで突入し、通行人7人を殺害、10人に重軽傷":
        "Drove a truck into a pedestrian precinct in Akihabara, Tokyo, on "
        "8 June 2008, killing seven people and injuring ten",
    "2009年7月5日、大阪市此花区のパチンコ店に放火し5人を死亡させ、10人に重軽傷":
        "Set fire to a pachinko parlour in Konohana Ward, Osaka, on 5 July 2009, "
        "killing five people and injuring ten",
    "2009年、岩手県洋野町で民家に侵入し、帰宅した女性2人を殺害して金品を奪った":
        "Broke into a house in Hirono, Iwate Prefecture, in 2009, killed two women "
        "who returned home, and robbed them",
    "2009年、川崎市でアパートの住人ら3人を包丁で刺殺":
        "Stabbed to death three residents of an apartment building in Kawasaki "
        "in 2009",
    "2010年6月、群馬県安中市で親子3人を殺害":
        "Killed a parent and two children — three people in all — in Annaka, "
        "Gunma Prefecture, in June 2010",
    "2011年9月、岡山市で元同僚の女性を殺害し、遺体を損壊した":
        "Killed a former female colleague in Okayama in September 2011 and "
        "mutilated the body",
    "2017年、神奈川県座間市のアパートで男女9人を殺害":
        "Killed nine men and women in an apartment in Zama, Kanagawa Prefecture, "
        "in 2017",
    "共犯者と共謀し、ファミリーレストランの店内と店前で拳銃を使い2人を射殺":
        "Conspired with accomplices to shoot dead two people with handguns inside "
        "and in front of a family restaurant",
    "名古屋市中区栄で、スナックの経営者を殺害":
        "Killed a bar proprietor in Sakae, Naka Ward, Nagoya",
    "現金を奪う目的で1人を拳銃で射殺し、さらに1人を殺害しようとした（強盗殺人・同未遂）":
        "Shot one person dead with a handgun to steal cash and attempted to kill "
        "another (robbery-murder and attempted robbery-murder)",
    "逮捕を恐れて口封じのため、元妻の伯母ら2人を殺害し死体を遺棄":
        "Killed two people, including an aunt of his former wife, to silence them "
        "for fear of arrest, and disposed of the bodies",
    "金品を奪う目的で2人をナイフで刺殺し、1人を殺害しようとした（強盗殺人・同未遂）":
        "Stabbed two people to death with a knife to steal money and valuables and "
        "attempted to kill a third (robbery-murder and attempted robbery-murder)",
    "暴力団組長として配下と共謀し、別々の機会に拳銃で3人を射殺、うち2件で死体を遺棄":
        "As a crime syndicate boss, conspired with subordinates to shoot dead three "
        "people on separate occasions, disposing of the bodies in two of the cases",

    # --- イラン ---
    "2026年1月の抗議行動参加者。「イスラエル・米国・敵対集団のための実行行為」（スパイ法）":
        "A participant in the January 2026 protests, convicted of “carrying out acts "
        "for Israel, the United States and hostile groups” under the espionage law",
    "2026年1月の抗議行動参加者。「敵対集団のための実行行為」（スパイ法）":
        "A participant in the January 2026 protests, convicted of “carrying out acts "
        "for hostile groups” under the espionage law",
    "2026年1月の抗議行動参加者（「アリハーニ広場」事件）。モハーレベ・地上の腐敗・公共物損壊。アフガニスタン系":
        "A participant in the January 2026 protests (the “Alihani Square” case), "
        "convicted of moharebeh, corruption on earth and destruction of public "
        "property. Of Afghan origin",
    "2人を殺害。アフガニスタン国籍": "Killed two people. Afghan national",
    "いとこの殺害（キサース）": "Murder of his cousin (qisas)",
    "武装強盗によるモハーレベ（神への敵対）":
        "Moharebeh (enmity against God) through armed robbery",
    "武装強盗によるモハーレベ（神への敵対）。Saeedの弟":
        "Moharebeh (enmity against God) through armed robbery. Brother of Saeed",
    "殺人（カフェでの口論）": "Murder, following an argument in a café",
    "殺人（キサース）。女性": "Murder (qisas). A woman",
    "夫の殺害（キサース）。強制結婚の被害者。女性":
        "Murder of her husband (qisas). A victim of forced marriage. A woman",
    "報告に記載なし": "Not stated in the report",
    "報告に記載なし。女性": "Not stated in the report. A woman",
    "麻薬犯罪 ※Hengawは6月21日執行と報告":
        "Drug offences. Hengaw reported the execution as having taken place on 21 June",
    "麻薬犯罪（ヘロイン 9kg）": "Drug offences (9 kg of heroin)",
    "麻薬犯罪（覚醒剤・アヘン 11kg）":
        "Drug offences (11 kg of methamphetamine and opium)",

    # --- サウジアラビア ---
    "7歳女児の誘拐・殺害（キサース）。女性":
        "Abduction and murder of a seven-year-old girl (qisas). A woman",
    "アンフェタミン錠剤の密輸・再犯（タアズィール刑）":
        "Smuggling amphetamine tablets, as a repeat offender (ta'zir)",
    "アンフェタミン錠剤の密輸（タアズィール刑）":
        "Smuggling amphetamine tablets (ta'zir)",
    "アンフェタミン錠剤の密輸（タアズィール刑）。エジプト国籍":
        "Smuggling amphetamine tablets (ta'zir). Egyptian national",
    "カプタゴン錠剤の密輸・再犯（タアズィール刑）":
        "Smuggling Captagon tablets, as a repeat offender (ta'zir)",
    "コカインの密輸（タアズィール刑）。ナイジェリア国籍":
        "Smuggling cocaine (ta'zir). Nigerian national",
    "コカインの密輸（タアズィール刑）。ナイジェリア国籍の女性":
        "Smuggling cocaine (ta'zir). A Nigerian woman",
    "ハシシの密輸・再犯（タアズィール刑）":
        "Smuggling hashish, as a repeat offender (ta'zir)",
    "ハシシの密輸（タアズィール刑）。オマーン国籍":
        "Smuggling hashish (ta'zir). Omani national",
    "ハシシ・規制薬物錠剤の密輸（タアズィール刑）":
        "Smuggling hashish and controlled-substance tablets (ta'zir)",
    "ヘロインの密輸（タアズィール刑）。パキスタン国籍":
        "Smuggling heroin (ta'zir). Pakistani national",
    "密輸されたアンフェタミン錠剤を密売目的で受領（タアズィール刑）":
        "Receiving smuggled amphetamine tablets for the purpose of trafficking (ta'zir)",
    "同郷のイエメン人を刺殺（キサース）。イエメン国籍":
        "Stabbed a fellow Yemeni to death (qisas). Yemeni national",
    "同郷のイエメン人を計画的に殺害（キサース）。イエメン国籍":
        "Premeditated killing of a fellow Yemeni (qisas). Yemeni national",
    "同郷のイエメン人を鋭利な工具で殴打し殺害（キサース）。イエメン国籍":
        "Beat a fellow Yemeni to death with a sharp implement (qisas). Yemeni national",
    "妻と娘を就寝中に刃物で殺害（ハッド刑）":
        "Killed his wife and daughter with a blade as they slept (hadd)",
    "娘婿の殺害": "Murder of his son-in-law",
    "母親を銃で殺害（タアズィール刑）": "Shot and killed his mother (ta'zir)",

    # --- リビア・その他 ---
    "テロ・暗殺。軍事法廷の判決":
        "Terrorism and assassination. Sentenced by a military court",
    "テロ（テロ組織への参加、軍人・民間人の暗殺）。軍事法廷の判決":
        "Terrorism — membership of a terrorist organisation and the assassination "
        "of soldiers and civilians. Sentenced by a military court",
    "強姦・強盗": "Rape and robbery",
}
