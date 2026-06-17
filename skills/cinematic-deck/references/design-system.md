# Design system (assets/cinematic.css)

Copy `$DF/skills/cinematic-deck/assets/cinematic.css` into the deck's `assets/`. Each slide:
```html
<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="assets/cinematic.css"></head>
<body><div class="slide"><div class="pad center"> … </div></div></body></html>
```

## Consistency rules (this is what reads as "professional")
- **Never set font-size or margins inline.** Use scale classes only: `.hero .h1 .h2 .h3`, `.lead`,
  `.meta`, `.stat`, `.eyebrow`. Inline sizes are the #1 amateur tell ("some big, some small").
- **Gradient `.display` for big narrative moments** (hero, key statements, closing); **solid
  `.plain .h2` for content headers.** That split is the hierarchy — keep it consistent.
- Use `.pad.center` to vertically balance light-content slides (avoid top-heavy dead space).
- One drawn `MOTIF` (node-graph SVG) reused on hero/hook/closing for visual continuity.

## Theme & brand
- Default is dark. For **light**, add `light` to the slide: `<div class="slide light">`.
- Override brand colors per deck on the slide: `style="--primary:#1f7a5a;--accent:#e0922b"`
  (a Brand Kit profile supplies these). Keep ONE dominant + one accent.

## Fonts (rendered into the image = embedded; no viewer dependency)
- Default pairing is **Space Grotesk** (display) + **Inter** (body), loaded via `@import` in
  cinematic.css. The renderer waits for `document.fonts.ready`.
- **Brand / alt font:** add the font's Google Fonts `<link>` in the slide `<head>` and set
  `style="--display:'Fraunces',serif;--body:'Inter',sans-serif"` on the slide. Pick one display +
  one body; keep it consistent across the deck.

## Non-English / RTL
For non-Latin scripts, add `intl` to the slide and load the script's Noto font into the font vars:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
<div class="slide intl" style="--display:'Noto Sans Devanagari',sans-serif;--body:'Noto Sans Devanagari',sans-serif">
```
`intl` removes letter-spacing/uppercase (which break Devanagari/CJK matras & conjuncts). For RTL
(Arabic/Hebrew) also add `dir="rtl"` to the slide. Use the matching Noto family (Noto Sans JP /
SC / Arabic / Hebrew, etc.).

## Components
**Type:** `.eyebrow` (accent kicker) · `.display`(`.hero/.h1/.h2`, gradient) · `.plain`(solid) ·
`.lead` (use `<b>` to emphasize — never a bullet list) · `.meta` · `.rule` (gradient underline) ·
`.stat` (giant gradient number) · `.src` (bottom-right citation) · `.logo`.

**Instead of bullets, choose by intent:**
- `.grid .cols-2|3|4` of `.feature` (`.ic` SVG icon, `h3`, `p`) — parallel points. Use real
  monoline SVG icons (stroke=accent), never emoji. `.feature.alt` swaps the accent.
- `.deflist` (`.t` term / `.d` meaning) — term→definition content.
- `.biglist` (`.row` > `.k` number / `.v` statement with optional `<small>`) — a manifesto/argument.
- `.statgrid` (3× `.num`/`.lab`) — a wall of proof numbers (great for asset-poor topics).
- `.timeline` (`.step` > `.dot`/`.line`/`.k`/`.v`) — a process or roadmap.
- `.pullquote` (`.by`) — a full-slide editorial quote.
- `.chart` (`.col` > `.cbar`/`.clab`/`.csub`) — a simple gradient bar chart.
- `.dtable` (`<table>` with `<th>`/`<td>`) — an editorial data table for genuinely tabular /
  comparison data; add `class="hi"` to a cell to highlight a winner. First column is muted mono.

**Real assets:**
- `.card` — white frame for a light captured diagram/screenshot (`<img>` inside, max-height 560).
- `.codeimg` — a pre-rendered DARK code window (from `engine/code_image.py`); height-capped so it
  never overflows. Prefer this over pasting light code screenshots.
- `.bleed` + `.scrim` — a full-bleed generated/photographic image with a legibility scrim; put the
  `.pad` text on top. Use for hero/section beats when you have a strong image.

**Split layout:** `.split` (two columns, centered) for text + asset.

## Asset-poor topics
No source images is fine — lean on `.statgrid`, `.biglist`, `.timeline`, `.pullquote`, `.feature`
grids, `.chart`, and the motif. The `out/fourday_deck/` example is entirely asset-poor and still rich.
