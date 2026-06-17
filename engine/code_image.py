#!/usr/bin/env python3
"""Render source code into a crisp DARK code-window image (cohesive on dark decks).

Beats pasting a light screenshot from the source: consistent theme, transparent
margins, retina. Uses Pygments for syntax highlighting + Playwright for the shot.

Usage:
  python code_image.py --lang python --title graph.py --out out/x.png  < code.txt
  python code_image.py --code-file snippet.py --lang python --out out/x.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer


def render(code: str, lang: str | None, title: str, out: str, style: str = "one-dark", width: int = 1000, light: bool = False):
    if light and style == "one-dark":
        style = "xcode"  # sensible light default
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except Exception:
        lexer = get_lexer_by_name("text")
    try:
        fmt = HtmlFormatter(noclasses=True, style=style)
    except Exception:
        fmt = HtmlFormatter(noclasses=True, style="monokai")
    body = highlight(code, lexer, fmt)
    win_bg = "#ffffff" if light else "#0d1117"
    bar_bg = "#eef1f7" if light else "#161b22"
    fn_col = "#8a93a6" if light else "#8b949e"
    border = "rgba(20,30,60,.10)" if light else "rgba(255,255,255,.08)"
    bar_border = "rgba(20,30,60,.08)" if light else "rgba(255,255,255,.06)"
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
      *{{margin:0;padding:0;box-sizing:border-box}}
      body{{background:transparent;padding:40px}}
      .win{{width:{width}px;border-radius:16px;overflow:hidden;background:{win_bg};
            box-shadow:0 44px 110px rgba(0,0,0,{'.18' if light else '.6'});border:1px solid {border}}}
      .bar{{height:50px;background:{bar_bg};display:flex;align-items:center;gap:9px;padding:0 22px;border-bottom:1px solid {bar_border}}}
      .bar i{{width:13px;height:13px;border-radius:50%;display:inline-block}}
      .r{{background:#ff5f57}}.y{{background:#febc2e}}.g{{background:#28c840}}
      .fn{{margin-left:12px;color:{fn_col};font-size:20px;font-family:ui-monospace,Menlo,monospace}}
      .code{{padding:26px 30px}}
      .code pre{{margin:0;background:transparent!important;font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:25px;line-height:1.55}}
      .code pre span{{background:transparent!important}}
    </style></head><body>
      <div class="win"><div class="bar"><i class="r"></i><i class="y"></i><i class="g"></i><span class="fn">{title}</span></div>
      <div class="code">{body}</div></div></body></html>"""

    from playwright.sync_api import sync_playwright
    out_p = Path(out); out_p.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_p.with_suffix(".html")
    tmp.write_text(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(device_scale_factor=2)
        pg.goto(tmp.resolve().as_uri(), wait_until="load")
        pg.locator(".win").screenshot(path=str(out_p), omit_background=True)
        b.close()
    tmp.unlink(missing_ok=True)
    return out_p


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--code-file"); ap.add_argument("--lang", default="python")
    ap.add_argument("--title", default="code"); ap.add_argument("--out", required=True)
    ap.add_argument("--style", default="one-dark"); ap.add_argument("--width", type=int, default=1000)
    ap.add_argument("--light", action="store_true")
    a = ap.parse_args(argv[1:])
    code = Path(a.code_file).read_text() if a.code_file else sys.stdin.read()
    out = render(code, a.lang, a.title, a.out, a.style, a.width, a.light)
    print(f"Rendered code image: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
