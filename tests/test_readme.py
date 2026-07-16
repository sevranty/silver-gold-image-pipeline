from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/validate_readme.py"


def load_module():
    spec = importlib.util.spec_from_file_location("readme_validator_tests", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module()


class ReadmeValidationTests(unittest.TestCase):
    def copy_repo(self, parent: Path) -> Path:
        target = parent / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "dist*", "__pycache__", ".validation-pycache"),
        )
        return target

    def mutate_readme(self, root: Path, old: str, new: str) -> None:
        path = root / "README.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_current_readme_passes(self) -> None:
        errors, details = VALIDATOR.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(details["headings"], 18)
        self.assertGreaterEqual(details["internal_links"], 10)

    def test_broken_link_and_missing_heading_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_repo(Path(directory))
            self.mutate_readme(root, "skills/silver-gold-image-pipeline/SKILL.md", "missing/SKILL.md")
            errors, _ = VALIDATOR.validate(root)
            self.assertTrue(any("broken README file link" in error for error in errors))

        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_repo(Path(directory))
            self.mutate_readme(root, "## Pipeline", "## Flow")
            errors, _ = VALIDATOR.validate(root)
            self.assertIn("missing required README heading: Pipeline", errors)

    def test_placeholder_private_path_brand_and_claim_fail(self) -> None:
        mutations = [
            ("## Known limitations", "TODO\n\n## Known limitations", "placeholder"),
            ("## Known limitations", "/Users/example/project\n\n## Known limitations", "private or local path"),
            ("## Known limitations", "MOEX\n\n## Known limitations", "brand marker"),
            (
                "## Known limitations",
                "is an official marketplace publication\n\n## Known limitations",
                "unsupported README claim",
            ),
        ]
        for old, new, expected in mutations:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root = self.copy_repo(Path(directory))
                self.mutate_readme(root, old, new)
                errors, _ = VALIDATOR.validate(root)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_invalid_rejected_example_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_repo(Path(directory))
            path = root / "docs/examples/rejected-gold-dominance.yaml"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            data["materials"]["declared_silver_ratio"] = 80
            data["materials"]["declared_gold_ratio"] = 20
            data["expected"]["critical_defects"] = []
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            errors, _ = VALIDATOR.validate(root)
            self.assertTrue(any("gold dominance" in error for error in errors))
            self.assertTrue(any("gold_dominance" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
