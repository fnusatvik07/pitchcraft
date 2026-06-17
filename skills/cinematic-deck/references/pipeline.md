# Pipeline — validate, render, QA, export

After composing `out/<deck>/slide-NN.html` (with `assets/cinematic.css` + chosen assets copied in):

## 1. Gate: lint + overflow check (do this BEFORE rendering)
```
py "$DF/engine/lint.py"  "$DF/out/<deck>"   # design-rule consistency (no slop, citations)
py "$DF/engine/check.py" "$DF/out/<deck>"   # overflow at 1920x1080
```
**lint** enforces the rules so unattended runs stay consistent: no inline font-size, no `<ul>/<li>`
bullet lists, no raw inline hex, emoji→SVG, and a `.src` citation on every stat/chart slide. Fix
all ERRORs. **check** flags anything past the canvas; fix each (shorten, fewer items, cap an image
with `.codeimg`/`.card` max-height, or split the slide). The renderer also auto-fits as a safety
net, but fix overflow at the source — don't rely on shrink-to-fit.

## 2. Render + assemble to .pptx
```
py "$DF/engine/html_to_pptx.py" "$DF/out/<deck>" "$DF/out/Deck.pptx" [notes.json]
```
Renders each slide @2x via Chromium and assembles full-bleed, in filename order. `notes.json`
(`{"slide-01":"speaker note", …}`) injects speaker notes.

## 3. Browser QA (visual pass)
```
py "$DF/engine/browser_qa.py" "$DF/out/Deck.pptx" "$DF/out/qa"
```
Renders the .pptx via pdf.js in Chromium → per-slide PNGs + `contact_sheet.png`. **Read the
contact sheet, then the riskiest slides.** Check: hierarchy (one dominant title), contrast,
balance/dead-space, that every stat/chart has a citation, no leftover placeholder. Fix in the HTML
and re-render. The `check.py` step already guarantees no overflow.

## 4. Export deliverables
```
py "$DF/engine/export.py" pdf     "$DF/out/Deck.pptx"      # shareable PDF
py "$DF/engine/export.py" handout "$DF/out/Deck.pptx"      # N-up handout
```

## 5. Editable companion (optional — for buyers who must edit in PowerPoint)
The cinematic .pptx is image slides (max quality). Offer an editable native version too:
```
py "$DF/engine/html_to_editable.py" "$DF/out/<deck>" "$DF/out/Deck_Editable.pptx" [--theme pitch|corporate]
```
Extracts each slide's text/structure and rebuilds it with real, editable text boxes (diagrams/code
carried over as pictures). Plainer than the cinematic deck, but every word is editable. Deliver
both: `Deck.pptx` (present) + `Deck_Editable.pptx` (edit).

## Definition of done (ship checklist)
- [ ] `check.py` clean (no overflow on any slide).
- [ ] Reads as a story: a hook, development, a payoff line (not "Thank you").
- [ ] Consistent type (no inline sizes); one accent palette; one motif.
- [ ] Every stat/chart cited; claims traceable.
- [ ] At least one real/captured or generated visual beyond text per "show" beat.
- [ ] PDF exports cleanly; opens in PowerPoint/Keynote.
