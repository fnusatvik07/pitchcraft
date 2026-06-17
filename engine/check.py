#!/usr/bin/env python3
"""Automated pre-render QA for cinematic slide HTML — catches overflow before it
ships. Loads each slide-NN.html at 1920x1080 and flags anything past the canvas
(the #1 defect in generated decks). Exits non-zero if any slide overflows.

Usage: python check.py <html_dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

W, H = 1920, 1080
TOL = 4


def check(html_dir: str):
    from playwright.sync_api import sync_playwright
    slides = sorted(Path(html_dir).glob("slide-*.html")) or sorted(Path(html_dir).glob("*.html"))
    problems = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for hp in slides:
            pg.goto(hp.resolve().as_uri(), wait_until="load")
            pg.wait_for_timeout(80)
            res = pg.evaluate(f"""() => {{
              const W={W}, H={H}, TOL={TOL};
              const root = document.documentElement;
              const out = {{sw: root.scrollWidth, sh: root.scrollHeight, items: []}};
              for (const el of document.querySelectorAll('.pad *')) {{
                const r = el.getBoundingClientRect();
                if (r.width===0||r.height===0) continue;
                if (r.bottom > H+TOL || r.right > W+TOL || r.left < -TOL || r.top < -TOL) {{
                  const t = (el.textContent||'').trim().slice(0,40);
                  out.items.push({{tag: el.className||el.tagName, bottom: Math.round(r.bottom),
                                   right: Math.round(r.right), text: t}});
                }}
              }}
              return out;
            }}""")
            over_canvas = res["sw"] > W + TOL or res["sh"] > H + TOL
            # de-dupe to the worst few
            items = sorted(res["items"], key=lambda x: max(x["bottom"] - H, x["right"] - W), reverse=True)[:3]
            if over_canvas or items:
                problems.append((hp.name, res["sw"], res["sh"], items))
        b.close()

    if not problems:
        print(f"✓ {len(slides)} slides — no overflow.")
        return 0
    print(f"✗ {len(problems)}/{len(slides)} slides overflow the 1920x1080 canvas:")
    for name, sw, sh, items in problems:
        print(f"  {name}: scroll {sw}x{sh}")
        for it in items:
            print(f"      ↳ '{it['text']}' [{it['tag']}] bottom={it['bottom']} right={it['right']}")
    print("Fix: shorten text, reduce items, or split the slide; then re-render.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit(2)
    raise SystemExit(check(sys.argv[1]))
