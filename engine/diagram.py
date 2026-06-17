#!/usr/bin/env python3
"""Generate architecture / flow / sequence diagrams from Mermaid text — themed to
match the deck (dark or light, accent colors) — as transparent PNGs to embed.

This is the "create diagrams" capability: the deck author writes a small Mermaid
spec (flowchart, architecture, sequence, etc.); this renders it via Mermaid.js in
Chromium and screenshots it with a transparent background.

Usage:
  python diagram.py --mmd-file flow.mmd --out out/x.png --theme dark [--primary 7c5cff --accent 00e0b8]
  echo 'flowchart LR; A-->B' | python diagram.py --out out/x.png --theme light
"""
from __future__ import annotations

import argparse
import http.server
import shutil
import socketserver
import sys
import tempfile
import threading
from pathlib import Path

MERMAID = Path(__file__).resolve().parent / "node" / "node_modules" / "mermaid" / "dist" / "mermaid.min.js"


def render(defn: str, out: str, theme: str = "dark", primary="7c5cff", accent="00e0b8", scale=2.0):
    if not MERMAID.exists():
        raise SystemExit("mermaid not installed (npm i mermaid in engine/node).")
    dark = theme != "light"
    node_fill = "#161d38" if dark else "#ffffff"
    text = "#f6f8ff" if dark else "#121829"
    line = "rgba(160,170,210,.6)" if dark else "#9aa3c6"
    sec = "#1f274a" if dark else "#eef1f9"
    tvars = {
        "background": "transparent",
        "primaryColor": node_fill, "primaryTextColor": text,
        "primaryBorderColor": f"#{accent}", "lineColor": line,
        "secondaryColor": sec, "secondaryBorderColor": f"#{primary}", "secondaryTextColor": text,
        "tertiaryColor": node_fill, "tertiaryBorderColor": f"#{primary}", "tertiaryTextColor": text,
        "fontFamily": "Helvetica Neue, Arial, sans-serif", "fontSize": "22px",
        "clusterBkg": sec, "clusterBorder": f"#{primary}",
    }
    tv = ",".join(f'"{k}":"{v}"' for k, v in tvars.items())
    serve = Path(tempfile.mkdtemp(prefix="dfdiag_"))
    shutil.copy(MERMAID, serve / "mermaid.min.js")
    (serve / "index.html").write_text(f"""<!doctype html><html><head><meta charset="utf-8">
      <script src="./mermaid.min.js"></script>
      <style>*{{margin:0;padding:0}}body{{background:transparent}}
        #wrap{{display:inline-block;padding:30px}} .mermaid{{background:transparent!important}}
        #wrap svg{{width:1640px!important;max-width:none!important;height:auto!important}}</style></head>
      <body><div id="wrap"><pre class="mermaid" id="d">{defn}</pre></div>
      <script>
        mermaid.initialize({{startOnLoad:false, securityLevel:'loose', theme:'base',
          themeVariables:{{{tv}}}, flowchart:{{curve:'basis', htmlLabels:true, padding:18}}}});
        window.__done=false;
        mermaid.run({{nodes:[document.getElementById('d')]}}).then(()=>{{window.__done=true;}});
      </script></body></html>""")

    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), lambda *a, **k:
        http.server.SimpleHTTPRequestHandler(*a, directory=str(serve), **k))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    out_p = Path(out); out_p.parent.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(device_scale_factor=scale)
            pg.goto(f"http://127.0.0.1:{port}/index.html", wait_until="load")
            pg.wait_for_function("window.__done === true", timeout=20000)
            pg.wait_for_selector("#wrap svg", timeout=20000)
            pg.locator("#wrap").screenshot(path=str(out_p), omit_background=True)
            b.close()
    finally:
        httpd.shutdown(); shutil.rmtree(serve, ignore_errors=True)
    return out_p


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mmd-file"); ap.add_argument("--out", required=True)
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    ap.add_argument("--primary", default="7c5cff"); ap.add_argument("--accent", default="00e0b8")
    a = ap.parse_args(argv[1:])
    defn = Path(a.mmd_file).read_text() if a.mmd_file else sys.stdin.read()
    out = render(defn, a.out, a.theme, a.primary, a.accent)
    print(f"Rendered diagram: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
