#!/usr/bin/env python3
"""Decide how many slides a deck should have — and the story skeleton to fill.

The count is never arbitrary. It's derived from: an explicit user request (wins),
the depth mode, and how much real source content there is. Short topic -> tight
deck; long doc -> more, but capped so it stays a *talk*, not a wall.

Heuristic:
  explicit N           -> use it (clamp 5..30)
  else content_slides  = clamp(round(source_words / 180), depth.min, depth.max)
                         (no source -> depth.base content slides)
  framing              = title + closing + 1 section divider per ~4 content slides
                         + agenda when content_slides >= 7
  total                = content + framing

Usage:
  python planner.py --mode standard [--words 2600] [--explicit 12] [--source-file page.txt]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEPTH = {  # content-slide envelope per depth
    "quick":    {"base": 5,  "min": 4,  "max": 7},
    "standard": {"base": 8,  "min": 6,  "max": 12},
    "deep":     {"base": 12, "min": 9,  "max": 18},
}


def plan(words: int | None = None, mode: str = "standard", explicit: int | None = None):
    d = DEPTH.get(mode, DEPTH["standard"])
    if explicit:
        total = max(5, min(30, explicit))
        content = max(3, total - 3)
        rationale = f"User asked for {explicit} slides."
    else:
        if words:
            content = max(d["min"], min(d["max"], round(words / 180)))
            rationale = f"{words} words of source ÷ ~180 words/slide → {content} content slides ({mode}, capped {d['min']}–{d['max']})."
        else:
            content = d["base"]
            rationale = f"No source text; {mode} default of {content} content slides."
        sections = max(0, content // 4)
        agenda = 1 if content >= 7 else 0
        total = content + 2 + sections + agenda  # title + closing + sections + agenda

    # build a story skeleton of EXACTLY `total` beats (problem -> fix -> develop -> proof -> payoff)
    skeleton = ["title (hero)"]
    if total >= 9:
        skeleton.append("agenda")
    open_beats = ["hook: the problem", "the turn: the fix", "what it unlocks (cards)"]
    close_beats = ["proof: a number or chart", "recap: what to remember", "closing (payoff)"]
    remaining = total - len(skeleton) - len(open_beats) - len(close_beats)
    develop = [f"develop key point {i + 1}" for i in range(max(0, remaining))]
    skeleton += open_beats + develop + close_beats
    skeleton = skeleton[:total]
    # if we trimmed, make sure it still ends on the payoff
    if skeleton[-1] != "closing (payoff)":
        skeleton[-1] = "closing (payoff)"

    return {"mode": mode, "recommended": total, "content_slides": total - (skeleton.count("agenda") + 2),
            "rationale": rationale, "skeleton": skeleton}


def main(argv):
    ap = argparse.ArgumentParser(description="Plan slide count + story skeleton")
    ap.add_argument("--mode", default="standard", choices=list(DEPTH))
    ap.add_argument("--words", type=int)
    ap.add_argument("--explicit", type=int)
    ap.add_argument("--source-file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv[1:])
    words = a.words
    if a.source_file and Path(a.source_file).exists():
        words = len(Path(a.source_file).read_text().split())
    p = plan(words, a.mode, a.explicit)
    if a.json:
        print(json.dumps(p, indent=2)); return 0
    print(f"Recommended: {p['recommended']} slides ({p['mode']})")
    print(f"Why: {p['rationale']}")
    print("Skeleton:")
    for i, b in enumerate(p["skeleton"], 1):
        print(f"  {i:>2}. {b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
