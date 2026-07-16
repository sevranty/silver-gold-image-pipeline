#!/usr/bin/env python3
"""Validate the Silver-Gold plugin source tree and built runtime archive."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

VERSIONS = {
    "skill_version": "0.1.0",
    "pipeline_core_version": "0.2.0",
    "style_core_version": "0.1.0",
    "background_profiles_version": "0.1.0",
    "prompt_schema_version": "0.1.0",
    "qa_schema_version": "0.1.0",
    "manifest_schema_version": "0.1.0",
}

EXPECTED_PLUGIN = {
    "schema_version": "1.0.0",
    "id": "silver-gold-image-pipeline",
    "version": "0.1.0",
    "display_name": "Silver-Gold Image Pipeline",
    "repository": "https://github.com/sevranty/silver-gold-image-pipeline",
    "homepage": "https://github.com/sevranty/silver-gold-image-pipeline#readme",
    "license": "MIT",
}

EXCLUDED_PREFIXES = ("docs/", "tests/", "release/", "dist/", "source-documents/")
EXCLUDED_MARKERS = ("/assets/examples/", "/assets/anchors/", "__pycache__")
BRAND_MARKERS = ("finuslugi", "финуслуги", "moscow exchange", "moex", "finkit")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".txt", ".py"}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_builder_module():
    path = SCRIPTS / "build_plugin_package.py"
    spec = importlib.util.spec_from_file_location("sgp_build_plugin_package", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load package builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_archive_path(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def excluded_archive_path(name: str) -> bool:
    return (
        name.startswith(EXCLUDED_PREFIXES)
        or any(marker in name for marker in EXCLUDED_MARKERS)
        or name.endswith(".pyc")
    )


def parse_checksum(path: Path) -> tuple[str, str]:
    parts = path.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2:
        raise ValueError("checksum file must contain '<sha256>  <filename>'")
    digest, filename = parts
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("checksum file contains invalid SHA-256")
    return digest, filename


def validate(
    root: Path,
    archive: Path | None = None,
    manifest: Path | None = None,
    checksum: Path | None = None,
) -> tuple[list[str], dict[str, Any]]:
    root = root.resolve()
    errors: list[str] = []
    details: dict[str, Any] = {}

    manifest_path = root / ".codex-plugin/plugin.json"
    contract_path = root / "release/package-contract.yaml"
    skill_path = root / "skills/silver-gold-image-pipeline/SKILL.md"
    agent_path = root / "skills/silver-gold-image-pipeline/agents/openai.yaml"
    required_packaging = (
        manifest_path,
        contract_path,
        skill_path,
        agent_path,
        root / "LICENSE",
        root / "CHANGELOG.md",
        root / "NOTICE.md",
        root / "docs/style-versioning.md",
    )
    for path in required_packaging:
        if not path.is_file():
            errors.append(f"missing required packaging file: {path.relative_to(root)}")
    if errors:
        return errors, details

    try:
        plugin = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"invalid plugin manifest: {error}"], details
    try:
        contract = load_yaml(contract_path)
        openai = load_yaml(agent_path)
    except (OSError, yaml.YAMLError) as error:
        return [f"invalid packaging YAML: {error}"], details

    for key, value in EXPECTED_PLUGIN.items():
        if plugin.get(key) != value:
            errors.append(f"plugin manifest {key} mismatch")
    if plugin.get("skills") != ["skills/silver-gold-image-pipeline"]:
        errors.append("plugin manifest must declare exactly one canonical skill path")
    if not isinstance(plugin.get("description"), str) or not plugin["description"].strip():
        errors.append("plugin manifest description is required")

    interface = openai.get("interface", {}) if isinstance(openai, dict) else {}
    if interface.get("display_name") != plugin.get("display_name"):
        errors.append("openai display name mismatch")
    metadata_text = " ".join(
        str(interface.get(key, "")) for key in ("short_description", "default_prompt")
    ).casefold()
    for marker in ("visual qa", "user-visible", "final delivery"):
        if marker not in metadata_text:
            errors.append(f"openai metadata missing delivery marker: {marker}")
    if any(marker in metadata_text for marker in BRAND_MARKERS):
        errors.append("brand-specific marker in agent metadata")

    frontmatter = re.match(r"^---\n(.*?)\n---", skill_path.read_text(encoding="utf-8"), re.S)
    if frontmatter is None:
        errors.append("SKILL front matter missing")
    else:
        try:
            frontmatter_data = yaml.safe_load(frontmatter.group(1))
        except yaml.YAMLError as error:
            errors.append(f"SKILL front matter invalid: {error}")
        else:
            if frontmatter_data.get("name") != plugin.get("id"):
                errors.append("SKILL front matter name mismatch")

    if contract.get("package_version") != plugin.get("version"):
        errors.append("package/plugin version mismatch")
    if contract.get("plugin_manifest_version") != plugin.get("schema_version"):
        errors.append("plugin manifest schema version mismatch")
    if contract.get("versions") != VERSIONS:
        errors.append("package contract versions mismatch")
    if contract.get("runtime_root") != "skills/silver-gold-image-pipeline":
        errors.append("package runtime_root mismatch")
    if contract.get("publish_tag_in_packaging_task") is not False:
        errors.append("packaging task must not publish the release tag")

    versioning = (root / "docs/style-versioning.md").read_text(encoding="utf-8")
    for key, value in {**VERSIONS, "plugin_manifest_version": "1.0.0"}.items():
        if f"{key}: {value}" not in versioning:
            errors.append(f"versioning document missing {key}: {value}")

    visual_path = root / "tests/cases/visual-regression-cases.yaml"
    if visual_path.is_file():
        visual = load_yaml(visual_path)
        if visual.get("style_core_version") != "0.1.0":
            errors.append("visual regression style_core_version mismatch")
        if visual.get("qa_schema_version") != "0.1.0":
            errors.append("visual regression qa_schema_version mismatch")

    required_relpaths = contract.get("required_runtime_files", [])
    if not isinstance(required_relpaths, list) or not required_relpaths:
        errors.append("package contract required_runtime_files must be a non-empty list")
        required_relpaths = []
    for relpath in required_relpaths:
        path = root / relpath
        if not path.is_file():
            errors.append(f"missing required runtime file: {relpath}")
    details["source_required_files"] = len(required_relpaths)

    if archive is None:
        return errors, details

    archive = archive.resolve()
    if not archive.is_file():
        errors.append(f"archive not found: {archive}")
        return errors, details

    builder = load_builder_module()
    expected_paths = [path.relative_to(root).as_posix() for path in builder.source_files(root)]
    archive_bytes = archive.read_bytes()
    archive_hash = hash_bytes(archive_bytes)
    details["archive_sha256"] = archive_hash

    try:
        with zipfile.ZipFile(archive) as package:
            names = package.namelist()
            if names != sorted(names):
                errors.append("archive file list is not sorted")
            if len(names) != len(set(names)):
                errors.append("archive contains duplicate paths")
            if names != expected_paths:
                errors.append("archive file list mismatch")
            for name in names:
                if not safe_archive_path(name):
                    errors.append(f"unsafe archive path: {name}")
                if excluded_archive_path(name):
                    errors.append(f"archive includes excluded content: {name}")
                try:
                    name.encode("ascii")
                except UnicodeEncodeError:
                    errors.append(f"non-ASCII archive path: {name}")

            for required in required_relpaths:
                if required not in names:
                    errors.append(f"archive missing required runtime file: {required}")

            for info in package.infolist():
                if info.is_dir():
                    errors.append(f"archive contains directory entry: {info.filename}")
                    continue
                data = package.read(info.filename)
                source_path = root / info.filename
                if not source_path.is_file():
                    errors.append(f"archive path has no source file: {info.filename}")
                    continue
                if hash_bytes(data) != hash_bytes(source_path.read_bytes()):
                    errors.append(f"archive byte mismatch: {info.filename}")
                if PurePosixPath(info.filename).suffix.casefold() in TEXT_SUFFIXES:
                    try:
                        text = data.decode("utf-8")
                    except UnicodeDecodeError:
                        errors.append(f"archive text file is not UTF-8: {info.filename}")
                        continue
                    folded = text.casefold()
                    if any(marker in folded for marker in BRAND_MARKERS):
                        errors.append(f"archive brand leakage: {info.filename}")
                    for pattern in SECRET_PATTERNS:
                        if pattern.search(text):
                            errors.append(f"archive secret-like value: {info.filename}")
                            break
    except zipfile.BadZipFile as error:
        errors.append(f"invalid ZIP archive: {error}")
        return errors, details

    details["archive_files"] = len(expected_paths)

    expected_records = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": hash_bytes(path.read_bytes()),
            "size_bytes": path.stat().st_size,
        }
        for path in builder.source_files(root)
    ]
    if manifest is not None:
        try:
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid package manifest: {error}")
        else:
            if manifest_data.get("schema_version") != "1.0.0":
                errors.append("package manifest schema_version mismatch")
            if manifest_data.get("package_version") != plugin.get("version"):
                errors.append("package manifest version mismatch")
            if manifest_data.get("archive") != archive.name:
                errors.append("package manifest archive name mismatch")
            if manifest_data.get("archive_sha256") != archive_hash:
                errors.append("package manifest archive checksum mismatch")
            if manifest_data.get("files") != expected_records:
                errors.append("package manifest file records mismatch")

    if checksum is not None:
        try:
            checksum_hash, checksum_filename = parse_checksum(checksum)
        except (OSError, ValueError) as error:
            errors.append(f"invalid checksum file: {error}")
        else:
            if checksum_hash != archive_hash:
                errors.append("checksum file does not match archive bytes")
            if checksum_filename != archive.name:
                errors.append("checksum file archive name mismatch")

    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--checksum", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors, details = validate(
        args.root.resolve(),
        args.archive.resolve() if args.archive else None,
        args.manifest.resolve() if args.manifest else None,
        args.checksum.resolve() if args.checksum else None,
    )
    payload = {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "details": details,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"plugin package: {'FAIL' if errors else 'PASS'}")
        for error in errors:
            print(f"- {error}")
        print(json.dumps(details, sort_keys=True))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
