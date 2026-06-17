# Changelog

All notable changes to PitchGraph are documented here. This project uses
[Semantic Versioning](https://semver.org).

## [1.0.0] 2026-06-17

First public release.

### Added
* Cinematic, story first deck generation from a topic or a URL, output as `.pptx` plus PDF.
* The `cinematic-deck` skill with progressive disclosure: a lean `SKILL.md` plus reference files
  for story and length, the design system, assets and imagery, and the pipeline.
* Design system (`cinematic.css`): locked type scale, dark and light themes, brand color and font
  overrides, embedded Google Fonts, and slop free components (feature cards, definition lists,
  stat grids, timelines, pull quotes, code windows, data tables).
* Asset capture from a source page: images, inline SVG diagrams, and code blocks.
* Generated architecture and flow diagrams from Mermaid, themed dark or light.
* Dark and light syntax highlighted code windows via Pygments.
* Slide count planner that derives length from source size or an explicit request.
* Guardrails: a linter for design rules and citations, an overflow checker, and an auto fit
  safety net so nothing ships clipped.
* Browser based visual QA, PDF and N up handout export.
* Editable companion deck with native, editable text for editing in PowerPoint.
* Non Latin script support (Devanagari, CJK, RTL) through an `intl` mode and Noto fonts.
* Optional AI hero images using your own image API key, with graceful fallback.
* A self contained example deck and a one command `setup.sh`.

[1.0.0]: https://github.com/fnusatvik07/pitchgraph/releases/tag/v1.0.0
