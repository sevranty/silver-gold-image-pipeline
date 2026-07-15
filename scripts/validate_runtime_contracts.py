#!/usr/bin/env python3
"""Validate SGIP #5/#6 runtime contracts without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "silver-gold-image-pipeline"

REQUIRED_PATHS = (
    "skills/silver-gold-image-pipeline/references/reference-analysis.md",
    "skills/silver-gold-image-pipeline/references/workflow-and-locks.md",
    "skills/silver-gold-image-pipeline/references/prompt-patterns.md",
    "skills/silver-gold-image-pipeline/references/quality-gates.md",
    "skills/silver-gold-image-pipeline/references/output-delivery.md",
    "skills/silver-gold-image-pipeline/assets/templates/reference-analysis-card.md",
    "skills/silver-gold-image-pipeline/assets/templates/scene-brief.yaml",
    "skills/silver-gold-image-pipeline/assets/templates/generation-spec.yaml",
    "skills/silver-gold-image-pipeline/assets/templates/edit-contract.yaml",
    "skills/silver-gold-image-pipeline/assets/templates/qa-scorecard.yaml",
    "skills/silver-gold-image-pipeline/assets/templates/output-manifest.yaml",
    "tests/cases/runtime-contracts-valid.yaml",
    "tests/cases/runtime-contracts-invalid.yaml",
    "tests/cases/qa-critical-defects.yaml",
    "tests/expected/smoke-test-qa-scorecard.yaml",
)

ALLOWED_REFERENCE_ROLES = {
    "subject_reference",
    "identity_reference",
    "composition_reference",
    "environment_reference",
    "text_reference",
    "logo_reference",
    "mask_reference",
}

ALLOWED_MODES = {
    "generate",
    "edit",
    "style_transfer",
    "reinterpretation",
    "composite",
    "sketch_to_render",
}

ALLOWED_BACKGROUND_PROFILES = {"product-light", "showcase-neutral"}

PROMPT_BLOCK_ORDER = [
    "asset_and_use_case",
    "primary_subject_and_action",
    "required_construction_details",
    "composition_and_camera",
    "silver_gold_material_allocation",
    "geometry_and_edges",
    "background_profile",
    "lighting_shadows_reflections",
    "negative_constraints",
    "output_constraints",
]

REQUIRED_MARKERS = {
    "matte_or_satin_silver_structural_base",
    "subtle_subordinate_gold_accents",
    "declared_70_85_15_30_allocation",
    "low_poly_faceted_geometry",
    "clean_edges_and_sharp_folds",
    "controlled_rim_light",
    "minimal_local_highlights_no_environment_reflection",
}

NEGATIVE_GROUPS = {
    "gloss",
    "reflection",
    "chrome",
    "liquid_metal",
    "jewelry",
    "gold_dominance",
    "baroque",
    "surface_noise",
    "colored_reflection",
    "style_mixing",
}

REQUIRED_LOCKS = {
    "semantic_lock",
    "identity_lock",
    "object_lock",
    "composition_lock",
    "palette_lock",
    "text_lock",
    "silver_gold_style_lock",
}

DIAGNOSTICS = {
    "semantic_error",
    "identity_error",
    "composition_error",
    "metal_ratio_error",
    "material_error",
    "reflection_error",
    "lighting_error",
    "background_error",
    "geometry_error",
    "text_error",
    "technical_error",
}

CRITICAL_DEFECTS = {
    "gold_base_material",
    "silver_not_dominant",
    "gloss_mirror_chrome",
    "jewelry_baroque",
    "wrong_subject_or_meaning",
    "identity_or_construction_failure",
    "background_profile_failure",
    "required_text_or_logo_damaged",
    "delivery_missing",
}

SCORE_WEIGHTS = {
    "task_semantic_fidelity": (20, 16),
    "reference_locks": (15, 11),
    "metal_allocation": (15, 12),
    "material_reflection_compliance": (15, 12),
    "geometry": (10, 7),
    "lighting_shadows": (10, 7),
    "composition_background_profile": (10, 7),
    "technical_delivery": (5, 5),
}

BANNED_RUNTIME_TERMS = (
    "finuslugi",
    "финуслуги",
    "moex",
    "finkit",
    "#ff0508",
)


def load_yaml(relative: str) -> Any:
    with (ROOT / relative).open("r", encoding="utf-8") as source:
        return yaml.safe_load(source)


def load_frontmatter(relative: str) -> dict[str, Any]:
    text = (ROOT / relative).read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match is None:
        raise ValueError(f"missing YAML front matter: {relative}")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"front matter is not a mapping: {relative}")
    return data


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_scene_like(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    mode = case.get("transformation_mode")
    profile = case.get("background_profile")
    silver = case.get("silver_ratio")
    gold = case.get("gold_ratio")
    style_enabled = case.get("style_lock_enabled")
    style_fidelity = case.get("style_lock_fidelity")
    prompt_mode = case.get("prompt_mode")
    roles = case.get("reference_roles", [])

    if mode not in ALLOWED_MODES:
        errors.append("transformation_mode")
    if profile not in ALLOWED_BACKGROUND_PROFILES:
        errors.append("background_profile")
    if not isinstance(silver, int) or not 70 <= silver <= 85:
        errors.append("silver_ratio_range")
    if not isinstance(gold, int) or not 15 <= gold <= 30:
        errors.append("gold_ratio_range")
    if isinstance(silver, int) and isinstance(gold, int) and silver + gold != 100:
        errors.append("ratio_sum")
    if style_enabled is not True or style_fidelity != 4:
        errors.append("style_lock")
    if any(role not in ALLOWED_REFERENCE_ROLES for role in roles):
        errors.append("reference_role")

    expected_prompt_mode = "edit" if mode == "edit" else "generate"
    if prompt_mode != expected_prompt_mode:
        errors.append("mode_mismatch")

    if mode == "edit":
        if case.get("diagnostic_category") not in DIAGNOSTICS:
            errors.append("diagnostic_category")
        if not isinstance(case.get("keep_unchanged_count"), int) or case["keep_unchanged_count"] < 6:
            errors.append("keep_unchanged")

    if case.get("text_lock_enabled") is True and case.get("deterministic_text") is not True:
        errors.append("deterministic_text")

    source_quality = case.get("source_quality")
    object_fidelity = case.get("object_fidelity")
    if isinstance(source_quality, int) and isinstance(object_fidelity, int):
        if object_fidelity > source_quality:
            errors.append("fidelity_overpromise")

    return errors


def main() -> int:
    errors: list[str] = []
    checks = 0

    for relative in REQUIRED_PATHS:
        checks += 1
        require((ROOT / relative).is_file(), errors, f"missing required file: {relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        checks += 1
        relative = path.relative_to(ROOT).as_posix()
        try:
            relative.encode("ascii")
        except UnicodeEncodeError:
            errors.append(f"non-ASCII path: {relative}")

    runtime_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".yaml", ".yml", ".json"}
    ).casefold()
    for term in BANNED_RUNTIME_TERMS:
        checks += 1
        require(term not in runtime_text, errors, f"runtime brand leakage: {term}")

    analysis = load_frontmatter(
        "skills/silver-gold-image-pipeline/assets/templates/reference-analysis-card.md"
    )
    checks += 6
    require(analysis.get("schema_version") == "1.0.0", errors, "analysis schema version")
    require(analysis.get("contract_version") == "0.1.0", errors, "analysis contract version")
    require(analysis.get("template_id") == "silver-gold-reference-analysis-card", errors, "analysis template id")
    require(isinstance(analysis.get("references"), list), errors, "analysis references list")
    require(isinstance(analysis.get("conflicts"), list), errors, "analysis conflicts list")
    require(isinstance(analysis.get("set_level"), dict), errors, "analysis set_level mapping")

    scene = load_yaml("skills/silver-gold-image-pipeline/assets/templates/scene-brief.yaml")
    checks += 12
    require(scene.get("schema_version") == "1.0.0", errors, "scene schema version")
    require(scene.get("contract_version") == "0.1.0", errors, "scene contract version")
    require(scene.get("transformation_mode") in ALLOWED_MODES, errors, "scene transformation mode")
    require(scene.get("background_profile") in ALLOWED_BACKGROUND_PROFILES, errors, "scene background profile")
    locks = scene.get("locks", {})
    require(set(locks) == REQUIRED_LOCKS, errors, "scene required lock set")
    for lock_name, lock in locks.items():
        checks += 2
        require(isinstance(lock.get("fidelity"), int) and 0 <= lock["fidelity"] <= 4, errors, f"{lock_name} fidelity")
        require(isinstance(lock.get("enabled"), bool), errors, f"{lock_name} enabled")
    style_lock = locks.get("silver_gold_style_lock", {})
    require(style_lock.get("enabled") is True, errors, "style lock enabled")
    require(style_lock.get("fidelity") == 4, errors, "style lock fidelity")
    materials = scene.get("materials", {})
    silver = materials.get("silver_ratio")
    gold = materials.get("gold_ratio")
    require(isinstance(silver, int) and 70 <= silver <= 85, errors, "scene silver range")
    require(isinstance(gold, int) and 15 <= gold <= 30, errors, "scene gold range")
    require(silver + gold == 100, errors, "scene ratio sum")
    require(scene.get("output", {}).get("width", 0) > 0, errors, "scene output width")
    require(scene.get("output", {}).get("height", 0) > 0, errors, "scene output height")

    generation = load_yaml("skills/silver-gold-image-pipeline/assets/templates/generation-spec.yaml")
    checks += 7
    require(generation.get("mode") == "generate", errors, "generation mode")
    actual_order = [block.get("id") for block in generation.get("prompt_blocks", [])]
    require(actual_order == PROMPT_BLOCK_ORDER, errors, "prompt block order")
    require(set(generation.get("required_semantic_markers", [])) == REQUIRED_MARKERS, errors, "required prompt markers")
    require(set(generation.get("negative_semantic_groups", [])) == NEGATIVE_GROUPS, errors, "negative semantic groups")
    allocation = generation.get("material_allocation", {})
    require(allocation.get("silver_ratio") + allocation.get("gold_ratio") == 100, errors, "generation ratio sum")
    require(generation.get("exact_text_strategy") == "deterministic-post-processing", errors, "text strategy")
    require(generation.get("logo_strategy") == "deterministic-provided-asset", errors, "logo strategy")

    edit = load_yaml("skills/silver-gold-image-pipeline/assets/templates/edit-contract.yaml")
    checks += 8
    require(edit.get("mode") == "edit", errors, "edit mode")
    require(edit.get("diagnostic_category") in DIAGNOSTICS, errors, "edit diagnostic")
    iteration = edit.get("iteration", {})
    require(iteration.get("targeted_corrections_remaining") == 2, errors, "edit correction budget")
    require(iteration.get("full_restart_used") is False, errors, "edit restart default")
    require(len(edit.get("keep_unchanged", [])) >= 8, errors, "edit keep unchanged invariants")
    require(isinstance(edit.get("editable_regions"), list), errors, "edit editable regions")
    require(isinstance(edit.get("protected_regions"), list), errors, "edit protected regions")
    require(edit.get("stop_condition") == "one_diagnostic_category_resolved_without_regression", errors, "edit stop condition")

    valid_cases = load_yaml("tests/cases/runtime-contracts-valid.yaml").get("cases", [])
    invalid_cases = load_yaml("tests/cases/runtime-contracts-invalid.yaml").get("cases", [])
    checks += 2
    require(len(valid_cases) >= 6, errors, "at least six valid fixtures")
    require(len(invalid_cases) >= 6, errors, "at least six invalid fixtures")

    for case in valid_cases:
        checks += 1
        case_errors = validate_scene_like(case)
        require(not case_errors, errors, f"valid fixture {case.get('id')} failed: {case_errors}")

    for case in invalid_cases:
        checks += 2
        case_errors = validate_scene_like(case)
        expected = case.get("expected_error")
        require(bool(case_errors), errors, f"invalid fixture {case.get('id')} unexpectedly passed")
        require(expected in case_errors, errors, f"invalid fixture {case.get('id')} missing expected {expected}: {case_errors}")

    scorecard_template = load_yaml("skills/silver-gold-image-pipeline/assets/templates/qa-scorecard.yaml")
    scores = scorecard_template.get("scores", {})
    checks += 5
    require(set(scores) == set(SCORE_WEIGHTS), errors, "scorecard category set")
    require(sum(item.get("weight", 0) for item in scores.values()) == 100, errors, "scorecard weight sum")
    for category, (weight, minimum) in SCORE_WEIGHTS.items():
        checks += 2
        require(scores[category].get("weight") == weight, errors, f"{category} weight")
        require(scores[category].get("minimum") == minimum, errors, f"{category} minimum")
    require(scorecard_template.get("pass_threshold") == 85, errors, "scorecard pass threshold")
    require(set(scorecard_template.get("gates", {})) == {"input", "scene_contract", "prompt_preflight", "visual_result", "technical_delivery"}, errors, "gate set")
    require(scorecard_template.get("status") == "pending", errors, "scorecard template status")

    smoke = load_yaml("tests/expected/smoke-test-qa-scorecard.yaml")
    awarded = {name: item.get("awarded") for name, item in smoke.get("scores", {}).items()}
    checks += 7
    require(smoke.get("status") == "pass", errors, "smoke status")
    require(all(gate.get("pass") is True for gate in smoke.get("gates", {}).values()), errors, "smoke gate pass")
    require(set(awarded) == set(SCORE_WEIGHTS), errors, "smoke score category set")
    require(all(isinstance(value, int) for value in awarded.values()), errors, "smoke awarded values")
    require(sum(awarded.values()) == smoke.get("total_awarded"), errors, "smoke total")
    require(smoke.get("total_awarded", 0) >= smoke.get("pass_threshold", 101), errors, "smoke threshold")
    require(not smoke.get("critical_defects"), errors, "smoke critical defects")
    for category, (_, minimum) in SCORE_WEIGHTS.items():
        checks += 1
        require(awarded[category] >= minimum, errors, f"smoke {category} minimum")

    defects = load_yaml("tests/cases/qa-critical-defects.yaml").get("defects", [])
    defect_ids = {item.get("id") for item in defects}
    checks += 3
    require(defect_ids == CRITICAL_DEFECTS, errors, "critical defect fixture set")
    require(all(isinstance(item.get("accepted"), dict) and item["accepted"] for item in defects), errors, "accepted critical examples")
    require(all(isinstance(item.get("rejected"), dict) and item["rejected"] for item in defects), errors, "rejected critical examples")

    manifest = load_yaml("skills/silver-gold-image-pipeline/assets/templates/output-manifest.yaml")
    checks += 8
    versions = manifest.get("versions", {})
    require(versions.get("pipeline_core_version") == "0.2.0", errors, "manifest pipeline version")
    require(versions.get("prompt_schema_version") == "0.1.0", errors, "manifest prompt version")
    require(versions.get("qa_schema_version") == "0.1.0", errors, "manifest qa version")
    require(versions.get("manifest_schema_version") == "0.1.0", errors, "manifest schema version")
    require(manifest.get("delivery", {}).get("state") == "PLANNED", errors, "manifest delivery default")
    require(manifest.get("delivery", {}).get("user_visible") is False, errors, "manifest visibility default")
    require(set(manifest.get("files", {})) == {"final", "preview", "source_render"}, errors, "manifest file set")
    require(isinstance(manifest.get("iterations"), list), errors, "manifest iterations list")

    reference_text = (SKILL_ROOT / "references" / "reference-analysis.md").read_text(encoding="utf-8")
    workflow_text = (SKILL_ROOT / "references" / "workflow-and-locks.md").read_text(encoding="utf-8")
    prompt_text = (SKILL_ROOT / "references" / "prompt-patterns.md").read_text(encoding="utf-8")
    quality_text = (SKILL_ROOT / "references" / "quality-gates.md").read_text(encoding="utf-8")
    delivery_text = (SKILL_ROOT / "references" / "output-delivery.md").read_text(encoding="utf-8")

    textual_requirements = (
        ("style_reference` is not a valid role", reference_text, "external style role rejection"),
        ("at most two targeted corrections", workflow_text, "targeted correction limit"),
        ("at most one full restart", workflow_text, "full restart limit"),
        ("one diagnostic category", prompt_text, "one-category edit rule"),
        ("total score at least 85/100", quality_text, "QA pass threshold text"),
        ("DELIVERY_MISSING", quality_text, "quality delivery missing"),
        ("Only `DELIVERED` is a successful terminal state", delivery_text, "terminal delivery rule"),
        ("blank final response is not completion", delivery_text, "blank response prohibition"),
    )
    for needle, haystack, label in textual_requirements:
        checks += 1
        require(needle in haystack, errors, label)

    print(f"runtime contract checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("result: PASS")
    print("validated: reference analysis, locks, scene/prompt contracts, QA gates, critical defects, delivery")
    return 0


if __name__ == "__main__":
    sys.exit(main())
