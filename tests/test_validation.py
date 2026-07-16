from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from inspect_image import inspect
from package_asset import package
from png_utils import PNG_SIGNATURE
from validate_manifest import validate as validate_manifest
from validate_prompt import validate as validate_prompt
from validate_scene_spec import validate as validate_scene
from validation_common import load_data

FIXTURES = ROOT / "tests/fixtures/validation"


def chunk(kind: bytes, payload: bytes, *, corrupt_crc: bool = False) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    if corrupt_crc:
        crc ^= 1
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def png_bytes(width: int = 2, height: int = 2, mode: str = "RGBA", *, text_chunk: bool = False) -> bytes:
    channels = {"L": 1, "LA": 2, "RGB": 3, "RGBA": 4}[mode]
    color_type = {"L": 0, "LA": 4, "RGB": 2, "RGBA": 6}[mode]
    pixel = bytes([180, 160, 120, 255][:channels])
    raw = (b"\x00" + pixel * width) * height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    chunks = [chunk(b"IHDR", ihdr)]
    if text_chunk:
        chunks.append(chunk(b"tEXt", b"Comment\x00metadata"))
    chunks.extend((chunk(b"IDAT", zlib.compress(raw)), chunk(b"IEND", b"")))
    return PNG_SIGNATURE + b"".join(chunks)


def write_png(path: Path, width: int, height: int, mode: str, *, text_chunk: bool = False) -> None:
    path.write_bytes(png_bytes(width, height, mode, text_chunk=text_chunk))


def indexed_png_bytes() -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 3, 0, 0, 0)
    raw = b"\x00\x00"
    return PNG_SIGNATURE + b"".join(
        (chunk(b"IHDR", ihdr), chunk(b"PLTE", b"\x00\x00\x00"), chunk(b"IDAT", zlib.compress(raw)), chunk(b"IEND", b""))
    )


class ValidationSuiteTests(unittest.TestCase):
    def test_scene_positive_and_negative(self) -> None:
        self.assertEqual(validate_scene(load_data(FIXTURES / "valid-scene.yaml")), [])
        self.assertTrue(validate_scene(load_data(FIXTURES / "invalid-scene.yaml")))

    def test_prompt_positive_negative_and_context(self) -> None:
        for name in ("valid-prompt.txt", "negative-reflection-prompt.txt"):
            raw = (FIXTURES / name).read_text(encoding="utf-8")
            self.assertEqual(validate_prompt(raw, raw), [], name)
        raw = (FIXTURES / "invalid-prompt.txt").read_text(encoding="utf-8")
        self.assertTrue(validate_prompt(raw, raw))

    def test_manifest_positive_and_negative(self) -> None:
        self.assertEqual(validate_manifest(load_data(FIXTURES / "valid-manifest.yaml")), [])
        self.assertTrue(validate_manifest(load_data(FIXTURES / "invalid-manifest.yaml")))

    def test_image_inspection_and_packaging(self) -> None:
        for mode in ("L", "LA", "RGB", "RGBA"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                final = tmp_path / "silver-gold-final.png"
                preview = tmp_path / "silver-gold-preview.png"
                write_png(final, 1024, 1024, mode, text_chunk=True)
                write_png(preview, 256, 256, "RGB")
                errors, _, details = inspect(final)
                self.assertEqual(errors, [])
                self.assertEqual(details["width"], 1024)
                self.assertEqual(details["mode"], mode)
                output = tmp_path / "dist"
                errors, packaged = package(final, preview, output, f"silver-gold-{mode.lower()}")
                self.assertEqual(errors, [])
                manifest_path = Path(packaged["manifest"])
                self.assertTrue(manifest_path.is_file())
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertFalse(manifest["exif_preserved"])
                self.assertEqual(set(manifest["files"]), {"final", "preview"})
                packaged_final = output / manifest["files"]["final"]["path"]
                self.assertNotIn(b"tEXt", packaged_final.read_bytes())
                self.assertEqual(inspect(packaged_final)[0], [])

    def test_malformed_pngs_are_rejected(self) -> None:
        ihdr_payload = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
        valid_idat = chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\xff"))
        cases = {
            "ihdr-only": PNG_SIGNATURE + chunk(b"IHDR", ihdr_payload),
            "bad-crc": PNG_SIGNATURE + chunk(b"IHDR", ihdr_payload, corrupt_crc=True) + valid_idat + chunk(b"IEND", b""),
            "missing-idat": PNG_SIGNATURE + chunk(b"IHDR", ihdr_payload) + chunk(b"IEND", b""),
            "missing-iend": PNG_SIGNATURE + chunk(b"IHDR", ihdr_payload) + valid_idat,
            "duplicate-ihdr": PNG_SIGNATURE + chunk(b"IHDR", ihdr_payload) + chunk(b"IHDR", ihdr_payload) + valid_idat + chunk(b"IEND", b""),
            "trailing-data": png_bytes() + b"trailing",
        }
        for name, data in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "broken.png"
                path.write_bytes(data)
                errors, _, _ = inspect(path)
                self.assertTrue(errors)

    def test_indexed_png_is_inspectable_but_not_packagable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "indexed.png"
            source.write_bytes(indexed_png_bytes())
            self.assertEqual(inspect(source)[0], [])
            errors, _ = package(source, None, root / "dist", "indexed")
            self.assertTrue(any("non-interlaced 8-bit" in error for error in errors), errors)

    def test_invalid_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_text("not an image", encoding="utf-8")
            errors, _, _ = inspect(path)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
