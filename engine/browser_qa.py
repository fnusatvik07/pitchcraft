#!/usr/bin/env python3
"""PitchGraph browser-based QA — render a deck with Playwright (headless Chromium).

Two render paths:
  * .pptx  -> LibreOffice converts to PDF (conversion only), then pdf.js renders each
             page to a canvas *inside Chromium* and Playwright screenshots it.
  * .html  -> each slide HTML is loaded and screenshotted directly (perfect fidelity).

Outputs per-slide PNGs + a contact_sheet.png. The pitchgraph-browser-qa agent then
reads the images and prescribes fixes. Falls back to pdftoppm if Playwright is absent.

Usage:
    python browser_qa.py <deck.pptx|deck.html|dir-of-html> [out_dir]
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDFJS = HERE / "node" / "node_modules" / "pdfjs-dist" / "build"


def _soffice() -> str | None:
    return shutil.which("soffice") or (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if Path("/Applications/LibreOffice.app/Contents/MacOS/soffice").exists() else None
    )


def pptx_to_pdf(pptx: Path, out: Path) -> Path | None:
    so = _soffice()
    if not so:
        return None
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([so, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(pptx)],
                   check=True, capture_output=True)
    pdf = out / (pptx.stem + ".pdf")
    return pdf if pdf.exists() else None


def render_pdf_browser(pdf: Path, out: Path, scale: float = 1.6) -> list[Path]:
    """Render every PDF page to PNG using pdf.js inside Chromium via Playwright.

    Serves the harness + pdf.js + the PDF over a tiny local HTTP server so the ES
    module imports resolve (file:// module imports are blocked by Chromium CORS).
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return []
    if not (PDFJS / "pdf.min.mjs").exists():
        return []

    import http.server
    import socketserver
    import threading
    import tempfile

    out.mkdir(parents=True, exist_ok=True)
    serve = Path(tempfile.mkdtemp(prefix="dfqa_"))
    shutil.copy(PDFJS / "pdf.min.mjs", serve / "pdf.min.mjs")
    shutil.copy(PDFJS / "pdf.worker.min.mjs", serve / "pdf.worker.min.mjs")
    shutil.copy(pdf, serve / "doc.pdf")
    (serve / "harness.html").write_text("""<!doctype html><html><body><canvas id="c"></canvas>
    <script type="module">
      import * as pdfjs from "./pdf.min.mjs";
      pdfjs.GlobalWorkerOptions.workerSrc = "./pdf.worker.min.mjs";
      let _pdf = null;
      window.__load = async () => {
        _pdf = await pdfjs.getDocument("./doc.pdf").promise;
        return _pdf.numPages;
      };
      window.__render = async (n, scale) => {
        const page = await _pdf.getPage(n);
        const vp = page.getViewport({scale});
        const c = document.getElementById('c'); c.width=vp.width; c.height=vp.height;
        await page.render({canvasContext: c.getContext('2d'), viewport: vp}).promise;
        return [vp.width, vp.height];
      };
      window.__ready = true;
    </script></body></html>""")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(serve), **k)
        def log_message(self, *a):
            pass

    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    pngs: list[Path] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}/harness.html")
            page.wait_for_function("window.__ready === true", timeout=15000)
            num = page.evaluate("() => window.__load()")
            for n in range(1, int(num) + 1):
                page.evaluate("([n,s]) => window.__render(n,s)", [n, scale])
                w, h = page.evaluate("[document.getElementById('c').width, document.getElementById('c').height]")
                page.set_viewport_size({"width": int(w), "height": int(h)})
                dest = out / f"slide-{n:02d}.png"
                page.locator("#c").screenshot(path=str(dest))
                pngs.append(dest)
            browser.close()
    finally:
        httpd.shutdown()
        shutil.rmtree(serve, ignore_errors=True)
    return pngs


def render_html_browser(html_paths: list[Path], out: Path) -> list[Path]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return []
    out.mkdir(parents=True, exist_ok=True)
    pngs = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for i, hp in enumerate(html_paths, 1):
            page.goto(hp.resolve().as_uri())
            dest = out / f"slide-{i:02d}.png"
            page.screenshot(path=str(dest))
            pngs.append(dest)
        browser.close()
    return pngs


def contact_sheet(pngs: list[Path], dest: Path, cols: int = 3):
    if not pngs:
        return
    from PIL import Image
    thumbs = [Image.open(p).convert("RGB") for p in pngs]
    tw = 540
    rows = (len(thumbs) + cols - 1) // cols
    th = max(int(t.height * tw / t.width) for t in thumbs)
    pad = 10
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * th + (rows + 1) * pad), (232, 232, 232))
    for i, t in enumerate(thumbs):
        t = t.resize((tw, int(t.height * tw / t.width)))
        r, c = divmod(i, cols)
        sheet.paste(t, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save(dest)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = Path(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else src.with_suffix("").parent / (src.stem + "_qa")
    out.mkdir(parents=True, exist_ok=True)

    if src.is_dir():
        pngs = render_html_browser(sorted(src.glob("*.html")), out)
        mode = "browser/html"
    elif src.suffix == ".html":
        pngs = render_html_browser([src], out)
        mode = "browser/html"
    else:  # pptx
        pdf = pptx_to_pdf(src, out)
        if not pdf:
            print("ERROR: could not convert .pptx to PDF (is LibreOffice installed?)")
            return 1
        pngs = render_pdf_browser(pdf, out)
        mode = "browser/pdf.js"
        if not pngs:  # fallback to poppler
            subprocess.run(["pdftoppm", "-png", "-r", "130", str(pdf), str(out / "slide")],
                           check=True, capture_output=True)
            pngs = sorted(out.glob("slide*.png"))
            mode = "fallback/pdftoppm"

    if not pngs:
        print("ERROR: no slides rendered.")
        return 1
    contact_sheet(pngs, out / "contact_sheet.png")
    print(f"QA render [{mode}]: {len(pngs)} slides -> {out}/")
    print(f"Contact sheet: {out / 'contact_sheet.png'}")
    print("-> pitchgraph-browser-qa agent: read the PNGs and inspect each slide.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
