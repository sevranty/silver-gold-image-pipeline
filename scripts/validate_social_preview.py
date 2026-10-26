#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
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


def is_safe_manifest_path(relative: object) -> bool:
    """Reject non-canonical paths before accessing manifest-controlled files."""
    if not isinstance(relative, str) or not relative.startswith("assets/repository/"):
        return False
    path = Path(relative)
    return (
        "\\" not in relative
        and "\x00" not in relative
        and ".." not in path.parts
        and path.as_posix() == relative
        and len(path.parts) > 2
    )


def is_safe_manifest_target(root: Path, relative: object) -> bool:
    """Reject file and asset-root symlinks that escape the repository."""
    if not is_safe_manifest_path(relative):
        return False
    try:
        project_root = root.resolve()
        asset_root = (project_root / "assets/repository").resolve()
        if not asset_root.is_relative_to(project_root):
            return False
        return (project_root / relative).resolve().is_relative_to(asset_root)
    except (OSError, RuntimeError, ValueError):
        return False


def validate_manifest_coverage(records: object) -> list[str]:
    """Require a digest and size record for every delivered preview asset."""
    if not isinstance(records, dict):
        return ["manifest files must be a mapping"]

    errors: list[str] = []
    required = set(EXPECTED_DIMENSIONS) | {SOURCE.as_posix()}
    for relative in sorted(required - records.keys()):
        errors.append(f"manifest missing required file record: {relative}")
    for relative in records:
        if not is_safe_manifest_path(relative):
            errors.append(f"unsafe social preview manifest path: {relative}")
    return errors


def validate_manifest_references(manifest: object) -> list[str]:
    """Check that public-facing manifest pointers name validated assets."""
    if not isinstance(manifest, dict):
        return ["social preview manifest must be a JSON object"]
    errors: list[str] = []
    if manifest.get("production_path") != PRODUCTION.as_posix():
        errors.append("production_path must reference the canonical preview PNG")
    if manifest.get("editable_source") != SOURCE.as_posix():
        errors.append("editable_source must reference the canonical SVG")
    expected_proofs = {
        "full_size": PRODUCTION.as_posix(),
        "github_crop": "assets/repository/proofs/github-crop-proof.png",
        "small_size": "assets/repository/proofs/small-size-proof.png",
        "light_ui": "assets/repository/proofs/light-ui-proof.png",
        "dark_ui": "assets/repository/proofs/dark-ui-proof.png",
    }
    proofs = manifest.get("proofs")
    if not isinstance(proofs, dict) or proofs != expected_proofs:
        errors.append("proofs must reference exactly the canonical preview assets")
    return errors




def validate_public_proof(public: object, status: object) -> list[str]:
    """Require traceable evidence before declaring the public repository card verified.

    URL shape and timestamp are structural checks, not independent proof that
    GitHub actually displays the preview. Human review remains mandatory.
    """
    if not isinstance(public, dict):
        return ["missing public_proof"]

    errors: list[str] = []
    if status == "public_verified":
        if public.get("verified") is not True or public.get("manual_action_required") is not False:
            errors.append("public_verified status requires verified proof and no manual action")

        evidence_ref = public.get("evidence_ref")
        evidence_pattern = (
            r"https://github\.com/sevranty/silver-gold-image-pipeline/"
            r"(?:issues/[0-9]+#issuecomment-[0-9]+|"
            r"blob/[0-9a-f]{40}/docs/evidence/[A-Za-z0-9._/-]+)"
        )
        if not isinstance(evidence_ref, str) or not re.fullmatch(evidence_pattern, evidence_ref):
            errors.append("public_verified requires a repository-owned evidence_ref")
        elif "/blob/" in evidence_ref:
            evidence_path = evidence_ref.split("/docs/evidence/", 1)[1]
            if any(segment in {"", ".", ".."} for segment in evidence_path.split("/")):
                errors.append("public_verified evidence_ref must use a canonical evidence path")

        verified_at = public.get("verified_at_utc")
        if not isinstance(verified_at, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
            verified_at,
        ):
            errors.append("public_verified requires verified_at_utc in UTC")
        else:
            try:
                verified_time = datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
                if verified_time > datetime.now(timezone.utc):
                    errors.append("public_verified verification time cannot be in the future")
            except ValueError:
                errors.append("public_verified requires a valid UTC verification time")
    elif public.get("verified") is not False or public.get("manual_action_required") is not True:
        errors.append("awaiting_settings_upload must keep the manual action explicit")
    return errors


def svg_has_external_resources(source_text: str) -> bool:
    """Reject active SVG content and nonlocal references in the editable source."""
    if re.search(
        r"<(?:image|script|foreignObject|animate|animateMotion|animateTransform|set)\b"
        r"|@import\b|<\?xml-stylesheet\b|<!DOCTYPE\b|<!ENTITY\b",
        source_text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(r"\bon[a-z][a-z0-9_-]*\s*=", source_text, flags=re.IGNORECASE):
        return True
    if re.search(r"url\s*\(\s*(?!['\"]?#)[^)]+\)", source_text, flags=re.IGNORECASE):
        return True
    if re.search(
        r"\b(?:xlink:)?href\s*=\s*['\"](?!#)[^'\"]+|"
        r"\bsrc\s*=\s*['\"][^'\"]+",
        source_text,
        flags=re.IGNORECASE,
    ):
        return True
    return False


def validate(root: Path = ROOT) -> tuple[list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    required = (MANIFEST, SOURCE, BENCHMARK, CONCEPTS, ASSET_NOTES)
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing social preview artifact: {relative.as_posix()}")
    if errors:
        return errors, {"files": 0, "benchmark_repositories": 0, "concepts": 0}

    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid social preview manifest: {exc}"], {"files": 0, "benchmark_repositories": 0, "concepts": 0}
    if not isinstance(manifest, dict):
        return ["social preview manifest must be a JSON object"], {"files": 0, "benchmark_repositories": 0, "concepts": 0}

    if manifest.get("schema_version") != "1.0.0":
        errors.append("social preview manifest schema_version must be 1.0.0")
    if manifest.get("status") not in {"awaiting_settings_upload", "public_verified"}:
        errors.append("invalid social preview lifecycle status")
    if manifest.get("dimensions") != {"width": 1280, "height": 640}:
        errors.append("production dimensions must be 1280 x 640")
    errors.extend(validate_manifest_references(manifest))
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
    errors.extend(validate_public_proof(public, manifest.get("status")))

    records = manifest.get("files")
    errors.extend(validate_manifest_coverage(records))
    if not isinstance(records, dict):
        records = {}
    for relative, record in records.items():
        if not is_safe_manifest_path(relative):
            continue
        if not is_safe_manifest_target(root, relative):
            errors.append(f"unsafe social preview manifest path: {relative}")
            continue
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
    if svg_has_external_resources(source_text):
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
        "production_sha256": sha256(root / PRODUCTION) if (root / PRODUCTION).is_file() else None,
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
