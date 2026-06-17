# DeckForge

Turn a **topic or a URL** into a **visually stunning, story-first presentation** — not generic AI bullet slides.

DeckForge composes each slide for its moment in the story, captures the **real** diagrams / screenshots / code from a source page, generates architecture diagrams, themes dark / light / your brand, and self-checks for slop, missing citations, and overflow. It ships a polished `.pptx` + `PDF`, and an **editable companion** for when you need to tweak text in PowerPoint.

> Built as a Claude Code plugin. You drive it with `/deck <topic or url>`.

---

## Install (Claude Code)

```text
/plugin marketplace add fnusatvik07/deckforge
/plugin install deckforge
```

Then, once per machine, install the runtime:

```bash
bash "$(claude plugin path deckforge)/setup.sh"      # or: cd into the plugin dir && bash setup.sh
```

Use it:

```text
/deck https://docs.example.com/some-guide
/deck "the economics of solar power" --light
/deck "Q3 strategy" --slides 12
```

You get `out/<Deck>.pptx`, `out/<Deck>.pdf`, and (on request) `out/<Deck>_Editable.pptx`.

## Install (standalone / CLI)

```bash
git clone https://github.com/fnusatvik07/deckforge && cd deckforge
bash setup.sh
# render the bundled example to see the output:
.venv/bin/python engine/html_to_pptx.py examples/four-day-week out/Example.pptx
.venv/bin/python engine/export.py pdf out/Example.pptx
```

## Requirements

- **Python 3.11–3.13** (auto-detected; 3.14 is avoided — flaky for `lxml`/`python-pptx`)
- **Node 18+** (Mermaid diagrams + pdf.js QA render)
- **LibreOffice** (`soffice`) — `.pptx → PDF` (`brew install --cask libreoffice` / `apt install libreoffice`)
- **poppler** (`pdftoppm`) — QA / handout rasterize (`brew install poppler` / `apt install poppler-utils`)
- `setup.sh` creates a local `.venv`, installs Python deps, `playwright install chromium`, and the Node deps.

## How it works

```
topic / URL
   │  plan length (planner)         capture real assets (capture)        generate diagrams (diagram)
   ▼                                                                     dark code windows (code_image)
story spine ─▶ compose bespoke slide HTML  ─▶  GATE: lint + check  ─▶  render @2x (html_to_pptx)
   (design system: cinematic.css)            (no slop / overflow)         │
                                                                          ▼
                            browser QA (browser_qa) ─▶ export PDF/handout (export)
                                                       editable companion (html_to_editable)
```

- **Story-first, slop-free** — no dashed bullet lists; uses feature cards, definition lists,
  stat grids, timelines, pull-quotes, dark code windows, data tables, captured diagrams.
- **Real assets** — pulls a source page's images / SVG diagrams / code blocks; generates
  architecture/flow diagrams from Mermaid; optional AI hero images (your own API key).
- **Themes** — dark (default), light, or a brand palette/font (set `--primary`/`--accent` + a font).
- **Guardrails** — `lint` (rules + citations), `check` (overflow), auto-fit safety net.
- **Output** — slides are designed images in the `.pptx` for max fidelity; the editable companion
  is native text for editing. Multilingual (Devanagari/CJK/RTL via `intl` + Noto).

See `skills/cinematic-deck/SKILL.md` and `skills/cinematic-deck/references/` for the full method.

## Repo layout

```
skills/cinematic-deck/   the skill: SKILL.md, references/, assets/cinematic.css (design system)
engine/                  the pipeline (Python + a small Node workspace)
  ├─ capture, planner, code_image, diagram, html_to_pptx, check, lint, gen_image, html_to_editable
  ├─ browser_qa, export
  ├─ native/             native python-pptx engine for the editable companion
  └─ node/               Mermaid + pdf.js (installed by setup.sh)
themes/                  theme tokens (corporate / pitch / academic / creative)
examples/four-day-week/  a complete, self-contained example deck
commands/deck.md         the /deck command
```

## Notes & limits

- Slides in the cinematic `.pptx` are rendered images (that's what enables the visual quality) —
  edit the slide HTML and re-render, or use the editable companion for text edits.
- The capture tool downloads a source page's media. Only use sources you have the right to use;
  for redistribution, prefer your own assets, generated diagrams, or licensed/CC media.
- AI hero images are optional and require your own image API key (set `OPENAI_API_KEY` or
  `.deckforge.local.json`); without it, decks use drawn motifs and captured/generated assets.

## License

MIT © Satvik — see [LICENSE](LICENSE).
