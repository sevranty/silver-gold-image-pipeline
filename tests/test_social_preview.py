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

    def test_non_object_manifest_fails_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_scope(Path(directory))
            path, _ = self.load_manifest(root)
            path.write_text("[]\n", encoding="utf-8")
            errors, details = VALIDATOR.validate(root)
            self.assertEqual(errors, ["social preview manifest must be a JSON object"])
            self.assertEqual(details["files"], 0)

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

    def test_missing_production_reports_all_available_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_scope(Path(directory))
            production = root / "assets/repository/repository-social-preview.png"
            if production.exists():
                production.unlink()
            errors, details = VALIDATOR.validate(root)
            self.assertIn(
                "missing preview proof: assets/repository/repository-social-preview.png",
                errors,
            )
            self.assertIsNone(details["production_sha256"])
            self.assertGreater(details["files"], 0)

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


    def test_manifest_references_are_canonical(self) -> None:
        _, manifest = self.load_manifest(ROOT)
        self.assertEqual(VALIDATOR.validate_manifest_references(manifest), [])
        mutations = (
            ("production_path", "assets/repository/other.png"),
            ("editable_source", "assets/repository/other.svg"),
            ("proofs", {"full_size": "assets/repository/other.png"}),
            ("proofs", None),
        )
        for key, replacement in mutations:
            with self.subTest(field=key, replacement=replacement):
                changed = dict(manifest)
                changed[key] = replacement
                self.assertTrue(VALIDATOR.validate_manifest_references(changed))

    def test_manifest_references_reject_extra_proofs(self) -> None:
        _, manifest = self.load_manifest(ROOT)
        changed = dict(manifest)
        changed["proofs"] = {**manifest["proofs"], "unreviewed": "assets/repository/other.png"}
        self.assertIn(
            "proofs must reference exactly the canonical preview assets",
            VALIDATOR.validate_manifest_references(changed),
        )


    def test_manifest_requires_all_preview_and_source_records(self) -> None:
        _, manifest = self.load_manifest(ROOT)
        records = dict(manifest["files"])
        missing = "assets/repository/proofs/dark-ui-proof.png"
        records.pop(missing)
        errors = VALIDATOR.validate_manifest_coverage(records)
        self.assertIn(f"manifest missing required file record: {missing}", errors)

    def test_manifest_rejects_path_escape(self) -> None:
        _, manifest = self.load_manifest(ROOT)
        records = dict(manifest["files"])
        records["assets/repository/../../../outside.png"] = {
            "sha256": "0" * 64,
            "size_bytes": 0,
        }
        errors = VALIDATOR.validate_manifest_coverage(records)
        self.assertTrue(any("unsafe social preview manifest path" in error for error in errors))


    def test_manifest_rejects_noncanonical_paths(self) -> None:
        for relative in (
            "assets/repository//double-separator.png",
            "assets/repository/./dot-segment.png",
            "assets/repository/../outside.png",
            "assets/repository\\windows-path.png",
            "assets/repository/nul\x00byte.png",
            None,
        ):
            with self.subTest(relative=relative):
                errors = VALIDATOR.validate_manifest_coverage({relative: {}})
                self.assertTrue(
                    any("unsafe social preview manifest path" in error for error in errors),
                    errors,
                )

    def test_manifest_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            asset_dir = root / "assets/repository"
            asset_dir.mkdir(parents=True)
            external = Path(directory) / "outside.png"
            external.write_bytes(b"not a repository preview")
            link = asset_dir / "escape.png"
            link.symlink_to(external)
            self.assertFalse(
                VALIDATOR.is_safe_manifest_target(
                    root, "assets/repository/escape.png"
                )
            )
            local = asset_dir / "local.png"
            local.write_bytes(b"local preview")
            self.assertTrue(
                VALIDATOR.is_safe_manifest_target(
                    root, "assets/repository/local.png"
                )
            )


    def test_manifest_rejects_symlink_cycle_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            asset_dir = root / "assets/repository"
            asset_dir.mkdir(parents=True)
            link = asset_dir / "loop.png"
            link.symlink_to(link)
            self.assertFalse(
                VALIDATOR.is_safe_manifest_target(
                    root, "assets/repository/loop.png"
                )
            )

    def test_manifest_rejects_symlinked_asset_root_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repo"
            (root / "assets").mkdir(parents=True)
            external = base / "external-assets"
            external.mkdir()
            (external / "preview.png").write_bytes(b"not a repository preview")
            (root / "assets/repository").symlink_to(
                external, target_is_directory=True
            )
            self.assertFalse(
                VALIDATOR.is_safe_manifest_target(
                    root, "assets/repository/preview.png"
                )
            )


if __name__ == "__main__":
    unittest.main()
