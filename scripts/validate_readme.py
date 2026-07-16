#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = Path("docs/examples/accepted-contract-smoke.yaml")
REJECTED = Path("docs/examples/rejected-gold-dominance.yaml")

REQUIRED_HEADINGS = [
    "Quick start",
    "Pipeline",
    "Style DNA",
    "Do and don't",
    "Supported cases",
    "Unsupported and blocked cases",
    "Background profiles",
    "Runtime contracts",
    "Contract examples",
    "Output manifest",
    "Validation",
    "Plugin package",
    "Repository structure",
    "Versioning",
    "Provenance and license",
    "Contributing",
    "Digital trace",
    "Known limitations",
]

REQUIRED_SNIPPETS = [
    "$silver-gold-image-pipeline",
    "https://github.com/sevranty/silver-gold-image-pipeline.git",
    "reference -> analysis -> policy -> locks -> scene brief -> adapter -> generation/edit -> full-size QA -> target-size QA -> correction -> technical validation -> user-visible delivery",
    "70-85%",
    "15-30%",
    "matte or satin",
    "controlled rim light",
    "minimal reflections",
    "python3 scripts/validate_readme.py",
    "python3 scripts/validate_all.py",
    "python3 scripts/build_plugin_package.py --out-dir dist-first",
    "python3 scripts/test_installation.py",
]

BANNED_MARKERS = ["finuslugi", "финуслуги", "moex", "finkit"]
UNSUPPORTED_CLAIMS = [
    r"\bis (?:an )?official marketplace (?:publication|release|listing)\b",
    r"\bautomatically (?:approves?|guarantees?) (?:visual|perceptual) quality\b",
    r"\bguarantees? pixel-perfect (?:identity|reference|style)\b",
]
PRIVATE_PATHS = [
    r"/Users/",
    r"/home/[^\"'`\s/]+/",
    r"[A-Za-z]:\\",
    r"\blocalhost\b",
    r"\b127\.0\.0\.1\b",
    r"\b192\.168\.\d+\.\d+\b",
]
PLACEHOLDERS = [r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"<(?:owner|repo|path|sha|token|placeholder)>"]


def heading_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", value).strip("-")


def load_yaml(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing YAML file: {path}")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid YAML {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"YAML root must be a mapping: {path}")
        return {}
    return data


def validate_example(data: dict, *, accepted: bool, errors: list[str]) -> None:
    label = "accepted" if accepted else "rejected"
    expected_status = "accepted" if accepted else "rejected"
    if data.get("status") != expected_status:
        errors.append(f"{label} example status must be {expected_status}")

    boundary = data.get("claim_boundary")
    if not isinstance(boundary, dict):
        errors.append(f"{label} example missing claim_boundary")
    else:
        if boundary.get("image_generator_executed") is not False:
            errors.append(f"{label} example must state image_generator_executed: false")
        if boundary.get("production_visual_quality_proven") is not False:
            errors.append(f"{label} example must state production_visual_quality_proven: false")

    materials = data.get("materials")
    if not isinstance(materials, dict):
        errors.append(f"{label} example missing materials")
        return
    silver = materials.get("declared_silver_ratio")
    gold = materials.get("declared_gold_ratio")
    if not isinstance(silver, int) or not isinstance(gold, int) or silver + gold != 100:
        errors.append(f"{label} example ratios must be integers that sum to 100")
        return

    expected = data.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{label} example missing expected")
        return
    if expected.get("manual_visual_review_required") is not True:
        errors.append(f"{label} example must require manual visual review")

    if accepted:
        if not 70 <= silver <= 85 or not 15 <= gold <= 30:
            errors.append("accepted example material ratio is outside the Silver-Gold contract")
        if expected.get("terminal_state") != "DELIVERED":
            errors.append("accepted example terminal_state must be DELIVERED")
        if expected.get("critical_defects") != []:
            errors.append("accepted example critical_defects must be empty")
    else:
        if gold <= silver or gold < 50:
            errors.append("rejected example must demonstrate gold dominance")
        defects = expected.get("critical_defects")
        if expected.get("terminal_state") != "REJECTED":
            errors.append("rejected example terminal_state must be REJECTED")
        if not isinstance(defects, list) or "gold_dominance" not in defects:
            errors.append("rejected example must include gold_dominance")
        if expected.get("user_visible_delivery_allowed") is not False:
            errors.append("rejected example must forbid user-visible delivery")


def validate(root: Path = ROOT) -> tuple[list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    readme_path = root / "README.md"
    if not readme_path.is_file():
        return ["missing README.md"], {"headings": 0, "internal_links": 0}

    text = readme_path.read_text(encoding="utf-8")
    headings = [match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    anchors = {heading_anchor(item) for item in headings}

    for heading in REQUIRED_HEADINGS:
        if heading not in headings:
            errors.append(f"missing required README heading: {heading}")
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            errors.append(f"missing required README content: {snippet}")

    lowered = text.lower()
    for marker in BANNED_MARKERS:
        if marker in lowered:
            errors.append(f"brand marker is not allowed in README: {marker}")
    for pattern in UNSUPPORTED_CLAIMS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"unsupported README claim: {pattern}")
    for pattern in PRIVATE_PATHS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"private or local path is not allowed: {pattern}")
    for pattern in PLACEHOLDERS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"placeholder is not allowed: {pattern}")

    internal_links = 0
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = unquote(match.group(1).strip())
        if target.startswith(("https://", "mailto:")):
            continue
        if target.startswith("http://"):
            errors.append(f"insecure external link: {target}")
            continue
        internal_links += 1
        if target.startswith("#"):
            if target[1:] not in anchors:
                errors.append(f"broken README heading anchor: {target}")
            continue

        path_part, _, fragment = target.partition("#")
        resolved = (root / path_part).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"README link escapes repository: {target}")
            continue
        if not resolved.is_file():
            errors.append(f"broken README file link: {target}")
            continue
        if fragment and resolved.suffix.lower() == ".md":
            linked = resolved.read_text(encoding="utf-8")
            linked_anchors = {
                heading_anchor(item)
                for item in re.findall(r"^#{1,6}\s+(.+?)\s*$", linked, flags=re.MULTILINE)
            }
            if fragment not in linked_anchors:
                errors.append(f"broken linked heading anchor: {target}")

    accepted_data = load_yaml(root / ACCEPTED, errors)
    rejected_data = load_yaml(root / REJECTED, errors)
    if accepted_data:
        validate_example(accepted_data, accepted=True, errors=errors)
    if rejected_data:
        validate_example(rejected_data, accepted=False, errors=errors)

    details = {
        "headings": len(headings),
        "internal_links": internal_links,
        "accepted_case": accepted_data.get("case_id") if accepted_data else None,
        "rejected_case": rejected_data.get("case_id") if rejected_data else None,
        "subjective_visual_quality_assessed": False,
    }
    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, details = validate(args.root)
    payload = {"status": "fail" if errors else "pass", "errors": errors, "details": details}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for error in errors:
            print(f"ERROR: {error}")
        print(
            f"README validation: {'FAIL' if errors else 'PASS'} "
            f"({details['headings']} headings, {details['internal_links']} internal links)"
        )
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
