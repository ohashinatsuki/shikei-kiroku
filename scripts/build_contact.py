# -*- coding: utf-8 -*-
"""お問い合わせページ（日英）を作る。

    python scripts/build_contact.py

Googleフォームを埋め込む形。メールアドレスはサイトに一切出さない。
英語フォームがまだ無いときは、EN_FORM を空のままにしておくと、
英語ページから日本語フォームへ案内する形で生成する。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JA_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdcGIKD14yvMaLZs9Z4KDsrksoLmCQYHN9-XkV9baRQC9deVg/viewform"
EN_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfuX1UQQUBH8jcReq5Df0uJpLMCpJ5YWq_Qe2XDvGfDimvYAw/viewform"

src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_site.py"),
              encoding="utf-8").read().replace("\nmain()\n", "\n")
ns = {"__name__": "borrowed",
      "__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_site.py")}
exec(compile(src, "build_site.py", "exec"), ns)
page = ns["page"]


def embed(url, lang="ja"):
    return ('<div class="formwrap"><iframe src="%s?embedded=true&amp;hl=%s" '
            'width="100%%" height="1180" frameborder="0" marginheight="0" marginwidth="0" '
            'title="%s" loading="lazy">%s</iframe></div>'
            % (url, lang,
               "お問い合わせフォーム" if lang == "ja" else "Contact form",
               "読み込んでいます…" if lang == "ja" else "Loading…"))


JA = """
<main class="wrap">
<article>
  <h1>お問い合わせ</h1>

  <p class="lead">世界死刑執行記録へのご連絡は、下のフォームからお願いします。
  いただいた内容は運営者のみが確認します。</p>

  <div class="note">
    <b>掲載内容の誤りを見つけた方へ。</b>このサイトは出典で確認できたことだけを載せていますが、
    出典そのものが誤っている場合や、後から訂正される場合があります。
    お気づきの点があれば、該当ページのURLとあわせてお知らせください。
    確認のうえ訂正し、訂正した旨を記録に残します。
  </div>

  <h2>お受けしている内容</h2>
  <ul>
    <li><b>掲載内容の誤りのご指摘</b> — 日付、氏名、罪状、出典など</li>
    <li><b>掲載内容の削除のお申し出</b> — ご本人・ご遺族・関係者の方から</li>
    <li><b>取材・引用のご相談</b></li>
    <li><b>サイトの不具合</b> — 表示の崩れ、リンク切れなど</li>
    <li>その他のご連絡</li>
  </ul>

  <h2>お答えできないこと</h2>
  <ul>
    <li><b>個別の事件についての見解や、死刑制度への賛否。</b>このサイトは立場を取りません
      （<a href="about.html">編集方針</a>）。</li>
    <li><b>法律相談。</b>弁護士ではありません。</li>
    <li><b>まだ執行されていない方についてのお問い合わせ。</b>このサイトは執行が確認された
      事例のみを扱っており、公判中の方や死刑確定者の情報は扱っていません。</li>
  </ul>

  <h2>返信について</h2>
  <p>返信をご希望の場合は、フォームにメールアドレスをご記入ください。
  <b>記入は任意です。</b>匿名でのご指摘も歓迎します。
  すべてに返信できるとは限りませんが、いただいた内容はすべて確認します。</p>
  <p>迷惑メール対策のため、メールアドレスはこのサイトに掲載していません。</p>

  {form}

  <p class="count">フォームが表示されない場合は、
  <a href="{url}?hl=ja" target="_blank" rel="noopener">こちらのページ</a>から直接ご記入いただけます。</p>

  <div class="rev">2026-09-08</div>
</article>
</main>
"""

EN = """
<main class="wrap">
<article>
  <h1>Contact</h1>

  <p class="lead">Please use the form below to get in touch. Messages are read by the editor
  only.</p>

  <div class="note">
    <b>If you have found an error.</b> This site publishes only what can be confirmed from a
    cited source, but sources are sometimes wrong, and are sometimes revised later. If you spot
    something, please tell us, together with the URL of the page. The entry will be checked and
    corrected, and a note kept that it was corrected.
  </div>

  <h2>What this form is for</h2>
  <ul>
    <li><b>Errors in the records</b> — dates, names, charges, sources</li>
    <li><b>Requests for removal</b> — from the people concerned, their families, or others
      affected</li>
    <li><b>Press enquiries and permission to quote</b></li>
    <li><b>Problems with the site</b> — broken links, display faults</li>
    <li>Anything else</li>
  </ul>

  <h2>What cannot be answered</h2>
  <ul>
    <li><b>Opinions on individual cases, or on capital punishment itself.</b> This site takes no
      position (see <a href="about.html">About this site</a>).</li>
    <li><b>Legal advice.</b> The editor is not a lawyer.</li>
    <li><b>Enquiries about people who have not been executed.</b> This site records only
      executions that have been carried out. It does not hold information on defendants on trial
      or on people under sentence of death.</li>
  </ul>

  <h2>Replies</h2>
  <p>If you would like a reply, please give an email address on the form. <b>This is
  optional</b> — anonymous corrections are welcome. Not every message can be answered, but every
  message is read.</p>
  <p>No email address is published on this site, to avoid spam.</p>

  {form}

  <p class="count">If the form does not appear, you can open it
  <a href="{url}?hl=en" target="_blank" rel="noopener">directly here</a>.</p>

  <div class="rev">8 September 2026</div>
</article>
</main>
"""

EN_JA_NOTICE = """
  <div class="note"><b>Note.</b> The contact form is currently in Japanese only. If you write in
  English in the message field, it will be read and understood. An English form is being
  prepared.</div>
"""


def write(name, text):
    full = os.path.join(ROOT, name)
    if os.path.dirname(full):
        os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8", newline="\n").write(text)


write("contact.html", page(
    "ja", "お問い合わせ — 世界死刑執行記録",
    "世界死刑執行記録へのお問い合わせフォーム。掲載内容の誤りのご指摘、削除のお申し出、"
    "取材・引用のご相談などを受け付けています。",
    "contact.html", JA.format(form=embed(JA_FORM, "ja"), url=JA_FORM),
    alt=("contact.html", "en/contact.html")))

en_form = EN_FORM or JA_FORM
en_body = EN.format(form=(("" if EN_FORM else EN_JA_NOTICE) + embed(en_form, "en")), url=en_form)
write("en/contact.html", page(
    "en", "Contact — World Execution Record",
    "Contact form for World Execution Record. Corrections to the records, removal requests, "
    "press enquiries and permission to quote.",
    "en/contact.html", en_body, alt=("contact.html", "en/contact.html")))

print("お問い合わせページ 2枚を生成しました" + ("" if EN_FORM else "（英語版は日本語フォームを案内中）"))
