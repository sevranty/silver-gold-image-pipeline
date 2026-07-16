#!/usr/bin/env python3
"""Build the deterministic standalone Silver-Gold plugin package."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contract(root: Path) -> dict[str, Any]:
    path = root / "release/package-contract.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("package contract must be a mapping")
    return data


def excluded(relative_path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(relative_path, pattern) for pattern in patterns)


def source_files(root: Path) -> list[Path]:
    root = root.resolve()
    configuration = contract(root)
    include = configuration.get("include", [])
    exclude = configuration.get("exclude", [])
    if not isinstance(include, list) or not include:
        raise ValueError("package contract include must be a non-empty list")
    if not isinstance(exclude, list):
        raise ValueError("package contract exclude must be a list")

    selected: set[Path] = set()
    for entry in include:
        if not isinstance(entry, str) or not entry:
            raise ValueError("package include entries must be non-empty strings")
        if entry.endswith("/**"):
            directory = root / entry[:-3]
            if not directory.is_dir():
                raise FileNotFoundError(f"included directory missing: {entry[:-3]}")
            candidates = (path for path in directory.rglob("*") if path.is_file())
        else:
            path = root / entry
            if not path.is_file():
                raise FileNotFoundError(f"included file missing: {entry}")
            candidates = (path,)

        for path in candidates:
            relative = path.relative_to(root).as_posix()
            if not excluded(relative, exclude):
                selected.add(path)

    return sorted(selected, key=lambda path: path.relative_to(root).as_posix())


def source_commit(root: Path) -> str | None:
    github_sha = os.environ.get("GITHUB_SHA")
    if github_sha:
        return github_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build(root: Path, output_directory: Path) -> dict[str, Any]:
    root = root.resolve()
    configuration = contract(root)
    version = configuration["package_version"]
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"silver-gold-image-pipeline-{version}.zip"
    records: list[dict[str, Any]] = []

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as package:
        for path in source_files(root):
            relative = path.relative_to(root).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(relative, FIXED_TIME)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
            records.append(
                {
                    "path": relative,
                    "sha256": sha256(data),
                    "size_bytes": len(data),
                }
            )

    archive_hash = sha256(archive.read_bytes())
    manifest = {
        "schema_version": "1.0.0",
        "package_version": version,
        "source_commit": source_commit(root),
        "archive": archive.name,
        "archive_sha256": archive_hash,
        "files": records,
    }
    manifest_path = output_directory / f"{archive.name}.manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checksum_path = output_directory / f"{archive.name}.sha256"
    checksum_path.write_text(
        f"{archive_hash}  {archive.name}\n",
        encoding="utf-8",
    )
    return {
        "archive": str(archive),
        "manifest": str(manifest_path),
        "checksum": str(checksum_path),
        "file_count": len(records),
        "archive_sha256": archive_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build(args.root.resolve(), args.out_dir.resolve())
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
