#!/usr/bin/env python3
"""Editable companion: cinematic slide HTML -> a fully EDITABLE native .pptx.

The cinematic deck is image slides (max visual quality). This produces a parallel
deck with real, editable text boxes/tables for buyers who must edit in PowerPoint.
It extracts each slide's structured content and renders it through the native
python-pptx engine (native engine) — plainer, but every word is editable.

Usage: python html_to_editable.py <html_dir> <out.pptx> [--theme pitch|corporate|academic|creative]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent


def _txt(el):
    return el.get_text(" ", strip=True) if el else None


def heading(slide):
    for sel in (".display", ".plain"):
        el = slide.select_one(sel)
        if el:
            return _txt(el)
    return None


def slide_to_item(slide, idx, total, assets_dir: Path):
    light = "light" in (slide.get("class") or [])
    eyebrow = _txt(slide.select_one(".eyebrow"))
    head = heading(slide)
    lead = _txt(slide.select_one(".lead"))
    sources = [_txt(m) for m in slide.select(".meta")] or ([_txt(slide.select_one(".src"))] if slide.select_one(".src") else [])
    src_caption = _txt(slide.select_one(".src"))

    def img_abs(el):
        src = el.get("src")
        if not src:
            return None
        p = (assets_dir.parent / src) if not src.startswith("/") else Path(src)
        return str(p.resolve())

    # 1. title / closing framing
    if idx == 0:
        return {"layout": "title", "kicker": eyebrow or "", "title": head or "Presentation", "subtitle": lead or ""}
    if idx == total - 1:
        srcs = []
        for m in slide.select(".meta"):
            srcs += [s.strip() for s in _txt(m).replace("·", "\n").split("\n") if s.strip()]
        return {"layout": "closing", "title": head or "Thank you", "subtitle": lead or "", "sources": srcs[:6]}

    # 2. single big stat
    st = slide.select_one(".stat")
    if st:
        return {"layout": "stat-callout", "stat": _txt(st), "label": lead or "",
                "source": {"text": src_caption.replace("Source:", "").strip()} if src_caption else None}

    # 3. pull-quote / quote
    pq = slide.select_one(".pullquote")
    if pq:
        by = _txt(pq.select_one(".by"))
        q = _txt(pq)
        if by:
            q = q.replace(by, "").strip()
        return {"layout": "quote", "quote": q.strip('"“”'), "attribution": (by or "").lstrip("—- ").strip()}

    # 4. data table -> comparison (2 cols) else flatten to bullets
    tbl = slide.select_one(".dtable")
    if tbl:
        rows = [[_txt(c) for c in tr.find_all(["th", "td"])] for tr in tbl.find_all("tr")]
        if rows:
            bullets = []
            hdr = rows[0]
            for r in rows[1:]:
                pairs = ", ".join(f"{hdr[i]}: {r[i]}" for i in range(1, len(r)) if i < len(hdr))
                bullets.append(f"{r[0]} — {pairs}")
            return {"layout": "content-image", "title": head or "Comparison", "bullets": bullets[:6], "image": None}

    # 5. structured lists -> content bullets
    bullets = []
    for f in slide.select(".feature"):
        h3 = _txt(f.select_one("h3")); p = _txt(f.select_one("p"))
        bullets.append(f"{h3} — {p}" if h3 and p else (h3 or p))
    if not bullets:
        ts = slide.select(".deflist .t"); ds = slide.select(".deflist .d")
        for t, d in zip(ts, ds):
            bullets.append(f"{_txt(t)} — {_txt(d)}")
    if not bullets:
        for row in slide.select(".biglist .row"):
            bullets.append(_txt(row.select_one(".v")))
    if not bullets:
        for s in slide.select(".timeline .step"):
            k = _txt(s.select_one(".k")); v = _txt(s.select_one(".v"))
            bullets.append(f"{k} — {v}" if k and v else (k or v))
    if not bullets:
        for g in slide.select(".statgrid > div"):
            n = _txt(g.select_one(".num")); l = _txt(g.select_one(".lab"))
            bullets.append(f"{n} — {l}" if n and l else (n or l))
    if bullets:
        item = {"layout": "content-image", "title": head or "", "bullets": [b for b in bullets if b][:6], "image": None}
        if src_caption:
            item["source"] = {"text": src_caption.replace("Source:", "").strip()}
        return item

    # 6. a captured/generated visual (diagram / code / image)
    vis = slide.select_one(".diagram, .codeimg, .card img, .bleed")
    if vis:
        return {"layout": "content-image", "title": head or "", "bullets": [lead] if lead else [],
                "image": {"path": img_abs(vis if vis.name == "img" else (vis.select_one("img") or vis))}}

    # 7. statement / section divider (just a big line)
    if head and not lead:
        return {"layout": "section", "title": head}
    return {"layout": "content-image", "title": head or "", "bullets": [lead] if lead else [], "image": None}


def build(html_dir: str, out_path: str, theme: str | None = None):
    d = Path(html_dir)
    slides = sorted(d.glob("slide-*.html")) or sorted(d.glob("*.html"))
    assets = d / "assets"
    light = False
    items = []
    for i, hp in enumerate(slides):
        soup = BeautifulSoup(hp.read_text(), "html.parser")
        sl = soup.select_one(".slide")
        if i == 0 and sl and "light" in (sl.get("class") or []):
            light = True
        items.append(slide_to_item(sl, i, len(slides), assets))
    if not theme:
        theme = "corporate" if light else "pitch"
    brief = {"topic": d.name, "theme": theme, "outline": items, "citations": []}
    brief_path = d / "_editable_brief.json"
    brief_path.write_text(json.dumps(brief, indent=2))
    # render via the native (editable) engine
    py = str(ROOT / ".venv" / "bin" / "python")
    subprocess.run([py, str(ROOT / "engine" / "native" / "build_deck.py"), str(brief_path), theme, out_path], check=True)
    return out_path, theme, len(items)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("html_dir"); ap.add_argument("out"); ap.add_argument("--theme")
    a = ap.parse_args(argv[1:])
    out, theme, n = build(a.html_dir, a.out, a.theme)
    print(f"Editable companion: {out} ({n} slides, theme '{theme}')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
