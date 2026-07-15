#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from validation_common import emit, load_data

REQUIRED_MARKERS = {"matte_or_satin_silver_structural_base", "subtle_subordinate_gold_accents", "declared_70_85_15_30_allocation", "low_poly_faceted_geometry", "clean_edges_and_sharp_folds", "controlled_rim_light", "minimal_local_highlights_no_environment_reflection"}
REQUIRED_NEGATIVE_GROUPS = {"gloss", "reflection", "chrome", "liquid_metal", "jewelry", "gold_dominance", "baroque", "surface_noise", "colored_reflection", "style_mixing"}
POSITIVE_PATTERNS = (
    (re.compile(r"\b(?:matte|satin)\b.*\bsilver\b", re.I | re.S), "matte/satin silver base"),
    (re.compile(r"\b(?:subtle|controlled|subordinate)\b.*\bgold\b", re.I | re.S), "controlled gold accents"),
    (re.compile(r"\b(?:low[- ]?poly|faceted|planar)\b", re.I), "low-poly/faceted geometry"),
    (re.compile(r"\bclean edges?\b|\bsharp folds?\b", re.I), "clean edges/sharp folds"),
    (re.compile(r"\bcontrolled rim light\b", re.I), "controlled rim light"),
    (re.compile(r"\bminimal (?:local )?(?:highlights|reflections)\b", re.I), "minimal reflections"),
)
FORBIDDEN = {
    "glossy": re.compile(r"\bglossy\b", re.I),
    "mirror": re.compile(r"\bmirror(?:ed)?\b", re.I),
    "reflective surface": re.compile(r"\breflective surface\b", re.I),
    "chrome": re.compile(r"\bchrome\b", re.I),
    "liquid metal": re.compile(r"\bliquid metal\b", re.I),
    "jewelry": re.compile(r"\bjewel(?:ry|lery)\b", re.I),
    "baroque": re.compile(r"\bbaroque\b", re.I),
    "gold body": re.compile(r"\b(?:gold[- ]covered|gold body|full gold)\b", re.I),
    "grunge": re.compile(r"\bgrunge\b", re.I),
    "obsidian": re.compile(r"\b(?:obsidian|black[- ]gold dominance)\b", re.I),
}


def negated(text: str, start: int) -> bool:
    window = text[max(0, start - 48):start].casefold()
    return bool(re.search(r"\b(?:no|not|avoid|without)\b[^.;:]{0,40}$", window))


def validate(data: object, raw_text: str) -> list[str]:
    errors: list[str] = []
    if isinstance(data, dict) and "prompt_blocks" in data:
        markers = set(data.get("required_semantic_markers", []))
        negative = set(data.get("negative_semantic_groups", []))
        missing = REQUIRED_MARKERS - markers
        if missing:
            errors.append(f"missing semantic markers: {sorted(missing)}")
        missing_negative = REQUIRED_NEGATIVE_GROUPS - negative
        if missing_negative:
            errors.append(f"missing negative groups: {sorted(missing_negative)}")
        if data.get("background_profile") not in {"product-light", "showcase-neutral"}:
            errors.append("invalid or missing background profile")
        blocks = data.get("prompt_blocks", [])
        if len(blocks) != 10:
            errors.append("prompt must contain 10 ordered blocks")
        positive_text = "\n".join(str(block.get("content", "")) for block in blocks if isinstance(block, dict))
    else:
        positive_text = raw_text
        for pattern, label in POSITIVE_PATTERNS:
            if not pattern.search(positive_text):
                errors.append(f"missing positive meaning: {label}")
        if not re.search(r"\b(?:product-light|showcase-neutral)\b", positive_text):
            errors.append("missing selected background profile")
    normalized = re.sub(r"\s+", " ", positive_text)
    for label, pattern in FORBIDDEN.items():
        if any(not negated(normalized, match.start()) for match in pattern.finditer(normalized)):
            errors.append(f"forbidden positive meaning: {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.path)
    raw = path.read_text(encoding="utf-8")
    data = load_data(path) if path.suffix.lower() in {".yaml", ".yml", ".json"} else raw
    return emit("validate_prompt", str(path), validate(data, raw), as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
