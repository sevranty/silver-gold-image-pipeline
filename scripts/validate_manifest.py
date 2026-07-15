#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from validation_common import emit, has_absolute_local_path, has_secret, load_data

SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSIONS = {"skill_version", "pipeline_core_version", "style_core_version", "background_profiles_version", "prompt_schema_version", "qa_schema_version", "manifest_schema_version"}


def validate(data: dict, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    for key in ("asset_id", "created_at", "versions", "references", "iterations", "quality", "files"):
        if key not in data:
            errors.append(f"missing field: {key}")
    if not isinstance(data.get("asset_id"), str) or not data.get("asset_id"):
        errors.append("invalid asset_id")
    created = data.get("created_at")
    if not isinstance(created, str) or "T" not in created or not created.endswith("Z"):
        errors.append("created_at must be UTC ISO-8601")
    versions = data.get("versions", {})
    missing_versions = VERSIONS - set(versions) if isinstance(versions, dict) else VERSIONS
    if missing_versions:
        errors.append(f"missing versions: {sorted(missing_versions)}")
    references = data.get("references", [])
    if not isinstance(references, list) or not references:
        errors.append("references must be a non-empty list")
    else:
        for item in references:
            if not all(key in item for key in ("path", "role", "provenance_status")):
                errors.append("reference missing path/role/provenance_status")
    if not isinstance(data.get("iterations"), list):
        errors.append("iterations must be a list")
    quality = data.get("quality", {})
    if quality.get("status") not in {"pass", "rejected"}:
        errors.append("invalid quality status")
    if not isinstance(quality.get("known_limitations"), list):
        errors.append("known_limitations must be a list")
    files = data.get("files", {})
    if not isinstance(files, dict) or "final" not in files:
        errors.append("final file record missing")
    else:
        for name, record in files.items():
            if not isinstance(record, dict):
                errors.append(f"{name} file record must be a mapping")
                continue
            for key in ("path", "sha256", "size_bytes"):
                if key not in record:
                    errors.append(f"{name} missing {key}")
            checksum = record.get("sha256")
            if checksum is not None and (not isinstance(checksum, str) or not SHA256.fullmatch(checksum)):
                errors.append(f"{name} invalid sha256")
            rel = record.get("path")
            if root and isinstance(rel, str) and rel and not (root / rel).is_file():
                errors.append(f"{name} file does not exist")
    for item in data.get("bundled_assets", []):
        if not all(key in item for key in ("path", "license_status", "redistribution_status")):
            errors.append("bundled asset missing license/status")
    if has_absolute_local_path(data):
        errors.append("absolute local path detected")
    if has_secret(data):
        errors.append("secret-like value detected")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.path)
    data = load_data(path)
    errors = validate(data if isinstance(data, dict) else {}, Path(args.root) if args.root else None)
    return emit("validate_manifest", str(path), errors, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
