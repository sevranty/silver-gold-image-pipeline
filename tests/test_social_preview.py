from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
MODULE_PATH = SCRIPTS / "validate_social_preview.py"


def load_module():
    spec = importlib.util.spec_from_file_location("social_preview_validator_tests", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module()


class SocialPreviewTests(unittest.TestCase):
    def copy_scope(self, parent: Path) -> Path:
        target = parent / "repo"
        for relative in ("assets/repository", "docs/social-preview-benchmark.md", "docs/social-preview-concepts.md"):
            source = ROOT / relative
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        return target

    def load_manifest(self, root: Path) -> tuple[Path, dict]:
        path = root / "assets/repository/repository-social-preview-manifest.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def write_manifest(self, path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_current_preview_passes(self) -> None:
        errors, details = VALIDATOR.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(details["benchmark_repositories"], 12)
        self.assertEqual(details["concepts"], 3)
        self.assertFalse(details["public_verified"])

    def test_wrong_dimensions_and_stale_checksum_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_scope(Path(directory))
            path, data = self.load_manifest(root)
            data["dimensions"]["width"] = 1200
            first = next(iter(data["files"]))
            data["files"][first]["sha256"] = "0" * 64
            self.write_manifest(path, data)
            errors, _ = VALIDATOR.validate(root)
            self.assertTrue(any("1280 x 640" in error for error in errors))
            self.assertTrue(any("stale checksum" in error for error in errors))

    def test_missing_source_and_alt_text_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_scope(Path(directory))
            (root / "assets/repository/repository-social-preview-source.svg").unlink()
            path, data = self.load_manifest(root)
            data["alt_text"] = ""
            self.write_manifest(path, data)
            errors, _ = VALIDATOR.validate(root)
            self.assertTrue(any("missing social preview artifact" in error for error in errors))

    def test_style_and_brand_mutations_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_scope(Path(directory))
            path, data = self.load_manifest(root)
            data["style_review"]["declared_silver_ratio"] = 35
            data["style_review"]["declared_gold_ratio"] = 65
            data["style_review"]["no_black_gold_drift"] = False
            data["style_review"]["no_small_critical_text"] = False
            data["style_review"]["external_brand_trace"] = True
            data["alt_text"] += " external-logo"
            self.write_manifest(path, data)
            errors, _ = VALIDATOR.validate(root)
            self.assertTrue(any("ratios violate" in error for error in errors))
            self.assertTrue(any("no_black_gold_drift" in error for error in errors))
            self.assertTrue(any("no_small_critical_text" in error for error in errors))
            self.assertTrue(any("external brand" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
