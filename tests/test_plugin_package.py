from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("package_validator_tests", SCRIPTS / "validate_plugin_package.py")
BUILDER = load_module("package_builder_tests", SCRIPTS / "build_plugin_package.py")
INSTALLER = load_module("package_installer_tests", SCRIPTS / "test_installation.py")


class PluginPackageTests(unittest.TestCase):
    def copy_repo(self, parent: Path) -> Path:
        target = parent / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", ".validation-pycache"),
        )
        return target

    def test_current_source_package_passes(self) -> None:
        errors, details = VALIDATOR.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(details["source_required_files"], 10)

    def test_invalid_metadata_fixtures_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = self.copy_repo(Path(temporary_directory))
            shutil.copy2(
                ROOT / "tests/fixtures/package/invalid-plugin.json",
                target / ".codex-plugin/plugin.json",
            )
            errors, _ = VALIDATOR.validate(target)
            self.assertTrue(any("plugin manifest" in error for error in errors))

        with tempfile.TemporaryDirectory() as temporary_directory:
            target = self.copy_repo(Path(temporary_directory))
            shutil.copy2(
                ROOT / "tests/fixtures/package/invalid-openai.yaml",
                target / "skills/silver-gold-image-pipeline/agents/openai.yaml",
            )
            errors, _ = VALIDATOR.validate(target)
            self.assertTrue(any("openai" in error or "brand-specific" in error for error in errors))

    def test_missing_reference_and_version_mismatch_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = self.copy_repo(Path(temporary_directory))
            (target / "skills/silver-gold-image-pipeline/references/quality-gates.md").unlink()
            errors, _ = VALIDATOR.validate(target)
            self.assertTrue(any("missing required runtime file" in error for error in errors))

        with tempfile.TemporaryDirectory() as temporary_directory:
            target = self.copy_repo(Path(temporary_directory))
            path = target / "release/package-contract.yaml"
            contract = yaml.safe_load(path.read_text(encoding="utf-8"))
            contract["versions"]["qa_schema_version"] = "9.9.9"
            path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            errors, _ = VALIDATOR.validate(target)
            self.assertIn("package contract versions mismatch", errors)

    def test_deterministic_archive_and_installation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            first = BUILDER.build(ROOT, temporary / "first")
            second = BUILDER.build(ROOT, temporary / "second")
            self.assertEqual(first["archive_sha256"], second["archive_sha256"])
            first_manifest = json.loads(Path(first["manifest"]).read_text(encoding="utf-8"))
            second_manifest = json.loads(Path(second["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(first_manifest["files"], second_manifest["files"])
            errors, details = VALIDATOR.validate(
                ROOT,
                Path(first["archive"]),
                Path(first["manifest"]),
                Path(first["checksum"]),
            )
            self.assertEqual(errors, [])
            self.assertEqual(details["archive_files"], first["file_count"])
            install_errors, install_details = INSTALLER.smoke(ROOT)
            self.assertEqual(install_errors, [])
            self.assertEqual(install_details["archive_sha256"], first["archive_sha256"])

    def test_forbidden_content_and_changed_archive_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            result = BUILDER.build(ROOT, temporary / "package")
            archive = Path(result["archive"])
            with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as package:
                package.writestr("docs/forbidden.md", "not runtime content\n")
            errors, _ = VALIDATOR.validate(ROOT, archive)
            self.assertTrue(any("excluded content" in error for error in errors))

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            result = BUILDER.build(ROOT, temporary / "package")
            archive = Path(result["archive"])
            archive.write_bytes(archive.read_bytes() + b"changed")
            errors, _ = VALIDATOR.validate(
                ROOT,
                archive,
                Path(result["manifest"]),
                Path(result["checksum"]),
            )
            self.assertTrue(any("checksum" in error for error in errors))

    def test_valid_metadata_fixtures_parse(self) -> None:
        plugin = json.loads(
            (ROOT / "tests/fixtures/package/valid-plugin.json").read_text(encoding="utf-8")
        )
        openai = yaml.safe_load(
            (ROOT / "tests/fixtures/package/valid-openai.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(plugin["id"], "silver-gold-image-pipeline")
        self.assertIn("visual QA", openai["interface"]["short_description"])


if __name__ == "__main__":
    unittest.main()
