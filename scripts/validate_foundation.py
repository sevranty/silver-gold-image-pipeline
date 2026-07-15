#!/usr/bin/env python3
"""Validate Silver-Gold foundation contracts without network access."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

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
    "Рымарь",
    "Хромова",
    "premium fintech aesthetic",
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
    "Critical rejection criteria",
    "Background contract: `background-profiles.md`",
)

STYLE_FORBIDDEN_OWNERSHIP_TERMS = (
    "recommended relative luminance",
    "Transparent output is a delivery mode",
    "final asset cannot be surfaced to the user",
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

SOURCE_INPUTS = {
    "style": {
        "filename": "FDS [visual-style] Стиль Silver-Gold v3.1 (2026-02-24).docx",
        "sha256": "9ba60cb1454efd657f8457f74b930c538eeba49637aa03d14984ffd8ff3961e4",
    },
    "architecture": {
        "filename": "FDS [visual-architecture] Архитектура визуальных стилей Финуслуг v2 (август 2025).docx",
        "sha256": "8bfc102c9f52597a5696f4717d37add41057caa79f047401134e799d5dde589b",
    },
}

EXPECTED_CASES = {
    "product-light-pass": {
        "profile": "product-light",
        "expected": "pass",
        "required_list": "assertions",
        "required_items": {
            "silver_separates_from_background",
            "controlled_contact_shadow",
            "no_mirror_glare",
            "safe_area_preserved",
        },
    },
    "product-light-fail": {
        "profile": "product-light",
        "expected": "fail",
        "required_list": "defects",
        "required_items": {
            "silver_dissolves_into_background",
            "broad_white_glare",
            "gold_used_as_primary_edge_separation",
        },
    },
    "showcase-neutral-pass": {
        "profile": "showcase-neutral",
        "expected": "pass",
        "required_list": "assertions",
        "required_items": {
            "silver_remains_dominant_structural_material",
            "silhouette_separates",
            "neutral_key_and_rim_light",
            "full_primary_silhouette_preserved",
        },
    },
    "showcase-neutral-fail": {
        "profile": "showcase-neutral",
        "expected": "fail",
        "required_list": "defects",
        "required_items": {
            "black_gold_dominance",
            "obsidian_like_read",
            "silver_not_dominant",
            "silhouette_merges_with_background",
        },
    },
}

SOURCE_OF_TRUTH_ROWS = (
    "| Repository boundaries and dependency direction | `docs/architecture.md` |",
    "| Accepted architecture decisions | `docs/decision-log.md` |",
    "| Visual style invariants | `skills/silver-gold-image-pipeline/references/style-spec.md` |",
    "| Background selection and delivery behavior | `skills/silver-gold-image-pipeline/references/background-profiles.md` |",
    "| Source provenance and normalization | `docs/source-map.md` |",
    "| Version semantics | `docs/style-versioning.md` |",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style-source", type=Path)
    parser.add_argument("--architecture-source", type=Path)
    return parser.parse_args()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def normalized_name(path: Path) -> str:
    return unicodedata.normalize("NFC", path.name)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def term_present(text: str, term: str) -> bool:
    folded_text = text.casefold()
    folded_term = term.casefold()
    if all(character.isalnum() for character in folded_term):
        pattern = rf"(?<!\w){re.escape(folded_term)}(?!\w)"
        return re.search(pattern, folded_text, flags=re.UNICODE) is not None
    return folded_term in folded_text


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_cases_fixture(text: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata: dict[str, Any] = {}
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_list: str | None = None

    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("schema_version:") or raw.startswith("contract_version:"):
            key, value = raw.split(":", 1)
            metadata[key.strip()] = parse_scalar(value)
            continue
        if raw == "cases:":
            continue
        if raw.startswith("  - id:"):
            if current is not None:
                cases.append(current)
            current = {"id": parse_scalar(raw.split(":", 1)[1])}
            current_list = None
            continue
        if current is None:
            raise ValueError(f"unexpected fixture line {line_number}: {raw}")
        if raw.startswith("    ") and not raw.startswith("      - "):
            key, value = raw.strip().split(":", 1)
            if value.strip():
                current[key] = parse_scalar(value)
                current_list = None
            else:
                current[key] = []
                current_list = key
            continue
        if raw.startswith("      - ") and current_list is not None:
            current[current_list].append(parse_scalar(raw.strip()[2:]))
            continue
        raise ValueError(f"unsupported fixture syntax at line {line_number}: {raw}")

    if current is not None:
        cases.append(current)
    return metadata, cases


def channel_to_linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_color) is None:
        raise ValueError(f"invalid hex color: {hex_color}")
    values = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    red, green, blue = (channel_to_linear(value) for value in values)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def extract_profile_section(text: str, profile: str, next_heading: str) -> str:
    start_marker = f"## 3. Profile: {profile}" if profile == "product-light" else f"## 4. Profile: {profile}"
    start = text.index(start_marker)
    end = text.index(next_heading, start)
    return text[start:end]


def extract_luminance_range(section: str) -> tuple[float, float]:
    match = re.search(r"recommended relative luminance: ([0-9.]+)-([0-9.]+);", section)
    if match is None:
        raise ValueError("relative luminance range not found")
    return float(match.group(1)), float(match.group(2))


def validate_source_file(
    errors: list[str], checks: list[int], label: str, path: Path, expected: dict[str, str]
) -> None:
    checks[0] += 1
    if not path.is_file():
        fail(errors, f"{label} source is not a file: {path}")
        return
    checks[0] += 1
    if normalized_name(path) != unicodedata.normalize("NFC", expected["filename"]):
        fail(errors, f"{label} source filename mismatch: {path.name}")
    checks[0] += 1
    actual_hash = sha256_file(path)
    if actual_hash != expected["sha256"]:
        fail(errors, f"{label} source SHA-256 mismatch: {actual_hash}")


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    checks = [0]

    if bool(args.style_source) != bool(args.architecture_source):
        fail(errors, "provide both --style-source and --architecture-source, or neither")

    for path in REQUIRED_PATHS:
        checks[0] += 1
        if not (ROOT / path).is_file():
            fail(errors, f"missing required file: {path}")

    for path in ROOT.rglob("*"):
        if path.is_file():
            checks[0] += 1
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
                checks[0] += 1
                if term_present(text, term):
                    fail(errors, f"runtime brand leakage in {path.relative_to(ROOT)}: {term}")

    style = read("skills/silver-gold-image-pipeline/references/style-spec.md")
    for term in STYLE_REQUIRED_TERMS:
        checks[0] += 1
        if term not in style:
            fail(errors, f"style contract missing term: {term}")
    for term in STYLE_FORBIDDEN_OWNERSHIP_TERMS:
        checks[0] += 1
        if term in style:
            fail(errors, f"style contract duplicates another contract owner: {term}")

    background = read("skills/silver-gold-image-pipeline/references/background-profiles.md")
    for term in BACKGROUND_REQUIRED_TERMS:
        checks[0] += 1
        if term not in background:
            fail(errors, f"background contract missing term: {term}")

    for profile, next_heading in (
        ("product-light", "## 4. Profile: showcase-neutral"),
        ("showcase-neutral", "## 5. Transparent output"),
    ):
        section = extract_profile_section(background, profile, next_heading)
        minimum, maximum = extract_luminance_range(section)
        checks[0] += 1
        if not 0 <= minimum < maximum <= 1:
            fail(errors, f"invalid luminance range for {profile}: {minimum}-{maximum}")
        example_line = next(
            (line for line in section.splitlines() if line.startswith("Examples of acceptable")),
            "",
        )
        examples = re.findall(r"#[0-9A-Fa-f]{6}", example_line)
        checks[0] += 1
        if not examples:
            fail(errors, f"no background examples for {profile}")
        for example in examples:
            checks[0] += 1
            luminance = relative_luminance(example)
            if not minimum <= luminance <= maximum:
                fail(
                    errors,
                    f"{profile} example {example} luminance {luminance:.6f} outside {minimum}-{maximum}",
                )

    source_map = read("docs/source-map.md")
    for expected in SOURCE_INPUTS.values():
        checks[0] += 2
        if expected["filename"] not in source_map:
            fail(errors, f"source map missing filename: {expected['filename']}")
        if expected["sha256"] not in source_map:
            fail(errors, f"source map missing SHA-256: {expected['sha256']}")

    if args.style_source and args.architecture_source:
        validate_source_file(errors, checks, "style", args.style_source, SOURCE_INPUTS["style"])
        validate_source_file(
            errors, checks, "architecture", args.architecture_source, SOURCE_INPUTS["architecture"]
        )

    fixture_text = read("tests/cases/background-profiles.yaml")
    try:
        metadata, cases = parse_cases_fixture(fixture_text)
    except ValueError as error:
        fail(errors, str(error))
        metadata, cases = {}, []

    checks[0] += 2
    if metadata.get("schema_version") != 1:
        fail(errors, "background fixture schema_version must be 1")
    if metadata.get("contract_version") != "0.1.0":
        fail(errors, "background fixture contract_version must be 0.1.0")

    case_ids = [case.get("id") for case in cases]
    checks[0] += 2
    if len(case_ids) != len(set(case_ids)):
        fail(errors, "duplicate background regression case IDs")
    if set(case_ids) != set(EXPECTED_CASES):
        fail(errors, f"background regression case set mismatch: {case_ids}")

    profile_ranges = {
        "product-light": extract_luminance_range(
            extract_profile_section(background, "product-light", "## 4. Profile: showcase-neutral")
        ),
        "showcase-neutral": extract_luminance_range(
            extract_profile_section(background, "showcase-neutral", "## 5. Transparent output")
        ),
    }

    for case in cases:
        case_id = str(case.get("id"))
        expected = EXPECTED_CASES.get(case_id)
        if expected is None:
            continue
        checks[0] += 2
        if case.get("profile") != expected["profile"]:
            fail(errors, f"{case_id} profile mismatch")
        if case.get("expected") != expected["expected"]:
            fail(errors, f"{case_id} expected outcome mismatch")

        silver_ratio = case.get("silver_ratio")
        gold_ratio = case.get("gold_ratio")
        checks[0] += 4
        if not isinstance(silver_ratio, int) or not 70 <= silver_ratio <= 85:
            fail(errors, f"{case_id} invalid silver_ratio: {silver_ratio}")
        if not isinstance(gold_ratio, int) or not 15 <= gold_ratio <= 30:
            fail(errors, f"{case_id} invalid gold_ratio: {gold_ratio}")
        if isinstance(silver_ratio, int) and isinstance(gold_ratio, int) and silver_ratio + gold_ratio != 100:
            fail(errors, f"{case_id} ratios do not sum to 100")

        background_hex = case.get("background_hex")
        if not isinstance(background_hex, str):
            fail(errors, f"{case_id} missing background_hex")
        else:
            try:
                luminance = relative_luminance(background_hex)
            except ValueError as error:
                fail(errors, f"{case_id}: {error}")
            else:
                minimum, maximum = profile_ranges[expected["profile"]]
                if expected["expected"] == "pass" and not minimum <= luminance <= maximum:
                    fail(errors, f"{case_id} pass background outside profile luminance range")
                if case_id == "showcase-neutral-fail" and luminance != 0:
                    fail(errors, f"{case_id} must use pure black")

        required_list = expected["required_list"]
        actual_items = set(case.get(required_list, []))
        checks[0] += 2
        if not expected["required_items"].issubset(actual_items):
            missing = sorted(expected["required_items"] - actual_items)
            fail(errors, f"{case_id} missing {required_list}: {missing}")
        forbidden_list = "defects" if required_list == "assertions" else "assertions"
        if case.get(forbidden_list):
            fail(errors, f"{case_id} must not define {forbidden_list}")

    architecture = read("docs/architecture.md")
    for row in SOURCE_OF_TRUTH_ROWS:
        checks[0] += 1
        if row not in architecture:
            fail(errors, f"architecture source-of-truth row missing: {row}")
    checks[0] += 1
    if "surface the final image to the user" not in architecture:
        fail(errors, "architecture missing user-visible final image requirement")

    decision_log = read("docs/decision-log.md")
    for adr in ("ADR-0001", "ADR-0002", "ADR-0003"):
        checks[0] += 1
        if adr not in decision_log:
            fail(errors, f"decision log missing {adr}")

    roadmap = read("docs/roadmap.md")
    checks[0] += 1
    if "#1 orchestration remains open" not in roadmap:
        fail(errors, "roadmap incorrectly treats orchestration issue #1 as complete")

    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".yaml", ".json"}
        and "docs/evidence" not in path.relative_to(ROOT).as_posix()
    )
    for marker in ("TODO", "TBD", "[placeholder]"):
        checks[0] += 1
        if marker in all_text:
            fail(errors, f"unfinished marker found: {marker}")

    checks[0] += 4
    if not term_present("lowercase finuslugi marker", "Finuslugi"):
        fail(errors, "brand matcher misses lowercase Finuslugi")
    if not term_present("ФИНУСЛУГИ", "Финуслуги"):
        fail(errors, "brand matcher misses uppercase Cyrillic")
    if term_present("contract fields remain valid", "FDS"):
        fail(errors, "brand matcher produces FDS false positive inside fields")
    if abs(relative_luminance("#24262B") - 0.0193571251) > 0.000001:
        fail(errors, "relative luminance implementation self-test failed")

    print(f"foundation checks: {checks[0]}")
    if args.style_source and args.architecture_source:
        print("source-byte verification: enabled")
    else:
        print("source-byte verification: not requested")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("result: PASS")
    print(
        "validated: architecture, ownership boundaries, style contract, background profiles, "
        "provenance metadata, regression semantics"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
