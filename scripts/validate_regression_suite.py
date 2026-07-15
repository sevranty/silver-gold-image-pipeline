#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CATEGORIES = {
    "product-light", "showcase-neutral", "transparency", "edit", "people", "text-logo",
    "gold-dominance", "chrome-gloss", "obsidian-drift", "noisy-texture",
    "unreadable-silhouette", "weak-rim-light", "borderline-metal-allocation",
}
WORKFLOW_MINIMUMS = {
    "simple_object": 3, "technical_object": 3, "financial_metaphor": 2,
    "badge_status": 2, "hero_object": 2, "sketch_to_render": 2,
    "multi_reference": 2, "people": 2, "text_logo": 2, "background_profile": 4,
}
STAGES = [
    "input_gate", "reference_analysis", "policy_decision", "locks", "scene_brief",
    "adapter_decision", "generation_or_edit_spec", "prompt_preflight", "generation_or_edit",
    "full_size_visual_qa", "target_size_visual_qa", "targeted_correction",
    "technical_validation", "user_visible_delivery",
]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ASCII = re.compile(r"^[\x00-\x7f]+$")
BRAND_MARKERS = ("finuslugi", "moscow exchange", "moex", "finkit", "fds ")


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    details: dict = {"subjective_visual_quality_assessed": False}
    paths = {
        "triggers": root / "tests/cases/trigger-cases.yaml",
        "workflows": root / "tests/cases/workflow-cases.yaml",
        "visual": root / "tests/cases/visual-regression-cases.yaml",
        "provenance": root / "skills/silver-gold-image-pipeline/assets/anchors/provenance.yaml",
        "repro": root / "skills/silver-gold-image-pipeline/assets/anchors/reproducibility-manifest.yaml",
        "rubric": root / "docs/visual-rubric.md",
        "builder": root / "scripts/build_regression_anchors.py",
    }
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"missing required file {name}: {path.relative_to(root)}")
    if errors:
        return errors, details

    triggers = load(paths["triggers"]).get("cases", [])
    class_counts = {key: 0 for key in ("positive", "negative", "boundary")}
    ids: set[str] = set()
    for case in triggers:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in ids:
            errors.append(f"invalid or duplicate trigger id: {cid}")
        ids.add(cid)
        cls = case.get("class")
        if cls not in class_counts:
            errors.append(f"trigger {cid}: invalid class")
        else:
            class_counts[cls] += 1
        if case.get("expected") not in {"trigger", "non_trigger"}:
            errors.append(f"trigger {cid}: invalid expected value")
        if not isinstance(case.get("request"), str) or not case["request"].strip():
            errors.append(f"trigger {cid}: empty request")
    if len(triggers) < 24:
        errors.append("trigger suite requires at least 24 cases")
    for cls, count in class_counts.items():
        if count < 8:
            errors.append(f"trigger class {cls} requires at least 8 cases")

    workflows = load(paths["workflows"]).get("cases", [])
    workflow_counts: dict[str, int] = {}
    for case in workflows:
        cid = case.get("id")
        category = case.get("category")
        workflow_counts[category] = workflow_counts.get(category, 0) + 1
        if case.get("expected_outcome") not in {"pass", "reject", "ambiguous", "block"}:
            errors.append(f"workflow {cid}: invalid outcome")
        if case.get("required_stages") != STAGES:
            errors.append(f"workflow {cid}: stage order mismatch")
        if not all(case.get(key) is True for key in (
            "full_size_qa_required", "target_size_qa_required", "reproducibility_manifest_required"
        )):
            errors.append(f"workflow {cid}: missing manual/reproducibility gate")
        if case.get("target_size_px") != 64:
            errors.append(f"workflow {cid}: target_size_px must be 64")
    if len(workflows) < 20:
        errors.append("workflow suite requires at least 20 cases")
    for category, minimum in WORKFLOW_MINIMUMS.items():
        if workflow_counts.get(category, 0) < minimum:
            errors.append(f"workflow category {category} requires at least {minimum} cases")

    visual = load(paths["visual"]).get("anchors", [])
    categories = {item.get("category") for item in visual}
    outcomes = {item.get("expected_outcome") for item in visual}
    if EXPECTED_CATEGORIES - categories:
        errors.append(f"missing visual categories: {sorted(EXPECTED_CATEGORIES - categories)}")
    if outcomes != {"accepted", "rejected", "ambiguous"}:
        errors.append("visual suite must contain accepted, rejected, and ambiguous outcomes")

    provenance_data = load(paths["provenance"])
    defaults = provenance_data.get("defaults", {})
    provenance = {item.get("id"): {**defaults, **item} for item in provenance_data.get("records", [])}
    repro = load(paths["repro"])
    repro_assets = {item.get("path"): item.get("sha256") for item in repro.get("assets", [])}
    if not (repro.get("deterministic") is True and repro.get("network_required") is False):
        errors.append("reproducibility manifest must be deterministic and offline")
    if repro.get("image_generator_used") is not False or repro.get("subjective_visual_quality_assessed") is not False:
        errors.append("reproducibility manifest makes a false generator/visual-quality claim")

    for item in visual:
        cid, rel = item.get("id"), item.get("path")
        if not isinstance(rel, str) or not ASCII.fullmatch(rel):
            errors.append(f"visual {cid}: path must be ASCII")
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"visual {cid}: missing asset {rel}")
            continue
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"visual {cid}: invalid SVG: {exc}")
        actual = digest(path)
        if item.get("sha256") != actual or not SHA256.fullmatch(str(item.get("sha256", ""))):
            errors.append(f"visual {cid}: SHA-256 mismatch")
        if repro_assets.get(rel) != actual:
            errors.append(f"visual {cid}: reproducibility manifest mismatch")
        if item.get("synthetic_qa_anchor") is not True or item.get("image_generator_output") is not False:
            errors.append(f"visual {cid}: synthetic/generator boundary invalid")
        if not all(item.get(key) is True for key in (
            "manual_review_required", "full_size_review_required", "target_size_review_required"
        )) or item.get("target_size_px") != 64:
            errors.append(f"visual {cid}: full-size and target-size manual review required")
        silver, gold = item.get("declared_silver_ratio"), item.get("declared_gold_ratio")
        if not isinstance(silver, int) or not isinstance(gold, int) or silver + gold != 100:
            errors.append(f"visual {cid}: declared ratios must be integers summing to 100")
        if item.get("expected_outcome") == "accepted" and not (70 <= silver <= 85 and 15 <= gold <= 30):
            errors.append(f"visual {cid}: accepted ratio outside contract")
        record = provenance.get(item.get("provenance_id"))
        if not record or record.get("path") != rel or record.get("sha256") != actual:
            errors.append(f"visual {cid}: provenance path/hash mismatch")
        elif any(record.get(key) is not False for key in ("third_party_content", "pii", "exif", "generator_output")):
            errors.append(f"visual {cid}: provenance privacy/source boundary invalid")
        elif record.get("license_status") != "original_project_asset":
            errors.append(f"visual {cid}: invalid license status")

    if len(provenance) != len(visual) or len(repro_assets) != len(visual):
        errors.append("visual, provenance, and reproducibility record counts must match")

    spec = importlib.util.spec_from_file_location("anchor_builder", paths["builder"])
    if spec is None or spec.loader is None:
        errors.append("cannot load anchor materializer")
    else:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            rebuilt = module.build(Path(temp))
            for rel, expected in rebuilt.items():
                repo_rel = f"skills/silver-gold-image-pipeline/assets/{rel}"
                if repro_assets.get(repo_rel) != expected:
                    errors.append(f"reproduced snapshot mismatch: {repo_rel}")

    rubric = paths["rubric"].read_text(encoding="utf-8").casefold()
    for phrase in ("full-size review", "target-size review", "does not automate subjective visual quality", "not outputs from an image generator", "ambiguous"):
        if phrase not in rubric:
            errors.append(f"visual rubric missing phrase: {phrase}")

    scan_paths = [paths["visual"], paths["provenance"], paths["repro"], paths["rubric"]]
    scan_paths.extend(root.glob("skills/silver-gold-image-pipeline/assets/examples/**/*.svg"))
    for path in scan_paths:
        text = path.read_text(encoding="utf-8").casefold()
        for marker in BRAND_MARKERS:
            if marker in text:
                errors.append(f"brand leakage in {path.relative_to(root)}: {marker!r}")

    details.update({
        "trigger_cases": len(triggers), "trigger_class_counts": class_counts,
        "workflow_cases": len(workflows), "workflow_category_counts": workflow_counts,
        "visual_anchors": len(visual), "visual_outcomes": sorted(outcomes),
        "coverage_categories": sorted(categories), "reproducibility_verified": not errors,
    })
    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SGP trigger, workflow, and visual regression suite.")
    parser.add_argument("root", nargs="?", default=str(ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, details = validate(Path(args.root).resolve())
    payload = {"status": "fail" if errors else "pass", "errors": errors, "details": details, "subjective_visual_quality_assessed": False}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if args.json else f"regression suite: {'FAIL' if errors else 'PASS'}\n" + "\n".join(f"- {e}" for e in errors) + "\n" + json.dumps(details, ensure_ascii=False, sort_keys=True))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
