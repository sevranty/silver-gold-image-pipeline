#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from validation_common import ascii_path, emit


def inspect(path: Path) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    details: dict = {}
    if not path.is_file():
        return ["file does not exist"], warnings, details
    if not ascii_path(Path(path.name)):
        errors.append("filename must be ASCII")
    if path.stat().st_size <= 0:
        errors.append("file is empty")
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            details = {"format": image.format, "width": width, "height": height, "aspect_ratio": width / height if height else None, "mode": image.mode, "alpha": "A" in image.getbands(), "size_bytes": path.stat().st_size, "exif_entries": len(image.getexif())}
            if width <= 0 or height <= 0:
                errors.append("invalid image dimensions")
            if image.getexif():
                warnings.append("EXIF metadata present")
    except (UnidentifiedImageError, OSError) as exc:
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
