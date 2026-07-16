#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path

from validation_common import ascii_path, emit, sha256_file

FORBIDDEN_SUFFIXES = {".doc", ".docx", ".pdf", ".pages"}
FORBIDDEN_PARTS = {"private", "source-documents", "confidential"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CRITICAL_CHUNKS = {b"IHDR", b"IDAT", b"IEND"}


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)


def clean_image(source: Path, target: Path) -> None:
    data = source.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("only PNG assets can be packaged without metadata preservation")
    offset = len(PNG_SIGNATURE)
    cleaned = bytearray(PNG_SIGNATURE)
    saw_ihdr = False
    saw_idat = False
    saw_iend = False
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise ValueError("truncated PNG file")
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:crc_end])[0]
        actual_crc = zlib.crc32(kind + payload) & 0xffffffff
        if actual_crc != expected_crc:
            raise ValueError(f"invalid PNG CRC for {kind.decode('ascii', errors='replace')}")
        if kind == b"IHDR":
            saw_ihdr = True
        elif kind == b"IDAT":
            saw_idat = True
        elif kind == b"IEND":
            saw_iend = True
        if kind in CRITICAL_CHUNKS:
            cleaned.extend(_chunk(kind, payload))
        offset = crc_end
        if kind == b"IEND":
            break
    if not (saw_ihdr and saw_idat and saw_iend):
        raise ValueError("PNG must contain IHDR, IDAT, and IEND")
    target.write_bytes(bytes(cleaned))


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
        except ValueError as exc:
            return [f"invalid PNG input {source.name}: {exc}"], {}
        records[role] = {"path": target.relative_to(output_dir).as_posix(), "sha256": sha256_file(target), "size_bytes": target.stat().st_size}
    manifest = {"schema_version": "1.0.0", "asset_id": asset_id, "files": records, "source_documents_included": False, "private_fixtures_included": False, "exif_preserved": False}
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
