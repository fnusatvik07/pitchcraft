# Assets & imagery

## Capture from a source page (URL/doc)
```
py "$DF/engine/capture.py" <url> "$DF/out/<deck>/capture"
```
Pulls real `<img>` diagrams, screenshots large inline SVGs, captures code blocks as images, and a
full-page reference. Read `capture/manifest.json` and copy the assets worth featuring into the
deck's `assets/`. Real source diagrams/screenshots are the strongest visuals — prefer them.

Also run `deckforge-web-researcher` for cited facts/stats when the topic needs numbers; every
stat/chart slide must carry a `.src` citation.

## Dark code windows (don't paste light screenshots)
Re-render code text into a cohesive dark window:
```
py "$DF/engine/code_image.py" --code-file snippet.py --lang python --title graph.py \
   --out "$DF/out/<deck>/assets/code.png" --style one-dark
```
Transparent background + mac chrome + syntax highlight (Pygments). Place with `<img class="codeimg" …>`.

## Generated diagrams (architecture / flow / sequence)
When the topic needs a diagram and the source has none, generate one from Mermaid text — themed
to match (dark or light, accent colors), transparent PNG:
```
py "$DF/engine/diagram.py" --mmd-file flow.mmd --out "$DF/out/<deck>/assets/arch.png" \
   --theme <dark|light> --primary 7c5cff --accent 00e0b8
```
Supports flowchart / architecture / sequence / state diagrams. Place with `<img class="diagram" …>`
(height-capped, fills width). Keep diagrams to ~5–9 nodes so they read at slide scale.
(Note: the draw.io MCP opens an interactive editor and can't export headlessly — use this instead.)

## Light vs dark code windows
`code_image.py` defaults to a dark window; add `--light` for a light window (auto-uses an `xcode`
style) so technical LIGHT decks stay coherent. Match the code window theme to the slide theme.

## Optional AI image generation (user-configured, never required)
For hero/section beats with no real asset, you MAY generate one — but only if the user opted in:
- **Ask once during intake:** "Want AI-generated hero imagery for a richer look? It uses your own
  image API key (e.g. OpenAI). If not, I'll use drawn motifs and captured assets." Always deliver
  either way.
- **Configure the key:** set `OPENAI_API_KEY` in the env, or write a git-ignored
  `$DF/.deckforge.local.json` = `{"OPENAI_API_KEY":"sk-..."}`.
- **Generate:**
  `py "$DF/engine/gen_image.py" "<cinematic, on-topic prompt>" "$DF/out/<deck>/assets/hero.png"`
  Exits 3 with no key → just skip and fall back to motifs (the deck still ships).
- **Place full-bleed:** `<img class="bleed" src="assets/hero.png"><div class="scrim"></div>` then
  the `.pad` text. The scrim keeps text legible over the image.

Good prompts: abstract, on-theme, no text, cinematic lighting, matches the deck's accent palette.

## Licensing (hard rules)
Embed only: CC0 / CC-BY / public-domain media (with credit in `.src`), brand logos used
nominatively, source-page assets, your own generated images, or drawn motifs. Never scrape or
embed unlicensed stock. Free CC stock is usually off-topic — prefer captured assets + generated
imagery + drawn motifs over generic photos.
