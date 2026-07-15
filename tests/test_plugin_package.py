from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("validate_plugin_package", ROOT / "scripts/validate_plugin_package.py")
BUILDER = load_module("build_plugin_package", ROOT / "scripts/build_plugin_package.py")
INSTALLER = load_module("test_installation", ROOT / "scripts/test_installation.py")


class PluginPackageTests(unittest.TestCase):
    def test_current_source_package_passes(self) -> None:
        errors, details = VALIDATOR.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(details["source_required_files"], 10)

    def test_invalid_plugin_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self._copy_repo(Path(tmp))
            fixture = ROOT / "tests/fixtures/package/invalid-plugin.json"
            shutil.copy2(fixture, target / ".codex-plugin/plugin.json")
            errors, _ = VALIDATOR.validate(target)
            self.assertTrue(any("plugin manifest" in error or "plugin repository" in error for error in errors))

    def test_invalid_openai_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self._copy_repo(Path(tmp))
            fixture = ROOT / "tests/fixtures/package/invalid-openai.yaml"
            shutil.copy2(fixture, target / "skills/silver-gold-image-pipeline/agents/openai.yaml")
            errors, _ = VALIDATOR.validate(target)
            self.assertTrue(any("openai" in error or "brand-specific" in error for error in errors))

    def test_deterministic_archive_and_installation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            first = BUILDER.build(ROOT, temp / "first")
            second = BUILDER.build(ROOT, temp / "second")
            self.assertEqual(first["archive_sha256"], second["archive_sha256"])
            errors, _ = VALIDATOR.validate(ROOT, Path(first["archive"]))
            self.assertEqual(errors, [])
            install_errors, details = INSTALLER.smoke(ROOT)
            self.assertEqual(install_errors, [])
            self.assertEqual(details["archive_sha256"], first["archive_sha256"])

    def test_valid_metadata_fixtures_parse(self) -> None:
        plugin = json.loads((ROOT / "tests/fixtures/package/valid-plugin.json").read_text())
        openai = yaml.safe_load((ROOT / "tests/fixtures/package/valid-openai.yaml").read_text())
        self.assertEqual(plugin["id"], "silver-gold-image-pipeline")
        self.assertIn("visual QA", openai["interface"]["short_description"])

    @staticmethod
    def _copy_repo(parent: Path) -> Path:
        target = parent / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", ".validation-pycache"))
        return target


if __name__ == "__main__":
    unittest.main()
