#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_OUTCOMES = {"accepted", "rejected", "ambiguous"}
WORKFLOW_OUTCOMES = {"pass", "reject", "ambiguous", "block"}
EXPECTED_CATEGORIES = {
    "product-light", "showcase-neutral", "transparency", "edit", "people", "text-logo",
    "gold-dominance", "chrome-gloss", "obsidian-drift", "noisy-texture",
    "unreadable-silhouette", "weak-rim-light", "borderline-metal-allocation",
}
REQUIRED_WORKFLOW_CATEGORIES = {
    "simple_object": 3, "technical_object": 3, "financial_metaphor": 2,
    "badge_status": 2, "hero_object": 2, "sketch_to_render": 2,
    "multi_reference": 2, "people": 2, "text_logo": 2, "background_profile": 4,
}
REQUIRED_STAGES = [
    "input_gate", "reference_analysis", "policy_decision", "locks", "scene_brief",
    "adapter_decision", "generation_or_edit_spec", "prompt_preflight", "generation_or_edit",
    "full_size_visual_qa", "target_size_visual_qa", "targeted_correction",
    "technical_validation", "user_visible_delivery",
]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ASCII = re.compile(r"^[\x00-\x7f]+$")
FORBIDDEN_RUNTIME_MARKERS = ("finuslugi", "moscow exchange", "moex", "finkit", "fds ")


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    return data


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    details: dict = {"subjective_visual_quality_assessed": False}
    trigger_path = root / "tests/cases/trigger-cases.yaml"
    workflow_path = root / "tests/cases/workflow-cases.yaml"
    visual_path = root / "tests/cases/visual-regression-cases.yaml"
    provenance_path = root / "skills/silver-gold-image-pipeline/assets/anchors/provenance.yaml"
    reproducibility_path = root / "skills/silver-gold-image-pipeline/assets/anchors/reproducibility-manifest.yaml"
    rubric_path = root / "docs/visual-rubric.md"
    builder_path = root / "scripts/build_regression_anchors.py"
    for path in (trigger_path, workflow_path, visual_path, provenance_path, reproducibility_path, rubric_path, builder_path):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(root)}")
    if errors:
        return errors, details

    triggers = load_yaml(trigger_path).get("cases", [])
    if len(triggers) < 24:
        errors.append("trigger suite must contain at least 24 cases")
    class_counts = {name: 0 for name in ("positive", "negative", "boundary")}
    trigger_ids: set[str] = set()
    for case in triggers:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in trigger_ids:
            errors.append(f"invalid or duplicate trigger id: {cid}")
        trigger_ids.add(cid)
        cls = case.get("class")
        if cls not in class_counts:
            errors.append(f"trigger {cid}: invalid class")
        else:
            class_counts[cls] += 1
        if case.get("expected") not in {"trigger", "non_trigger"}:
            errors.append(f"trigger {cid}: invalid expected value")
        if not isinstance(case.get("request"), str) or not case["request"].strip():
            errors.append(f"trigger {cid}: empty request")
    for cls, count in class_counts.items():
        if count < 8:
            errors.append(f"trigger class {cls} requires at least 8 cases")

    workflows = load_yaml(workflow_path).get("cases", [])
    if len(workflows) < 20:
        errors.append("workflow suite must contain at least 20 cases")
    workflow_counts: dict[str, int] = {}
    for case in workflows:
        cid = case.get("id")
        cat = case.get("category")
        workflow_counts[cat] = workflow_counts.get(cat, 0) + 1
        if case.get("expected_outcome") not in WORKFLOW_OUTCOMES:
            errors.append(f"workflow {cid}: invalid outcome")
        if case.get("required_stages") != REQUIRED_STAGES:
            errors.append(f"workflow {cid}: stage order mismatch")
        if case.get("full_size_qa_required") is not True or case.get("target_size_qa_required") is not True:
            errors.append(f"workflow {cid}: both visual QA sizes are mandatory")
        if case.get("target_size_px") != 64:
            errors.append(f"workflow {cid}: target_size_px must be 64")
        if case.get("reproducibility_manifest_required") is not True:
            errors.append(f"workflow {cid}: reproducibility manifest required")
    for cat, minimum in REQUIRED_WORKFLOW_CATEGORIES.items():
        if workflow_counts.get(cat, 0) < minimum:
            errors.append(f"workflow category {cat} requires at least {minimum} cases")

    visual = load_yaml(visual_path).get("anchors", [])
    categories = {item.get("category") for item in visual}
    missing_categories = EXPECTED_CATEGORIES - categories
    if missing_categories:
        errors.append(f"missing visual categories: {sorted(missing_categories)}")
    outcomes = {item.get("expected_outcome") for item in visual}
    if outcomes != ALLOWED_OUTCOMES:
        errors.append("visual suite must contain accepted, rejected, and ambiguous outcomes")

    provenance_records = load_yaml(provenance_path).get("records", [])
    provenance = {item.get("id"): item for item in provenance_records}
    repro = load_yaml(reproducibility_path)
    repro_assets = {item.get("path"): item.get("sha256") for item in repro.get("assets", [])}
    if repro.get("deterministic") is not True or repro.get("network_required") is not False:
        errors.append("reproducibility manifest must be deterministic and offline")
    if repro.get("image_generator_used") is not False or repro.get("subjective_visual_quality_assessed") is not False:
        errors.append("reproducibility manifest makes an invalid generator/visual-quality claim")

    for item in visual:
        cid = item.get("id")
        rel = item.get("path")
        if not isinstance(rel, str) or not ASCII.fullmatch(rel):
            errors.append(f"visual {cid}: path must be ASCII")
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"visual {cid}: missing asset {rel}")
            continue
        if path.suffix.lower() != ".svg":
            errors.append(f"visual {cid}: anchors must be SVG")
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"visual {cid}: invalid SVG: {exc}")
        digest = sha256(path)
        if item.get("sha256") != digest or not SHA256.fullmatch(str(item.get("sha256", ""))):
            errors.append(f"visual {cid}: SHA-256 mismatch")
        if repro_assets.get(rel) != digest:
            errors.append(f"visual {cid}: reproducibility manifest mismatch")
        if item.get("synthetic_qa_anchor") is not True or item.get("image_generator_output") is not False:
            errors.append(f"visual {cid}: synthetic/generator boundary invalid")
        if not all(item.get(key) is True for key in ("manual_review_required", "full_size_review_required", "target_size_review_required")):
            errors.append(f"visual {cid}: manual full-size and target-size review required")
        if item.get("target_size_px") != 64:
            errors.append(f"visual {cid}: target size must be 64")
        sr, gr = item.get("declared_silver_ratio"), item.get("declared_gold_ratio")
        if not isinstance(sr, int) or not isinstance(gr, int) or sr + gr != 100:
            errors.append(f"visual {cid}: declared ratios must be integers summing to 100")
        if item.get("expected_outcome") == "accepted" and not (70 <= sr <= 85 and 15 <= gr <= 30):
            errors.append(f"visual {cid}: accepted ratio outside contract")
        prov = provenance.get(item.get("provenance_id"))
        if not prov:
            errors.append(f"visual {cid}: missing provenance record")
        else:
            if prov.get("path") != rel or prov.get("sha256") != digest:
                errors.append(f"visual {cid}: provenance path/hash mismatch")
            for key, expected in (("third_party_content", False), ("pii", False), ("exif", False), ("generator_output", False)):
                if prov.get(key) is not expected:
                    errors.append(f"visual {cid}: provenance {key} must be {expected}")
            if prov.get("license_status") != "original_project_asset":
                errors.append(f"visual {cid}: invalid license status")
        text = path.read_text(encoding="utf-8").casefold()
        for marker in FORBIDDEN_RUNTIME_MARKERS:
            if marker in text:
                errors.append(f"visual {cid}: external brand leakage marker {marker!r}")

    if len(provenance) != len(visual):
        errors.append("provenance record count must equal visual anchor count")

    import importlib.util
    spec = importlib.util.spec_from_file_location("build_regression_anchors", builder_path)
    if spec is None or spec.loader is None:
        errors.append("cannot load anchor builder")
    else:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            rebuilt = module.build(Path(tmp))
            for rel, expected_hash in rebuilt.items():
                repo_rel = f"skills/silver-gold-image-pipeline/assets/{rel}"
                if repro_assets.get(repo_rel) != expected_hash:
                    errors.append(f"rebuilt anchor mismatch: {repo_rel}")

    rubric = rubric_path.read_text(encoding="utf-8").casefold()
    for phrase in ("full-size review", "target-size review", "does not automate subjective visual quality", "not outputs from an image generator", "ambiguous"):
        if phrase not in rubric:
            errors.append(f"visual rubric missing phrase: {phrase}")

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
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"regression suite: {'FAIL' if errors else 'PASS'}")
        for error in errors:
            print(f"- {error}")
        print(json.dumps(details, ensure_ascii=False, sort_keys=True))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
