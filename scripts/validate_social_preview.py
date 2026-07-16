#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from png_utils import parse_png

MANIFEST = Path("assets/repository/repository-social-preview-manifest.json")
SOURCE = Path("assets/repository/repository-social-preview-source.svg")
PRODUCTION = Path("assets/repository/repository-social-preview.png")
BENCHMARK = Path("docs/social-preview-benchmark.md")
CONCEPTS = Path("docs/social-preview-concepts.md")
ASSET_NOTES = Path("assets/repository/README.md")
EXPECTED_DIMENSIONS = {
    "assets/repository/repository-social-preview.png": (1280, 640),
    "assets/repository/proofs/github-crop-proof.png": (1280, 640),
    "assets/repository/proofs/small-size-proof.png": (640, 320),
    "assets/repository/proofs/light-ui-proof.png": (1440, 840),
    "assets/repository/proofs/dark-ui-proof.png": (1440, 840),
}
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "external-logo")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path = ROOT) -> tuple[list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    required = (MANIFEST, SOURCE, PRODUCTION, BENCHMARK, CONCEPTS, ASSET_NOTES)
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing social preview artifact: {relative.as_posix()}")
    if errors:
        return errors, {"files": 0, "benchmark_repositories": 0, "concepts": 0}

    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid social preview manifest: {exc}"], {"files": 0, "benchmark_repositories": 0, "concepts": 0}

    if manifest.get("schema_version") != "1.0.0":
        errors.append("social preview manifest schema_version must be 1.0.0")
    if manifest.get("status") not in {"awaiting_settings_upload", "public_verified"}:
        errors.append("invalid social preview lifecycle status")
    if manifest.get("dimensions") != {"width": 1280, "height": 640}:
        errors.append("production dimensions must be 1280 x 640")
    alt_text = manifest.get("alt_text")
    if not isinstance(alt_text, str) or len(alt_text.strip()) < 40:
        errors.append("social preview alt text is missing or too short")

    style = manifest.get("style_review")
    if not isinstance(style, dict):
        errors.append("missing style_review")
    else:
        if style.get("manual_review") != "pass":
            errors.append("manual style review must pass")
        silver = style.get("declared_silver_ratio")
        gold = style.get("declared_gold_ratio")
        if not isinstance(silver, int) or not isinstance(gold, int) or silver + gold != 100:
            errors.append("declared material ratios must be integers that sum to 100")
        elif not 70 <= silver <= 85 or not 15 <= gold <= 30:
            errors.append("declared material ratios violate Silver-Gold contract")
        for key in ("silver_dominant", "gold_accent_only", "no_black_gold_drift", "no_chrome_or_gloss", "no_small_critical_text"):
            if style.get(key) is not True:
                errors.append(f"style_review must confirm {key}")
        if style.get("external_brand_trace") is not False:
            errors.append("external brand trace must be false")

    public = manifest.get("public_proof")
    if not isinstance(public, dict):
        errors.append("missing public_proof")
    elif manifest.get("status") == "public_verified":
        if public.get("verified") is not True or public.get("manual_action_required") is not False:
            errors.append("public_verified status requires verified proof and no manual action")
    elif public.get("verified") is not False or public.get("manual_action_required") is not True:
        errors.append("awaiting_settings_upload must keep the manual action explicit")

    records = manifest.get("files")
    if not isinstance(records, dict):
        errors.append("manifest files must be a mapping")
        records = {}
    for relative, record in records.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"manifest file missing: {relative}")
            continue
        if not isinstance(record, dict):
            errors.append(f"manifest record must be a mapping: {relative}")
            continue
        if record.get("sha256") != sha256(path):
            errors.append(f"stale checksum: {relative}")
        if record.get("size_bytes") != path.stat().st_size:
            errors.append(f"stale size: {relative}")

    for relative, expected in EXPECTED_DIMENSIONS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing preview proof: {relative}")
            continue
        try:
            info = parse_png(path.read_bytes())
        except ValueError as exc:
            errors.append(f"invalid preview PNG {relative}: {exc}")
            continue
        if (info.width, info.height) != expected:
            errors.append(f"wrong preview dimensions: {relative}")
        if relative == PRODUCTION.as_posix() and path.stat().st_size >= 1_000_000:
            errors.append("production preview must be under 1 MB")

    source_text = (root / SOURCE).read_text(encoding="utf-8")
    if '<svg' not in source_text or 'width="1280"' not in source_text or 'height="640"' not in source_text:
        errors.append("editable SVG source must declare 1280 x 640")
    if re.search(r"<(?:image|script)\b|(?:href|src)=[\"']https?://", source_text, flags=re.IGNORECASE):
        errors.append("editable source must not embed external resources")

    combined_text = "\n".join((source_text, (root / BENCHMARK).read_text(encoding="utf-8"), (root / CONCEPTS).read_text(encoding="utf-8"), json.dumps(manifest))).casefold()
    for marker in BANNED:
        if marker in combined_text:
            errors.append(f"external brand marker is not allowed: {marker}")

    benchmark_text = (root / BENCHMARK).read_text(encoding="utf-8")
    benchmark_count = len(re.findall(r"^\| https://github\.com/", benchmark_text, flags=re.MULTILINE))
    if benchmark_count < 12:
        errors.append("benchmark must contain at least 12 repositories")
    for snippet in ("1280 x 640", "under 1 MB", "Settings -> Social preview -> Edit"):
        if snippet not in benchmark_text:
            errors.append(f"benchmark missing official requirement: {snippet}")

    concepts_text = (root / CONCEPTS).read_text(encoding="utf-8")
    concept_count = len(re.findall(r"^\| [ABC]\. ", concepts_text, flags=re.MULTILINE))
    if concept_count < 3:
        errors.append("concept document must score at least three concepts")
    if "97 | selected" not in concepts_text:
        errors.append("concept decision must identify the selected winner")

    details = {
        "files": len(records),
        "benchmark_repositories": benchmark_count,
        "concepts": concept_count,
        "production_sha256": sha256(root / PRODUCTION),
        "public_verified": bool(public.get("verified")) if isinstance(public, dict) else False,
        "subjective_style_review": "manual",
    }
    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, details = validate(args.root)
    payload = {"status": "fail" if errors else "pass", "errors": errors, "details": details}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"social preview validation: {'FAIL' if errors else 'PASS'} ({details.get('benchmark_repositories', 0)} repositories, {details.get('concepts', 0)} concepts)")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
