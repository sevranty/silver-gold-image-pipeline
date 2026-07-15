from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_regression_suite", ROOT / "scripts/validate_regression_suite.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RegressionSuiteTests(unittest.TestCase):
    def test_complete_suite_passes(self) -> None:
        errors, details = MODULE.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(details["trigger_cases"], 30)
        self.assertEqual(details["workflow_cases"], 24)
        self.assertEqual(details["visual_anchors"], 13)
        self.assertFalse(details["subjective_visual_quality_assessed"])

    def test_missing_category_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._copy_tree(target)
            path = target / "tests/cases/visual-regression-cases.yaml"
            data = yaml.safe_load(path.read_text())
            data["anchors"] = [a for a in data["anchors"] if a["category"] != "chrome-gloss"]
            path.write_text(yaml.safe_dump(data, sort_keys=False))
            errors, _ = MODULE.validate(target)
            self.assertTrue(any("missing visual categories" in e for e in errors))

    def test_hash_mutation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._copy_tree(target)
            asset = target / "skills/silver-gold-image-pipeline/assets/examples/accepted/product-light.svg"
            asset.write_text(asset.read_text() + "<!-- mutation -->\n")
            errors, _ = MODULE.validate(target)
            self.assertTrue(any("SHA-256 mismatch" in e for e in errors))

    def test_false_generator_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._copy_tree(target)
            path = target / "tests/cases/visual-regression-cases.yaml"
            data = yaml.safe_load(path.read_text())
            data["anchors"][0]["image_generator_output"] = True
            path.write_text(yaml.safe_dump(data, sort_keys=False))
            errors, _ = MODULE.validate(target)
            self.assertTrue(any("synthetic/generator boundary invalid" in e for e in errors))

    def _copy_tree(self, target: Path) -> None:
        import shutil
        for rel in ("scripts", "tests/cases", "docs", "skills/silver-gold-image-pipeline/assets"):
            source = ROOT / rel
            shutil.copytree(source, target / rel, dirs_exist_ok=True)


if __name__ == "__main__":
    unittest.main()
