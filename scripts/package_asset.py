#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from png_utils import clean_png
from validation_common import ascii_path, emit, sha256_file

FORBIDDEN_SUFFIXES = {".doc", ".docx", ".pdf", ".pages"}
FORBIDDEN_PARTS = {"private", "source-documents", "confidential"}


def clean_image(source: Path, target: Path) -> None:
    cleaned, _ = clean_png(source.read_bytes())
    target.write_bytes(cleaned)


def package(final: Path, preview: Path | None, output_dir: Path, asset_id: str) -> tuple[list[str], dict]:
    errors: list[str] = []
    if not asset_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in asset_id):
        errors.append("asset_id must use lowercase ASCII letters, digits, and hyphens")
    sources = [final] + ([preview] if preview else [])
    for source in sources:
        if source is None or not source.is_file():
            errors.append(f"missing input file: {source}")
            continue
        if source.suffix.lower() in FORBIDDEN_SUFFIXES or any(part.casefold() in FORBIDDEN_PARTS for part in source.parts):
            errors.append(f"forbidden source input: {source}")
        if source.suffix.lower() != ".png":
            errors.append(f"unsupported source format: {source.name}")
        if not ascii_path(Path(source.name)):
            errors.append(f"non-ASCII filename: {source.name}")
    if errors:
        return errors, {}
    target_dir = output_dir / asset_id
    target_dir.mkdir(parents=True, exist_ok=True)
    records = {}
    for role, source in (("final", final), ("preview", preview)):
        if source is None:
            continue
        target = target_dir / source.name
        try:
            clean_image(source, target)
        except (OSError, ValueError) as exc:
            return [f"invalid PNG input {source.name}: {exc}"], {}
        records[role] = {
            "path": target.relative_to(output_dir).as_posix(),
            "sha256": sha256_file(target),
            "size_bytes": target.stat().st_size,
        }
    manifest = {
        "schema_version": "1.0.0",
        "asset_id": asset_id,
        "files": records,
        "source_documents_included": False,
        "private_fixtures_included": False,
        "exif_preserved": False,
    }
    manifest_path = target_dir / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return [], {"package_dir": str(target_dir), "manifest": str(manifest_path), "files": records}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", required=True)
    parser.add_argument("--preview")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, details = package(Path(args.final), Path(args.preview) if args.preview else None, Path(args.output_dir), args.asset_id)
    return emit("package_asset", args.final, errors, details=details, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
