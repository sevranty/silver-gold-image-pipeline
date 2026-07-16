#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path

from validation_common import ascii_path, emit

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _inspect_png(data: bytes) -> dict:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    offset = len(PNG_SIGNATURE)
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        if payload_end + 4 > len(data):
            raise ValueError("truncated PNG file")
        payload = data[payload_start:payload_end]
        if kind == b"IHDR":
            if length != 13:
                raise ValueError("invalid PNG IHDR")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", payload)
            if bit_depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
                raise ValueError("unsupported PNG header")
            mode = {0: "L", 2: "RGB", 6: "RGBA"}.get(color_type)
            if mode is None:
                raise ValueError(f"unsupported PNG color type: {color_type}")
            return {"format": "PNG", "width": width, "height": height, "aspect_ratio": width / height if height else None, "mode": mode, "alpha": color_type == 6, "exif_entries": 0}
        offset = payload_end + 4
    raise ValueError("missing PNG IHDR")


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
        details = _inspect_png(path.read_bytes())
        details["size_bytes"] = size_bytes
        if details["width"] <= 0 or details["height"] <= 0:
            errors.append("invalid image dimensions")
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
