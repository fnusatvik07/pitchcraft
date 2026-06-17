# Story & length

## How many slides? (never guess — derive it)
Run the planner; it turns input into a count + a beat skeleton:
```
py "$DF/engine/planner.py" --mode <quick|standard|deep> [--explicit N] [--words W | --source-file page.txt]
```
Logic:
- **Explicit request wins** — if the user says "10 slides", use it (clamped 5–30).
- **From a source** (URL/doc): `content = clamp(round(words / 180), depth.min, depth.max)`.
  180 words ≈ one well-designed slide. Envelopes: quick 4–7, standard 6–12, deep 9–18.
- **Topic only** (no source): the depth's base (quick 5 / standard 8 / deep 12 content slides).
- **Framing** added on top: title + closing, one section divider per ~4 content slides, and an
  agenda when total ≥ 9. The planner returns an exact skeleton of that length.

Rules of thumb: a 1-line topic → ~9–11; a long docs page → 14–18 (cap it, it's a talk not a wall);
"quick/teaser" → 6–8; "deep dive/workshop" → 16+.

## The narrative arc (fill the skeleton)
Always tell a story, not a table of contents:
1. **Hero** — title, set the frame.
2. **Hook** — the problem/tension ("Your agent is brilliant. And amnesiac.").
3. **The turn** — the fix, stated plainly.
4. **What it unlocks** — the payoff up front (cards).
5. **Develop** — how it works, 1 idea per slide, alternating treatments (diagram → code → stat).
6. **Proof** — a real number, chart, or quote.
7. **Objection / nuance** — address the obvious doubt honestly.
8. **Use it** — the concrete next step.
9. **Payoff** — a closing line that lands the thesis (not "Thank you").

Headlines: write the *claim*, not the *category*. "A dial from fast to bulletproof" beats
"Durability modes". One idea per slide; if two ideas appear, split it.

## Rhythm
Alternate slide types so no two adjacent slides look the same: statement → cards → showcase →
stat → split → chart → quote. Section dividers reset attention before a new act.
