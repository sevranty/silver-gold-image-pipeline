#!/usr/bin/env python3
"""Validate the Silver-Gold foundation contracts without network access."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "AGENTS.md",
    "docs/architecture.md",
    "docs/decision-log.md",
    "docs/roadmap.md",
    "docs/style-versioning.md",
    "docs/source-map.md",
    "skills/silver-gold-image-pipeline/references/style-spec.md",
    "skills/silver-gold-image-pipeline/references/background-profiles.md",
    "tests/cases/background-profiles.yaml",
)

RUNTIME_BANNED_TERMS = (
    "Finuslugi",
    "Финуслуги",
    "MOEX",
    "FinKit",
    "FDS",
    "#FF0508",
)

STYLE_REQUIRED_TERMS = (
    "70-85",
    "15-30",
    "matte or satin",
    "low-poly",
    "clean edges",
    "sharp folds",
    "controlled rim light",
    "minimal reflections",
    "product-light",
    "showcase-neutral",
    "Critical rejection criteria",
)

BACKGROUND_REQUIRED_TERMS = (
    "product-light",
    "showcase-neutral",
    "default",
    "pure black",
    "Transparent output",
    "Safe area",
    "Rejection criteria",
)

SOURCE_HASHES = (
    "9ba60cb1454efd657f8457f74b930c538eeba49637aa03d14984ffd8ff3961e4",
    "8bfc102c9f52597a5696f4717d37add41057caa79f047401134e799d5dde589b",
)

CASE_IDS = (
    "product-light-pass",
    "product-light-fail",
    "showcase-neutral-pass",
    "showcase-neutral-fail",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    checks = 0

    for path in REQUIRED_PATHS:
        checks += 1
        if not (ROOT / path).is_file():
            fail(errors, f"missing required file: {path}")

    for path in ROOT.rglob("*"):
        if path.is_file():
            checks += 1
            relative = path.relative_to(ROOT).as_posix()
            try:
                relative.encode("ascii")
            except UnicodeEncodeError:
                fail(errors, f"non-ASCII repository path: {relative}")

    runtime_root = ROOT / "skills"
    if runtime_root.exists():
        for path in runtime_root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for term in RUNTIME_BANNED_TERMS:
                checks += 1
                if term in text:
                    fail(errors, f"runtime brand leakage in {path.relative_to(ROOT)}: {term}")

    style = read("skills/silver-gold-image-pipeline/references/style-spec.md")
    for term in STYLE_REQUIRED_TERMS:
        checks += 1
        if term not in style:
            fail(errors, f"style contract missing term: {term}")

    background = read(
        "skills/silver-gold-image-pipeline/references/background-profiles.md"
    )
    for term in BACKGROUND_REQUIRED_TERMS:
        checks += 1
        if term not in background:
            fail(errors, f"background contract missing term: {term}")

    source_map = read("docs/source-map.md")
    for digest in SOURCE_HASHES:
        checks += 1
        if digest not in source_map:
            fail(errors, f"source map missing SHA-256: {digest}")

    cases = read("tests/cases/background-profiles.yaml")
    for case_id in CASE_IDS:
        checks += 1
        if f"id: {case_id}" not in cases:
            fail(errors, f"missing regression case: {case_id}")

    architecture = read("docs/architecture.md")
    checks += 2
    if "Source-of-truth matrix" not in architecture:
        fail(errors, "architecture missing source-of-truth matrix")
    if "surface the final image to the user" not in architecture:
        fail(errors, "architecture missing user-visible final image requirement")

    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".yaml"}
        and "docs/evidence" not in path.relative_to(ROOT).as_posix()
    )
    for marker in ("TODO", "TBD", "[placeholder]"):
        checks += 1
        if marker in all_text:
            fail(errors, f"unfinished marker found: {marker}")

    print(f"foundation checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("result: PASS")
    print("validated: architecture, style contract, background profiles, provenance, regressions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
