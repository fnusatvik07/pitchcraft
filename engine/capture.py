#!/usr/bin/env python3
"""Capture real visual assets from a source web page for use in a deck.

Uses the bundled Chromium (Playwright) to pull what's actually on the page —
something the text-only research pass misses:

  * <img> elements (downloaded), filtered to meaningful sizes
  * large inline <svg> diagrams (element screenshots)
  * code blocks <pre>/<code> (crisp syntax-highlighted screenshots — great for dev decks)
  * a full-page screenshot (for reference / hero crops)

Writes everything to <outdir>/ and a manifest.json describing each asset
(path, kind, alt/caption, size) so the deck author can place them with intent.

Usage: python capture.py <url> <outdir> [--max-code 6] [--max-img 12]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

UA = {"User-Agent": "PitchCraft/visual (+deck asset capture)"}


def capture(url: str, outdir: Path, max_code=6, max_img=12) -> dict:
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"url": url, "assets": []}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=2)
        page.goto(url, wait_until="networkidle", timeout=45000)

        # full-page reference screenshot
        full = outdir / "page_full.png"
        page.screenshot(path=str(full), full_page=True)
        manifest["assets"].append({"kind": "page", "path": full.name})

        # meaningful <img> elements
        imgs = page.evaluate("""() => [...document.images]
          .filter(i => i.naturalWidth >= 200 && i.naturalHeight >= 120)
          .slice(0, 40)
          .map(i => ({src: i.currentSrc || i.src, alt: i.alt || '',
                      w: i.naturalWidth, h: i.naturalHeight}))""")
        seen = set()
        for n, im in enumerate(imgs):
            if not im["src"] or im["src"] in seen:
                continue
            seen.add(im["src"])
            if len([a for a in manifest["assets"] if a["kind"] == "img"]) >= max_img:
                break
            try:
                ext = ".png" if ".png" in im["src"].lower() else (".svg" if ".svg" in im["src"].lower() else ".jpg")
                dest = outdir / f"img_{n:02d}{ext}"
                if im["src"].startswith("data:"):
                    continue
                req = urllib.request.Request(im["src"], headers=UA)
                dest.write_bytes(urllib.request.urlopen(req, timeout=20).read())
                manifest["assets"].append({"kind": "img", "path": dest.name, "alt": im["alt"],
                                           "w": im["w"], "h": im["h"], "src": im["src"]})
            except Exception:
                pass

        # large inline SVG diagrams -> element screenshots
        svgs = page.query_selector_all("svg")
        nshot = 0
        for el in svgs:
            try:
                box = el.bounding_box()
                if not box or box["width"] < 280 or box["height"] < 160:
                    continue
                dest = outdir / f"svg_{nshot:02d}.png"
                el.screenshot(path=str(dest))
                manifest["assets"].append({"kind": "svg", "path": dest.name,
                                           "w": int(box["width"]), "h": int(box["height"])})
                nshot += 1
                if nshot >= 6:
                    break
            except Exception:
                pass

        # code blocks -> crisp screenshots (syntax-highlighted as rendered)
        blocks = page.query_selector_all("pre")
        ncode = 0
        for el in blocks:
            try:
                box = el.bounding_box()
                if not box or box["height"] < 40 or box["width"] < 200:
                    continue
                txt = (el.inner_text() or "").strip()
                dest = outdir / f"code_{ncode:02d}.png"
                el.screenshot(path=str(dest))
                manifest["assets"].append({"kind": "code", "path": dest.name,
                                           "preview": txt[:80], "lines": txt.count("\n") + 1,
                                           "w": int(box["width"]), "h": int(box["height"])})
                ncode += 1
                if ncode >= max_code:
                    break
            except Exception:
                pass

        browser.close()

    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main(argv):
    ap = argparse.ArgumentParser(description="Capture visual assets from a web page")
    ap.add_argument("url")
    ap.add_argument("outdir")
    ap.add_argument("--max-code", type=int, default=6)
    ap.add_argument("--max-img", type=int, default=12)
    a = ap.parse_args(argv[1:])
    m = capture(a.url, Path(a.outdir), a.max_code, a.max_img)
    kinds = {}
    for asset in m["assets"]:
        kinds[asset["kind"]] = kinds.get(asset["kind"], 0) + 1
    print(f"Captured from {a.url} -> {a.outdir}/")
    print("  " + ", ".join(f"{k}×{v}" for k, v in sorted(kinds.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
