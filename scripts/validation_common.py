#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

EXIT_OK = 0
EXIT_VALIDATION = 2
EXIT_USAGE = 64

SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home|tmp|var|private|mnt)/"),
    re.compile(r"\b[A-Za-z]:\\"),
)


def load_data(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ascii_path(path: Path) -> bool:
    try:
        path.as_posix().encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def has_secret(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def has_absolute_local_path(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return any(pattern.search(text) for pattern in ABSOLUTE_PATH_PATTERNS)


def emit(tool: str, path: str | None, errors: list[str], warnings: list[str] | None = None, details: dict[str, Any] | None = None, as_json: bool = False) -> int:
    warnings = warnings or []
    payload = {
        "tool": tool,
        "path": path,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "details": details or {},
        "subjective_visual_quality_assessed": False,
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{tool}: {payload['status'].upper()}")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
    return EXIT_OK if not errors else EXIT_VALIDATION
