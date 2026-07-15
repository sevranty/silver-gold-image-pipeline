#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from validation_common import emit, load_data

MODES = {"generate", "edit", "style_transfer", "reinterpretation", "composite", "sketch_to_render"}
PROFILES = {"product-light", "showcase-neutral"}
ROLES = {"subject_reference", "identity_reference", "composition_reference", "environment_reference", "text_reference", "logo_reference", "mask_reference"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "contract_version", "transformation_mode", "background_profile", "references", "locks", "materials", "preserve", "change", "exclude", "output"):
        if key not in data:
            errors.append(f"missing field: {key}")
    if data.get("transformation_mode") not in MODES:
        errors.append("invalid transformation_mode")
    if data.get("background_profile") not in PROFILES:
        errors.append("invalid background_profile")
    references = data.get("references", {})
    for item in references.get("items", []) if isinstance(references, dict) else []:
        if item.get("role") not in ROLES:
            errors.append("invalid reference role")
        priority = item.get("priority")
        if not isinstance(priority, int) or not 1 <= priority <= 100:
            errors.append("invalid reference priority")
    locks = data.get("locks", {})
    style_lock = locks.get("silver_gold_style_lock", {}) if isinstance(locks, dict) else {}
    if style_lock.get("enabled") is not True or style_lock.get("fidelity") != 4:
        errors.append("invalid silver_gold_style_lock")
    materials = data.get("materials", {})
    silver, gold = materials.get("silver_ratio"), materials.get("gold_ratio")
    if not isinstance(silver, int) or not 70 <= silver <= 85:
        errors.append("silver_ratio out of range")
    if not isinstance(gold, int) or not 15 <= gold <= 30:
        errors.append("gold_ratio out of range")
    if isinstance(silver, int) and isinstance(gold, int) and silver + gold != 100:
        errors.append("metal ratios must sum to 100")
    for key in ("preserve", "change", "exclude"):
        if not isinstance(data.get(key), list):
            errors.append(f"{key} must be a list")
    output = data.get("output", {})
    width, height = output.get("width"), output.get("height")
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        errors.append("invalid output dimensions")
    ratio = output.get("aspect_ratio")
    if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0 and isinstance(ratio, str) and ":" in ratio:
        a, b = ratio.split(":", 1)
        try:
            declared = float(a) / float(b)
            actual = width / height
            if abs(declared - actual) > 0.02:
                errors.append("aspect ratio conflicts with dimensions")
        except (ValueError, ZeroDivisionError):
            errors.append("invalid aspect_ratio")
    else:
        errors.append("invalid aspect_ratio")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.path)
    data = load_data(path)
    errors = validate(data if isinstance(data, dict) else {})
    return emit("validate_scene_spec", str(path), errors, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
