# -*- coding: utf-8 -*-
"""英語版の固定ページ（About / Privacy）を作る。

    python scripts/build_en_static.py

build_site.py と同じ枠を使うので、ナビや見た目は自動でそろう。
中身を変えるときはこのファイルを直す。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# build_site.py の page() をそのまま借りる（main() は動かさない）
src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_site.py"),
              encoding="utf-8").read()
src = src.replace("\nmain()\n", "\n")
ns = {"__name__": "borrowed",
      "__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_site.py")}
exec(compile(src, "build_site.py", "exec"), ns)
page = ns["page"]

ABOUT = """
<main class="wrap">
<article>
  <h1>About this site</h1>

  <p class="lead">World Execution Record is a daily record of who has been executed around the
  world. It exists to keep, one by one, the executions that can be confirmed from a published
  source. This page sets out what is recorded here, what is deliberately left out, and how the
  numbers should be read.</p>

  <h2>Who runs this site</h2>
  <table class="kv">
    <tr><th>Editor</th><td>Ryo Kashiwagi</td></tr>
    <tr><th>Based in</th><td>Gifu, Japan</td></tr>
    <tr><th>Started</th><td>September 2026</td></tr>
    <tr><th>Updated</th><td>Daily, at around 03:30 Japan Standard Time</td></tr>
    <tr><th>Affiliation</th><td>An individual record. Not connected to any organisation,
      political party or religious body.</td></tr>
  </table>

  <h2>What is recorded</h2>
  <p>Only executions that were actually carried out after judicial proceedings, and that can be
  confirmed from a published source. Every entry links to the source used to confirm it.</p>

  <h3>What is not recorded</h3>
  <ul>
    <li><b>Murder cases, suspects, arrests, and defendants on trial.</b> Writing about people
      whose guilt has not been established risks doing them serious harm. This is not a site
      about crimes.</li>
    <li><b>Images of bodies, of executions, or of crime scenes.</b> Out of respect for the dead
      and their families. This site works only in text and figures.</li>
    <li><b>Rankings and league tables of countries.</b> This is not a place for comparing states
      against one another.</li>
    <li><b>Arguments for or against capital punishment.</b> Neither side is argued here. What is
      written down is what happened.</li>
  </ul>

  <h2>How the counting works</h2>
  <ul>
    <li><b>Figures are the smallest number that can be confirmed from a source.</b> Where several
      organisations report the same execution, it is counted once. Nothing is inflated by
      estimate.</li>
    <li><b>Dates are converted to Japan Standard Time.</b> Where a country publishes the time of
      death — as the United States does — the local time is converted. An execution carried out
      on a Monday evening in the eastern United States therefore appears here under Tuesday.</li>
    <li><b>Where no time is published</b> — Iran and Saudi Arabia, among others — the local date
      is used as it stands.</li>
    <li><b>Where no name is published</b>, only the number of people is recorded.</li>
    <li><b>Where sources disagree</b> — for instance on the charge — both accounts are given.</li>
  </ul>

  <h2>The limits of this record</h2>
  <div class="note">
    <p style="margin-top:0"><b>“No record for today” does not mean that no one was executed.</b></p>
    <p>Around 80 per cent of the world's executions take place in Iran, and the Iranian
    authorities announce only about one in ten of them. The rest are confirmed over days or weeks
    by human rights organisations working through families and prison sources. The record here
    therefore always grows after the fact.</p>
    <p style="margin-bottom:0">China, North Korea and Vietnam treat their execution figures as
    state secrets and publish nothing. China is believed to execute thousands of people a year,
    but because no source can confirm them, not one of those executions appears here.
    <b>The figures on this site are a fraction of what is actually carried out.</b></p>
  </div>

  <h2>Sources consulted</h2>
  <p>The following are checked every day. The link on the right of each record is the source used
  to confirm that particular execution.</p>
  <ul>
    <li><b><a href="https://hengaw.net/en" target="_blank" rel="noopener">Hengaw Organization for
      Human Rights</a></b> — Iran; daily reports with names, ages and prisons</li>
    <li><b><a href="https://iranhr.net/en/" target="_blank" rel="noopener">Iran Human Rights
      (IHRNGO)</a></b> — Iran; detailed case reporting</li>
    <li><b><a href="https://iran-hrm.com/" target="_blank" rel="noopener">Iran Human Rights
      Monitor</a></b> — Iran; monthly reports</li>
    <li><b><a href="https://www.spa.gov.sa/" target="_blank" rel="noopener">Saudi Press Agency
      (SPA)</a></b> — official Ministry of Interior announcements</li>
    <li><b><a href="https://deathpenaltyinfo.org/" target="_blank" rel="noopener">Death Penalty
      Information Center</a></b> — the United States</li>
    <li><b><a href="https://www.cnb.gov.sg/" target="_blank" rel="noopener">Central Narcotics
      Bureau</a></b> — Singapore</li>
    <li><b><a href="https://handsoffcain.info/" target="_blank" rel="noopener">Hands Off
      Cain</a></b> — worldwide</li>
    <li><b>National press.</b> Times of death in the United States come from AP and local
      reporting; executions in Japan come from the press conference held by the Minister of
      Justice.</li>
  </ul>

  <h2>Corrections</h2>
  <p>Errors are corrected when they are found. Records are not removed; a note is kept that the
  entry was corrected. The same applies where a source later revises its own account.</p>

  <h2>Disclaimer</h2>
  <p>The contents of this site are compiled from published sources, but their accuracy and
  completeness are not guaranteed. Sources may themselves be wrong, or may be revised later. The
  editor accepts no liability for loss arising from use of this site, or for the contents of
  external sites linked from it.</p>

  <div class="rev">Last updated 8 September 2026</div>
</article>
</main>
"""

PRIVACY = """
<main class="wrap">
<article>
  <h1>Privacy policy</h1>

  <p class="lead">How information about visitors is handled on World Execution Record
  (“this site”).</p>

  <h2>What this site does not collect</h2>
  <p>There is no registration, login, comment facility or checkout on this site. The editor does
  not ask visitors to enter, and does not collect, names, email addresses, postal addresses,
  telephone numbers or payment details.</p>

  <h2>Information recorded when you visit</h2>
  <p>This site is published through GitHub Pages (GitHub, Inc.). As a technical consequence of
  serving a page, GitHub's servers may record access information such as IP addresses and
  browser type. This is handled under the
  <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement"
  target="_blank" rel="noopener">GitHub Privacy Statement</a>.</p>
  <p>This site loads typefaces from Google Fonts (Google LLC), which also transmits technical
  information such as your IP address to that company, handled under the
  <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Google Privacy
  Policy</a>.</p>

  <h2>Advertising</h2>
  <p>This site intends to carry advertising through Google AdSense in order to cover running
  costs. Once advertising is in place:</p>
  <ul>
    <li>Google and other third-party vendors may use cookies to serve advertisements based on
      your prior visits to this and other sites.</li>
    <li>You may opt out of personalised advertising at
      <a href="https://adssettings.google.com/authenticated" target="_blank" rel="noopener">Google
      Ads Settings</a>, or opt out of third-party vendor cookies at
      <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">www.aboutads.info</a>.</li>
    <li>See <a href="https://policies.google.com/technologies/ads" target="_blank"
      rel="noopener">Advertising – Policies and Terms – Google</a> for details.</li>
  </ul>
  <div class="note">No advertising cookies are set by this site until advertising is actually
  running.</div>

  <h2>Analytics</h2>
  <p>This site uses Google Analytics (GA4) to understand which pages are read.</p>
  <ul>
    <li>Google Analytics uses cookies to collect information about your visit.</li>
    <li>What is collected is statistical: pages viewed, time on page, referrer, approximate
      region, and browser type.</li>
    <li><b>No personally identifying information is collected.</b> The editor cannot identify
      individual visitors.</li>
    <li>IP address anonymisation is enabled on this site.</li>
  </ul>
  <div class="note">If you would rather not be counted, install the
  <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google
  Analytics Opt-out Browser Add-on</a>, or disable cookies in your browser. The records on this
  site remain fully readable either way.</div>

  <h2>Names appearing in the records</h2>
  <p>This site records the names and ages of people who have been executed. All such information
  is reproduced from material already made public — official government announcements, reports by
  international human rights organisations, and press coverage. No independent investigation is
  carried out to identify individuals.</p>
  <p>Only executions confirmed to have been carried out after judicial proceedings are listed.
  Suspects, people who have been arrested, and defendants on trial are not listed. See
  <a href="about.html">About this site</a>.</p>
  <p>Where an entry is wrong, or where removal is requested, the matter will be checked and
  addressed.</p>

  <h2>Disclaimer</h2>
  <p>The contents of this site are compiled from published sources, but their accuracy and
  completeness are not guaranteed. The editor accepts no liability for loss arising from use of
  this site, nor for the contents or privacy practices of external sites linked from it.</p>

  <h2>Copyright</h2>
  <p>Rights in the text, structure and arrangement of data created for this site rest with the
  editor. Rights in quoted material rest with the respective press organisations and human rights
  bodies. If you quote from this site, please cite its URL.</p>

  <h2>Changes to this policy</h2>
  <p>This policy may change without notice as the law or the services used by this site change.
  Any revised version applies from the moment it is published on this page.</p>

  <div class="rev">Adopted 7 September 2026 / last updated 8 September 2026</div>
</article>
</main>
"""


def write(name, text):
    full = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8", newline="\n").write(text)


write("en/about.html", page(
    "en", "About this site — World Execution Record",
    "The editorial policy of World Execution Record: what is recorded, what is left out, how "
    "executions are counted and dated, and the sources consulted every day.",
    "en/about.html", ABOUT, alt=("about.html", "en/about.html")))

write("en/privacy.html", page(
    "en", "Privacy policy — World Execution Record",
    "How cookies, advertising and analytics are handled on World Execution Record.",
    "en/privacy.html", PRIVACY, alt=("privacy.html", "en/privacy.html")))

print("英語の固定ページ 2枚を生成しました")
