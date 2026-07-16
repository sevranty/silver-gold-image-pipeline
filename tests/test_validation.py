from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import struct
import zlib


def write_png(path: Path, width: int, height: int, mode: str, *, text_chunk: bool = False) -> None:
    channels = {"RGB": 3, "RGBA": 4}[mode]
    color_type = {"RGB": 2, "RGBA": 6}[mode]
    pixel = bytes([180, 180, 184, 255][:channels])
    row = b"\x00" + pixel * width
    raw = row * height
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    chunks = [chunk(b"IHDR", ihdr)]
    if text_chunk:
        chunks.append(chunk(b"tEXt", b"Comment\x00metadata"))
    chunks.extend([chunk(b"IDAT", zlib.compress(raw)), chunk(b"IEND", b"")])
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"".join(chunks))
sys.path.insert(0, str(ROOT / "scripts"))

from inspect_image import inspect
from package_asset import package
from validate_manifest import validate as validate_manifest
from validate_prompt import validate as validate_prompt
from validate_scene_spec import validate as validate_scene
from validation_common import load_data

FIXTURES = ROOT / "tests/fixtures/validation"


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
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            final = tmp_path / "silver-gold-final.png"
            preview = tmp_path / "silver-gold-preview.png"
            write_png(final, 1024, 1024, "RGBA", text_chunk=True)
            write_png(preview, 256, 256, "RGB")
            errors, _, details = inspect(final)
            self.assertEqual(errors, [])
            self.assertEqual(details["width"], 1024)
            output = tmp_path / "dist"
            errors, packaged = package(final, preview, output, "silver-gold-test")
            self.assertEqual(errors, [])
            manifest_path = Path(packaged["manifest"])
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertFalse(manifest["exif_preserved"])
            self.assertEqual(set(manifest["files"]), {"final", "preview"})
            packaged_final = output / manifest["files"]["final"]["path"]
            self.assertNotIn(b"tEXt", packaged_final.read_bytes())

    def test_invalid_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_text("not an image", encoding="utf-8")
            errors, _, _ = inspect(path)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
