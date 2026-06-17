---
name: cinematic-deck
description: Build a visually stunning, story-first presentation from a topic or a URL/doc — dark or light editorial design, real diagrams/screenshots/code captured from the source, generated visuals, big type, no bullet-dash slop. Use when the user wants an impressive, non-generic deck ("make it beautiful / cinematic / a pitch / a keynote"). Produces a designed .pptx (image slides) + PDF.
license: MIT
metadata: {"emoji":"🎬","platforms":["macos","linux"],"requires":{"python":["python-pptx","playwright","pillow","pygments"],"bins":["soffice"]},"optional":{"env":["OPENAI_API_KEY"]},"tags":["pptx","powerpoint","cinematic","story","visual","keynote","pitch","deck"]}
---

# Cinematic Deck

Build a **story-first, visually striking** deck. Quality comes from composing each slide for its
moment from a slop-free design system, using real captured assets — never slotting content into
uniform bullet layouts. `$DF` = `${CLAUDE_PLUGIN_ROOT}`; py = `$DF/.venv/bin/python`.

## The four rules (non-negotiable)
1. **Story spine first** — a narrative arc (problem → fix → unlock → how → proof → payoff), one
   idea per slide. Headlines carry tension, not labels.
2. **Use real assets** — if given a URL/doc, capture and feature ITS diagrams, screenshots, code.
3. **No AI slop** — no dashed bullet lists, no "—" markers, no accent line under every title.
   Replace bullets with feature cards, definition lists, dark code windows, stat grids, timelines,
   pull-quotes, big statements.
4. **Consistency** — never set font-size/margins inline; use the scale classes only.

## Workflow (high level — load the linked reference for each step)
1. **Setup once:** `bash "$DF/setup.sh"`.
2. **Intake & imagery opt-in** — topic or URL/doc; ask audience, depth, and whether to use
   AI imagery (needs the user's key). → `references/assets-and-imagery.md`
3. **Plan length & story** — derive slide count and the beat skeleton; don't guess. →
   `references/story-and-length.md`
4. **Capture assets** (if URL/doc) and prepare code/images. → `references/assets-and-imagery.md`
5. **Compose bespoke slides** as `out/<deck>/slide-NN.html` using the component library. →
   `references/design-system.md`
6. **Validate, render, QA, export.** → `references/pipeline.md`

## References (read on demand — progressive disclosure)
- `references/story-and-length.md` — narrative arc + the slide-count formula (`engine/planner.py`).
- `references/design-system.md` — the cinematic.css component cheatsheet, consistency rules,
  light theme, and the asset-poor layouts (stat grid, timeline, pull-quote, manifesto).
- `references/assets-and-imagery.md` — capture from a page, dark code windows, optional AI image
  generation + key config, and licensing.
- `references/pipeline.md` — overflow auto-check, render→pptx, browser QA, PDF/handout export.

## Worked example
`$DF/examples/four-day-week/` is a complete, validated deck (light theme, asset-poor — built
entirely from the design system, no external images). Render it to see the output:
`"$DF/.venv/bin/python" "$DF/engine/html_to_pptx.py" "$DF/examples/four-day-week" "$DF/out/Example.pptx"`

## Note
Slides are designed images inside the `.pptx` (that's what enables the visual ceiling). To edit,
change the slide HTML and re-render (step 6) — not in PowerPoint. HTML sources are kept.
