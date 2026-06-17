#!/usr/bin/env python3
"""Optional AI hero-image generation for cinematic decks.

OFF by default. The skill ASKS the user whether they want generated imagery; if
yes, it uses their API key. With no key the whole feature is skipped and the deck
still renders (drawn motifs / captured assets).

Key resolution order: --key arg  ->  $OPENAI_API_KEY  ->  pitchcraft/.pitchcraft.local.json
{"OPENAI_API_KEY": "sk-..."}.  Returns exit code 3 when no key (caller falls back).

Usage:
  python gen_image.py "a cinematic abstract visualization of …" out/img/hero.png [--size 1792x1024]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def resolve_key(cli_key=None):
    if cli_key:
        return cli_key
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    cfg = ROOT / ".pitchcraft.local.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text()).get("OPENAI_API_KEY")
        except Exception:
            return None
    return None


def generate(prompt, out_path, size="1792x1024", model="gpt-image-1", key=None):
    key = resolve_key(key)
    if not key:
        return None  # signal: no key -> caller falls back
    body = json.dumps({"model": model, "prompt": prompt, "size": size, "n": 1}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    item = resp["data"][0]
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if item.get("b64_json"):
        out.write_bytes(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        out.write_bytes(urllib.request.urlopen(item["url"], timeout=120).read())
    else:
        return None
    return out


def main(argv):
    ap = argparse.ArgumentParser(description="Optional AI hero-image generation")
    ap.add_argument("prompt")
    ap.add_argument("out")
    ap.add_argument("--size", default="1792x1024")
    ap.add_argument("--model", default="gpt-image-1")
    ap.add_argument("--key")
    a = ap.parse_args(argv[1:])
    if not resolve_key(a.key):
        print("NO_KEY — image generation skipped (deck will use drawn motifs / captured assets).")
        return 3
    try:
        out = generate(a.prompt, a.out, a.size, a.model, a.key)
        if out:
            print(f"Generated {out}")
            return 0
        print("Generation returned no image; falling back.")
        return 1
    except Exception as e:
        print(f"Image generation failed ({e}); falling back to default visuals.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
