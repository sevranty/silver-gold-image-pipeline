#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from png_utils import parse_png
from validation_common import ascii_path, emit


def inspect(path: Path) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    details: dict = {}
    if not path.is_file():
        return ["file does not exist"], warnings, details
    if not ascii_path(Path(path.name)):
        errors.append("filename must be ASCII")
    size_bytes = path.stat().st_size
    if size_bytes <= 0:
        errors.append("file is empty")
    try:
        info = parse_png(path.read_bytes())
        details = {
            "format": "PNG",
            "width": info.width,
            "height": info.height,
            "aspect_ratio": info.width / info.height,
            "mode": info.mode,
            "alpha": info.alpha,
            "size_bytes": size_bytes,
            "exif_entries": 0,
        }
    except (OSError, ValueError) as exc:
        errors.append(f"image cannot be opened: {exc}")
    return errors, warnings, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.path)
    errors, warnings, details = inspect(path)
    return emit("inspect_image", str(path), errors, warnings, details, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
