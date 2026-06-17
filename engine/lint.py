#!/usr/bin/env python3
"""Design-rule linter for cinematic slide HTML — the consistency guardrail.

Enforces the rules that keep unattended runs from drifting into slop:
  ERROR  inline font-size            (use the scale classes, not px)
  ERROR  <ul>/<ol>/<li> bullet lists (use feature/deflist/biglist instead)
  ERROR  raw inline color/background hex (use theme vars / classes)
  WARN   emoji used as an icon       (use monoline SVG icons)
  WARN   stat/chart/statgrid slide with no .src citation
  WARN   slide with no heading       (.display or .plain)

Exits non-zero if any ERROR. Run BEFORE rendering (with check.py).

Usage: python lint.py <html_dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# pictographic emoji only — NOT typographic arrows (→ ↔) which are legitimate
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F900-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF]")
INLINE_FONTSIZE = re.compile(r'style="[^"]*font-size', re.I)
BULLET_TAG = re.compile(r"<(ul|ol|li)\b", re.I)
INLINE_HEX = re.compile(r'style="[^"]*(?:^|;|\s)(?:color|background(?:-color)?)\s*:\s*#', re.I)


def lint_file(path: Path):
    html = path.read_text()
    errors, warns = [], []
    if INLINE_FONTSIZE.search(html):
        errors.append("inline font-size (use scale classes: .hero/.h1/.h2/.lead/.meta/.stat)")
    if BULLET_TAG.search(html):
        errors.append("bullet list tag <ul>/<ol>/<li> (use .feature / .deflist / .biglist)")
    if INLINE_HEX.search(html):
        errors.append("raw inline color/background hex (use theme vars / classes)")
    em = EMOJI.findall(html)
    if em:
        warns.append(f"emoji used ({''.join(em[:6])}) — prefer monoline SVG icons")
    needs_src = any(c in html for c in ('class="stat"', 'class="chart"', 'class="statgrid"', "statgrid"))
    if needs_src and 'class="src"' not in html:
        warns.append("data/stat slide without a .src citation")
    if "display" not in html and "plain" not in html and "stat" not in html and "pullquote" not in html:
        warns.append("no heading (.display/.plain) on the slide")
    return errors, warns


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    d = Path(argv[1])
    slides = sorted(d.glob("slide-*.html")) or sorted(d.glob("*.html"))
    n_err = n_warn = 0
    for s in slides:
        errs, warns = lint_file(s)
        if errs or warns:
            print(f"{s.name}:")
            for e in errs:
                print(f"  ✗ ERROR  {e}"); n_err += 1
            for w in warns:
                print(f"  ⚠ warn   {w}"); n_warn += 1
    if not n_err and not n_warn:
        print(f"✓ {len(slides)} slides — clean (no slop, consistent).")
    else:
        print(f"\n{n_err} error(s), {n_warn} warning(s) across {len(slides)} slides.")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
