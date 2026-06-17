"""Theme token loader for PitchGraph.

A *theme* is a pure-data JSON file in `themes/<name>.json`. This module loads it
into a typed `Theme` object that every layout function reads from. No colors,
fonts, or sizes are ever hardcoded in the engine -- they live only in the tokens,
so a new look is one JSON file and zero engine code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"  # repo_root/themes


def hex_to_rgb(value: str) -> RGBColor:
    """Accept 'RRGGBB' or '#RRGGBB' and return an RGBColor. Never pass '#'."""
    return RGBColor.from_string(value.lstrip("#").upper())


@dataclass
class Theme:
    name: str
    palette: dict
    fonts: dict
    type_scale: dict
    layout: dict
    chart_style: dict
    voice: str = ""
    image_treatment: str = "none"
    template: str | None = None
    raw: dict = field(default_factory=dict)

    # ---- palette accessors (return RGBColor) ----
    def color(self, key: str) -> RGBColor:
        return hex_to_rgb(self.palette[key])

    def hex(self, key: str) -> str:
        return self.palette[key].lstrip("#").upper()

    # ---- typography ----
    def font(self, role: str = "body") -> str:
        return self.fonts.get(role, self.fonts["body"])

    def size(self, role: str) -> Pt:
        return Pt(self.type_scale[role])

    # ---- layout metrics (inches) ----
    @property
    def margin(self) -> float:
        return self.layout.get("margin_in", 0.6)

    @property
    def gutter(self) -> float:
        return self.layout.get("gutter_in", 0.3)

    def m(self) -> Inches:
        return Inches(self.margin)

    # ---- chart series colors (list of RGBColor) ----
    def series_colors(self) -> list[RGBColor]:
        return [hex_to_rgb(self.palette[k]) for k in self.chart_style.get("series", ["primary"])]

    @classmethod
    def load(cls, name: str, themes_dir: Path | None = None) -> "Theme":
        base = themes_dir or THEMES_DIR
        path = base / f"{name}.json"
        if not path.exists():
            available = ", ".join(sorted(p.stem for p in base.glob("*.json"))) or "(none)"
            raise FileNotFoundError(f"Theme '{name}' not found in {base}. Available: {available}")
        data = json.loads(path.read_text())
        return cls(
            name=data.get("name", name),
            palette=data["palette"],
            fonts=data["fonts"],
            type_scale=data["type_scale"],
            layout=data.get("layout", {}),
            chart_style=data.get("chart_style", {}),
            voice=data.get("voice", ""),
            image_treatment=data.get("image_treatment", "none"),
            template=data.get("template"),
            raw=data,
        )
