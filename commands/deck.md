---
description: Build a cinematic, story-first deck (.pptx + PDF) from a topic or a URL.
argument-hint: <topic or URL> [--light] [--slides N]
---

# /deck — build a cinematic presentation

Input: **$ARGUMENTS**

Use the **cinematic-deck** skill. `$DF` = `${CLAUDE_PLUGIN_ROOT}`.

1. **Setup once:** if `$DF/.venv` is missing, run `bash "$DF/setup.sh"`.
2. Follow the skill's workflow (read `$DF/skills/cinematic-deck/SKILL.md` and its references):
   intake → plan length (`engine/planner.py`) → capture assets if a URL (`engine/capture.py`) →
   write the story spine → compose bespoke slide HTML in `$DF/out/<deck>/` using the design
   system → **gate** (`engine/lint.py` + `engine/check.py`) → render (`engine/html_to_pptx.py`) →
   browser QA (`engine/browser_qa.py`) → export PDF (`engine/export.py`) → optional editable
   companion (`engine/html_to_editable.py`).
3. **Deliver** the `.pptx` + `.pdf` (and `_Editable.pptx` if asked), and report what was built.

Honor flags in the input: `--light` (light theme), `--slides N` (force count), a brand color or
font if the user gives one. If the user provides an image API key, offer generated hero imagery
(`engine/gen_image.py`); otherwise use drawn motifs + captured/generated assets.
