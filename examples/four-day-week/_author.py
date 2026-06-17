#!/usr/bin/env python3
"""Generality test: an asset-poor, conceptual topic in the LIGHT theme with a warm
brand palette — proving the cinematic system works beyond technical/source decks."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
# light theme + warm professional palette (teal-green + amber) set per-deck
HEAD = ('<!doctype html><html><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="assets/cinematic.css"></head><body>'
        '<div class="slide light" style="--primary:#1f7a5a;--accent:#e0922b">')
FOOT = "</div></body></html>"
MOTIF = """<svg class="nodes" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
  <g stroke="var(--line)" stroke-width="2" fill="none">
   <line x1="1360" y1="280" x2="1560" y2="200"/><line x1="1560" y1="200" x2="1740" y2="320"/>
   <line x1="1560" y1="200" x2="1600" y2="460"/><line x1="1740" y1="320" x2="1840" y2="520"/></g>
  <g fill="var(--surface)" stroke="var(--primary)" stroke-width="2">
   <circle cx="1360" cy="280" r="40"/><circle cx="1560" cy="200" r="54"/><circle cx="1740" cy="320" r="44"/><circle cx="1600" cy="460" r="34"/></g>
  <g fill="var(--accent)"><circle cx="1460" cy="240" r="8"/><circle cx="1650" cy="260" r="8"/></g></svg>"""

SLIDES = [
f"""{MOTIF}<div class="pad center">
  <div class="eyebrow">The future of work</div>
  <div class="display hero">The Four-Day Week</div>
  <div class="lead">Same pay. One less day. The evidence is in — and it's not what skeptics expected.</div>
  <div class="rule"></div></div>""",
f"""{MOTIF}<div class="pad center">
  <div class="eyebrow">The premise</div>
  <div class="plain h1">We've optimized everything<br><span style="color:var(--muted)">except the week itself.</span></div>
  <div class="lead">The five-day week is a 1920s artifact. The largest trials ever run just tested whether it still earns its place.</div></div>""",
"""<div class="pad center">
  <div class="eyebrow">UK pilot · 61 organisations · 6 months</div>
  <div class="plain h2" style="margin-bottom:10px">The results, in three numbers</div>
  <div class="statgrid">
    <div><div class="num">92%</div><div class="lab">of companies kept the four-day week after the trial</div></div>
    <div><div class="num">71%</div><div class="lab">of employees reported lower burnout</div></div>
    <div><div class="num">57%</div><div class="lab">fall in staff attrition versus before</div></div>
  </div></div><div class="src">Source: 4 Day Week Global — UK Pilot (2022–2023)</div>""",
"""<div class="pad center">
  <div class="pullquote">"Revenue held steady, people were healthier, and almost no one wanted to go back.<span class="by">— Findings across the 4 Day Week Global UK pilot</span></div></div>""",
"""<div class="pad">
  <div class="eyebrow">Why it works</div>
  <div class="plain h2">Less time forces better time</div>
  <div class="rule"></div>
  <div class="biglist">
    <div class="row"><div class="k">01</div><div class="v">Meetings get cut, not work<small>Teams drop low-value meetings and status rituals first.</small></div></div>
    <div class="row"><div class="k">02</div><div class="v">Focus replaces presence<small>Output is measured by results, not hours at a desk.</small></div></div>
    <div class="row"><div class="k">03</div><div class="v">Recovery compounds<small>A real third rest day lifts energy and retention all week.</small></div></div>
  </div></div>""",
"""<div class="pad">
  <div class="eyebrow">How to pilot it</div>
  <div class="plain h2">A safe path to four days</div>
  <div class="rule"></div>
  <div class="timeline">
    <div class="step"><div class="dot"></div><div class="line"></div><div class="k">Define</div><div class="v">Pick 3–4 success metrics: output, quality, wellbeing, retention.</div></div>
    <div class="step"><div class="dot"></div><div class="line"></div><div class="k">Trial</div><div class="v">Run a 3-month pilot at 100% pay, 80% time, 100% output.</div></div>
    <div class="step"><div class="dot"></div><div class="line"></div><div class="k">Measure</div><div class="v">Compare against your baseline, not against hope.</div></div>
    <div class="step"><div class="dot"></div><div class="k">Decide</div><div class="v">Keep, tune, or revert — with data, not vibes.</div></div>
  </div></div>""",
"""<div class="pad">
  <div class="eyebrow">The honest objection</div>
  <div class="plain h2">"Won't output just drop?"</div>
  <div class="rule"></div>
  <div class="grid cols-2">
    <div class="feature"><h3>What skeptics expect</h3><p>20% less time means 20% less done, missed deadlines, unhappy clients.</p></div>
    <div class="feature alt"><h3>What the trials found</h3><p>Output held or rose; the lost day was mostly waste, not work.</p></div>
  </div></div>""",
"""<div class="pad center">
  <div class="eyebrow">Where to start</div>
  <div class="display h1">Don't mandate it. Prove it.</div>
  <div class="lead">Run one team, one quarter, one honest scorecard. Let the results make the argument.</div>
  <div class="rule"></div></div>""",
f"""{MOTIF}<div class="pad center">
  <div class="display h1">The week was never sacred.<br>Results are.</div>
  <div class="lead">Four days isn't about working less. It's about proving how little of the fifth day was ever work.</div>
  <div class="rule"></div>
  <div class="meta" style="margin-top:30px">Sources: 4 Day Week Global UK Pilot (2022–2023) · UKRI · Boston College</div></div>""",
]
for i, inner in enumerate(SLIDES, 1):
    (HERE / f"slide-{i:02d}.html").write_text(HEAD + inner + FOOT)
for extra in HERE.glob("slide-*.html"):
    if int(extra.stem.split("-")[1]) > len(SLIDES):
        extra.unlink()
print(f"wrote {len(SLIDES)} slides")
