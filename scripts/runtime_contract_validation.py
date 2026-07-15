from __future__ import annotations

import re
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
ROLES = {
    "subject_reference", "identity_reference", "composition_reference",
    "environment_reference", "text_reference", "logo_reference", "mask_reference",
}
MODES = {"generate", "edit", "style_transfer", "reinterpretation", "composite", "sketch_to_render"}
EDIT_MODES = {"edit", "style_transfer"}
PROFILES = {"product-light", "showcase-neutral"}
BLOCKS = [
    "asset_and_use_case", "primary_subject_and_action", "required_construction_details",
    "composition_and_camera", "silver_gold_material_allocation", "geometry_and_edges",
    "background_profile", "lighting_shadows_reflections", "negative_constraints",
    "output_constraints",
]
MARKERS = {
    "matte_or_satin_silver_structural_base", "subtle_subordinate_gold_accents",
    "declared_70_85_15_30_allocation", "low_poly_faceted_geometry",
    "clean_edges_and_sharp_folds", "controlled_rim_light",
    "minimal_local_highlights_no_environment_reflection",
}
NEGATIVES = {
    "gloss", "reflection", "chrome", "liquid_metal", "jewelry", "gold_dominance",
    "baroque", "surface_noise", "colored_reflection", "style_mixing",
}
LOCKS = {
    "semantic_lock", "identity_lock", "object_lock", "composition_lock",
    "palette_lock", "text_lock", "silver_gold_style_lock",
}
LOCK_LIST_FIELDS = {"source_reference_ids", "preserve", "allowed_deviation", "evidence", "uncertainty"}
DIAGNOSTICS = {
    "semantic_error", "identity_error", "composition_error", "metal_ratio_error",
    "material_error", "reflection_error", "lighting_error", "background_error",
    "geometry_error", "text_error", "technical_error",
}
DEFECTS = {
    "gold_base_material", "silver_not_dominant", "gloss_mirror_chrome",
    "jewelry_baroque", "wrong_subject_or_meaning", "identity_or_construction_failure",
    "background_profile_failure", "required_text_or_logo_damaged", "delivery_missing",
}
WEIGHTS = {
    "task_semantic_fidelity": (20, 16), "reference_locks": (15, 11),
    "metal_allocation": (15, 12), "material_reflection_compliance": (15, 12),
    "geometry": (10, 7), "lighting_shadows": (10, 7),
    "composition_background_profile": (10, 7), "technical_delivery": (5, 5),
}
FILE_FIELDS = {"required", "path", "sha256", "size_bytes", "width", "height", "format", "alpha"}
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "#ff0508")


def yaml_file(relative: str) -> Any:
    return yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))


def frontmatter(relative: str) -> dict[str, Any]:
    text = (ROOT / relative).read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match is None:
        raise ValueError(f"missing YAML front matter: {relative}")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise ValueError(f"front matter is not a mapping: {relative}")
    return value


def scene_errors(case: dict[str, Any]) -> list[str]:
    out: list[str] = []
    mode = case.get("transformation_mode")
    profile = case.get("background_profile")
    silver = case.get("silver_ratio")
    gold = case.get("gold_ratio")
    if mode not in MODES: out.append("transformation_mode")
    if profile not in PROFILES: out.append("background_profile")
    if not isinstance(silver, int) or not 70 <= silver <= 85: out.append("silver_ratio_range")
    if not isinstance(gold, int) or not 15 <= gold <= 30: out.append("gold_ratio_range")
    if isinstance(silver, int) and isinstance(gold, int) and silver + gold != 100: out.append("ratio_sum")
    if case.get("style_lock_enabled") is not True or case.get("style_lock_fidelity") != 4: out.append("style_lock")
    if any(role not in ROLES for role in case.get("reference_roles", [])): out.append("reference_role")
    expected_mode = "edit" if mode in EDIT_MODES else "generate"
    if case.get("prompt_mode") != expected_mode: out.append("mode_mismatch")
    if mode in EDIT_MODES:
        if case.get("diagnostic_category") not in DIAGNOSTICS: out.append("diagnostic_category")
        if not isinstance(case.get("keep_unchanged_count"), int) or case["keep_unchanged_count"] < 6:
            out.append("keep_unchanged")
    if case.get("text_lock_enabled") is True and case.get("deterministic_text") is not True:
        out.append("deterministic_text")
    quality, fidelity = case.get("source_quality"), case.get("object_fidelity")
    if isinstance(quality, int) and isinstance(fidelity, int) and fidelity > quality:
        out.append("fidelity_overpromise")
    return out


def main() -> int:
    errors: list[str] = []
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(label)

    for relative in REQUIRED_PATHS:
        require((ROOT / relative).is_file(), f"missing required file: {relative}")
    for path in ROOT.rglob("*"):
        if path.is_file():
            try:
                path.relative_to(ROOT).as_posix().encode("ascii")
            except UnicodeEncodeError:
                errors.append(f"non-ASCII path: {path.relative_to(ROOT).as_posix()}")
            checks += 1

    runtime = "\n".join(
        p.read_text(encoding="utf-8") for p in SKILL_ROOT.rglob("*")
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".json"}
    ).casefold()
    for term in BANNED:
        require(term not in runtime, f"runtime brand leakage: {term}")

    analysis = frontmatter("skills/silver-gold-image-pipeline/assets/templates/reference-analysis-card.md")
    require(analysis.get("schema_version") == "1.0.0", "analysis schema version")
    require(analysis.get("contract_version") == "0.1.0", "analysis contract version")
    require(isinstance(analysis.get("references"), list), "analysis references")
    require(isinstance(analysis.get("conflicts"), list), "analysis conflicts")
    ref_schema = analysis.get("reference_entry_schema", {})
    conflict_schema = analysis.get("conflict_entry_schema", {})
    require(ref_schema.get("source_quality_range") == [0, 4], "source quality range")
    require(ref_schema.get("confidence_range") == [0, 4], "confidence range")
    require(len(ref_schema.get("required_fields", [])) >= 14, "reference entry fields")
    require(len(conflict_schema.get("required_fields", [])) >= 7, "conflict entry fields")

    scene = yaml_file("skills/silver-gold-image-pipeline/assets/templates/scene-brief.yaml")
    require(scene.get("transformation_mode") in MODES, "scene mode")
    require(scene.get("background_profile") in PROFILES, "scene profile")
    locks = scene.get("locks", {})
    require(set(locks) == LOCKS, "scene lock set")
    for name, lock in locks.items():
        require(isinstance(lock.get("enabled"), bool), f"{name} enabled")
        require(isinstance(lock.get("fidelity"), int) and 0 <= lock["fidelity"] <= 4, f"{name} fidelity")
        for field in LOCK_LIST_FIELDS:
            require(isinstance(lock.get(field), list), f"{name} {field}")
    require(locks["silver_gold_style_lock"].get("enabled") is True, "style lock enabled")
    require(locks["silver_gold_style_lock"].get("fidelity") == 4, "style lock fidelity")
    require(bool(locks["silver_gold_style_lock"].get("evidence")), "style lock evidence")
    materials = scene.get("materials", {})
    silver, gold = materials.get("silver_ratio"), materials.get("gold_ratio")
    require(isinstance(silver, int) and 70 <= silver <= 85, "scene silver")
    require(isinstance(gold, int) and 15 <= gold <= 30, "scene gold")
    require(silver + gold == 100, "scene ratio sum")

    generation = yaml_file("skills/silver-gold-image-pipeline/assets/templates/generation-spec.yaml")
    require([b.get("id") for b in generation.get("prompt_blocks", [])] == BLOCKS, "prompt block order")
    require(set(generation.get("required_semantic_markers", [])) == MARKERS, "prompt markers")
    require(set(generation.get("negative_semantic_groups", [])) == NEGATIVES, "negative groups")
    allocation = generation.get("material_allocation", {})
    require(allocation.get("silver_ratio") + allocation.get("gold_ratio") == 100, "generation ratio")

    edit = yaml_file("skills/silver-gold-image-pipeline/assets/templates/edit-contract.yaml")
    require(edit.get("mode") == "edit", "edit mode")
    require(edit.get("diagnostic_category") in DIAGNOSTICS, "edit diagnostic")
    require(set(edit.get("active_lock_snapshot", {})) == LOCKS, "active lock snapshot")
    keep = edit.get("keep_unchanged", {})
    require(set(keep.get("from_active_locks", {})) == LOCKS, "keep active locks")
    require(isinstance(keep.get("additional_invariants"), list), "keep additional invariants")
    require(edit.get("iteration", {}).get("targeted_corrections_remaining") == 2, "correction budget")
    require(edit.get("iteration", {}).get("full_restart_used") is False, "restart default")

    valid = yaml_file("tests/cases/runtime-contracts-valid.yaml").get("cases", [])
    invalid = yaml_file("tests/cases/runtime-contracts-invalid.yaml").get("cases", [])
    require(len(valid) >= 6, "valid fixture count")
    require(len(invalid) >= 7, "invalid fixture count")
    for case in valid:
        require(not scene_errors(case), f"valid fixture {case.get('id')}: {scene_errors(case)}")
    for case in invalid:
        found = scene_errors(case)
        require(bool(found), f"invalid fixture {case.get('id')} passed")
        require(case.get("expected_error") in found, f"invalid fixture {case.get('id')} expected {case.get('expected_error')}: {found}")

    scorecard = yaml_file("skills/silver-gold-image-pipeline/assets/templates/qa-scorecard.yaml")
    scores = scorecard.get("scores", {})
    require(set(scores) == set(WEIGHTS), "score categories")
    require(sum(v.get("weight", 0) for v in scores.values()) == 100, "score weight sum")
    for name, (weight, minimum) in WEIGHTS.items():
        require(scores[name].get("weight") == weight, f"{name} weight")
        require(scores[name].get("minimum") == minimum, f"{name} minimum")
    require(scorecard.get("pass_threshold") == 85, "score threshold")

    smoke = yaml_file("tests/expected/smoke-test-qa-scorecard.yaml")
    awarded = {name: value.get("awarded") for name, value in smoke.get("scores", {}).items()}
    require(smoke.get("status") == "pass", "smoke status")
    require(all(g.get("pass") is True for g in smoke.get("gates", {}).values()), "smoke gates")
    require(sum(awarded.values()) == smoke.get("total_awarded"), "smoke total")
    require(smoke.get("total_awarded", 0) >= 85, "smoke threshold")
    require(not smoke.get("critical_defects"), "smoke critical defects")
    for name, (_, minimum) in WEIGHTS.items():
        require(awarded.get(name, -1) >= minimum, f"smoke {name}")

    defects = yaml_file("tests/cases/qa-critical-defects.yaml").get("defects", [])
    require({d.get("id") for d in defects} == DEFECTS, "critical defect set")
    require(all(d.get("accepted") and d.get("rejected") for d in defects), "critical defect examples")

    manifest = yaml_file("skills/silver-gold-image-pipeline/assets/templates/output-manifest.yaml")
    require(manifest.get("delivery", {}).get("state") == "PLANNED", "manifest state")
    require(manifest.get("delivery", {}).get("user_visible") is False, "manifest visibility")
    records = manifest.get("files", {})
    require(set(records) == {"final", "preview", "source_render", "deterministic_overlay"}, "manifest file set")
    for name, record in records.items():
        require(set(record) == FILE_FIELDS, f"manifest {name} fields")
        require(isinstance(record.get("required"), bool), f"manifest {name} required")
    require(records.get("final", {}).get("required") is True, "manifest final required")

    text_requirements = (
        ("style_reference` is not a valid role", "reference-analysis.md"),
        ("`edit` and `style_transfer`", "workflow-and-locks.md"),
        ("machine-readable snapshot of every active lock", "workflow-and-locks.md"),
        ("`style_transfer` is routed as generate", "prompt-patterns.md"),
        ("total score at least 85/100", "quality-gates.md"),
        ("Only `DELIVERED` is a successful terminal state", "output-delivery.md"),
        ("deterministic overlay as a file object", "output-delivery.md"),
    )
    for needle, filename in text_requirements:
        text = (SKILL_ROOT / "references" / filename).read_text(encoding="utf-8")
        require(needle in text, f"text requirement: {needle}")

    print(f"runtime contract checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("result: PASS")
    print("validated: analysis schemas, complete locks, safe mode routing, prompt/QA contracts, manifest files, delivery")
    return 0
