#!/usr/bin/env python3
"""Build, validate, unpack, and inspect the standalone plugin package."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("sgp_build_plugin_package", SCRIPTS / "build_plugin_package.py")
VALIDATOR = load_module("sgp_validate_plugin_package", SCRIPTS / "validate_plugin_package.py")


def smoke(root: Path) -> tuple[list[str], dict[str, Any]]:
    root = root.resolve()
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary = Path(temporary_directory)
        result = BUILDER.build(root, temporary / "package")
        archive = Path(result["archive"])
        manifest = Path(result["manifest"])
        checksum = Path(result["checksum"])

        package_errors, package_details = VALIDATOR.validate(
            root,
            archive=archive,
            manifest=manifest,
            checksum=checksum,
        )
        errors.extend(package_errors)

        install = temporary / "installed"
        install.mkdir()
        if not errors:
            with zipfile.ZipFile(archive) as package:
                package.extractall(install)

        plugin_path = install / ".codex-plugin/plugin.json"
        if not plugin_path.is_file():
            errors.append("installed plugin manifest missing")
            plugin: dict[str, Any] = {}
        else:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))

        skills = plugin.get("skills", [])
        if skills != ["skills/silver-gold-image-pipeline"]:
            errors.append("installed plugin skill path mismatch")
            skill_root = install / "skills/silver-gold-image-pipeline"
        else:
            skill_root = install / skills[0]

        skill = skill_root / "SKILL.md"
        agent = skill_root / "agents/openai.yaml"
        if not skill.is_file() or not agent.is_file():
            errors.append("installed skill or agent metadata missing")
        else:
            skill_text = skill.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---", skill_text, re.S)
            frontmatter = yaml.safe_load(match.group(1)) if match else {}
            if frontmatter.get("name") != plugin.get("id"):
                errors.append("installed skill id mismatch")
            references = sorted(set(re.findall(r"`(references/[^`]+)`", skill_text)))
            if not references:
                errors.append("installed SKILL contains no runtime reference links")
            for relative in references:
                if not (skill_root / relative).is_file():
                    errors.append(f"installed reference missing: {relative}")

        forbidden_roots = ("docs", "tests", "release", "source-documents")
        for forbidden in forbidden_roots:
            if (install / forbidden).exists():
                errors.append(f"installed package contains forbidden root: {forbidden}")
        if any((install / "skills").rglob("assets/examples")):
            errors.append("installed package contains visual regression examples")
        if any((install / "skills").rglob("assets/anchors")):
            errors.append("installed package contains visual regression anchors")

        installed_files = sorted(
            path.relative_to(install).as_posix() for path in install.rglob("*") if path.is_file()
        )
        details = {
            "archive_sha256": result["archive_sha256"],
            "archive_files": package_details.get("archive_files", 0),
            "installed_files": len(installed_files),
            "standalone_root": skill_root.relative_to(install).as_posix(),
        }
        return errors, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors, details = smoke(args.root.resolve())
    payload = {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "details": details,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"installation smoke: {'FAIL' if errors else 'PASS'}")
        for error in errors:
            print(f"- {error}")
        print(json.dumps(details, sort_keys=True))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
