#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "skills/silver-gold-image-pipeline/assets/templates/capability-profiles.yaml"
DECISION = ROOT / "skills/silver-gold-image-pipeline/assets/templates/adapter-decision.yaml"
CONTRACT = ROOT / "skills/silver-gold-image-pipeline/references/generator-adapters.md"
CASES = ROOT / "tests/cases/adapter-routing-cases.yaml"
STATUSES = {"supported", "partial", "unsupported"}
CAPABILITIES = {
    "text_to_image", "reference_image_generation", "image_editing", "mask_or_region_editing",
    "multi_reference", "identity_preservation", "composition_preservation", "transparent_output",
    "exact_text", "aspect_ratio_control", "resolution_control", "seed_reproducibility",
    "visible_final_output", "iterative_editing",
}
MODES = {"generate", "edit", "style_transfer", "reinterpretation", "composite", "sketch_to_render"}
RISKS = {"chrome_mirror_amplification", "gold_overfill", "matte_loss", "rim_light_drift", "metallic_noise", "background_drift", "black_gold_drift", "identity_composition_drift"}
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "#ff0508")


def choose(profiles: dict, available: list[str], required: list[str]) -> tuple[str | None, str, list[str]]:
    candidates = []
    for index, profile_id in enumerate(available):
        profile = profiles[profile_id]
        statuses = {name: profile["capabilities"][name]["status"] for name in required}
        if any(status == "unsupported" for status in statuses.values()):
            continue
        supported = sum(status == "supported" for status in statuses.values())
        partial = [name for name, status in statuses.items() if status == "partial"]
        candidates.append((-supported, len(partial), index, profile_id, partial))
    if not candidates:
        return None, "stop", []
    _, _, _, profile_id, partial = sorted(candidates)[0]
    return profile_id, "fallback" if partial else "route", partial


def main() -> int:
    errors: list[str] = []
    checks = 0
    def require(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(label)

    for path in (PROFILES, DECISION, CONTRACT, CASES):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    data = yaml.safe_load(PROFILES.read_text(encoding="utf-8"))
    require(data.get("schema_version") == "1.0.0", "profile schema")
    require(data.get("adapter_contract_version") == "0.1.0", "profile contract version")
    require(set(data.get("status_values", [])) == STATUSES, "status values")
    profile_list = data.get("profiles", [])
    require(len(profile_list) >= 3, "profile count")
    profiles = {profile.get("id"): profile for profile in profile_list}
    require(len(profiles) == len(profile_list), "duplicate profile IDs")
    require({"openai-native-image", "google-nano-banana-2", "generic-runtime-detected"} <= set(profiles), "required profiles")
    for profile_id, profile in profiles.items():
        require(set(profile.get("capabilities", {})) == CAPABILITIES, f"{profile_id}: capability set")
        require(set(profile.get("silver_gold_risks", [])) == RISKS, f"{profile_id}: risk set")
        require(isinstance(profile.get("runtime_availability_required"), bool), f"{profile_id}: runtime availability")
        for name, entry in profile.get("capabilities", {}).items():
            require(entry.get("status") in STATUSES, f"{profile_id}/{name}: status")
            require(isinstance(entry.get("evidence"), str) and bool(entry["evidence"]), f"{profile_id}/{name}: evidence")
            require(isinstance(entry.get("limitations"), list), f"{profile_id}/{name}: limitations")
        if profile_id != "generic-runtime-detected":
            require(bool(profile.get("evidence_sources")), f"{profile_id}: evidence sources")
            for source in profile["evidence_sources"]:
                require(source.get("type") == "official_documentation", f"{profile_id}: source type")
                require(str(source.get("url", "")).startswith("https://"), f"{profile_id}: source URL")
                require(source.get("retrieved_at") == "2026-07-15", f"{profile_id}: retrieval date")

    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    required_decision_fields = {"schema_version", "adapter_contract_version", "decision_id", "run_id", "requested_mode", "mandatory_capabilities", "available_profile_ids", "selected_profile_id", "runtime_available", "capability_results", "degradations", "preserved_requirements", "lost_requirements", "deterministic_post_processing", "fallback_level", "stop_reason", "actual_invocation"}
    require(set(decision) == required_decision_fields, "decision fields")
    require(decision.get("requested_mode") in MODES, "decision mode")
    require(decision.get("runtime_available") is False, "decision availability default")
    require(decision.get("actual_invocation", {}).get("user_visible") is False, "decision visibility default")

    fixture = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = fixture.get("cases", [])
    require(fixture.get("schema_version") == "1.0.0", "case schema")
    require(fixture.get("adapter_contract_version") == "0.1.0", "case contract version")
    require(len(cases) >= 10, "case count")
    for case in cases:
        case_id = case.get("id")
        require(case.get("mode") in MODES, f"{case_id}: mode")
        require(set(case.get("mandatory_capabilities", [])) <= CAPABILITIES, f"{case_id}: capabilities")
        require(set(case.get("available_profiles", [])) <= set(profiles), f"{case_id}: profiles")
        selected, outcome, degradations = choose(profiles, case["available_profiles"], case["mandatory_capabilities"])
        allowed = set(case.get("allowed_profiles", [case.get("expected_profile")]))
        require(selected in allowed, f"{case_id}: selected {selected}")
        require(outcome == case.get("expected_outcome"), f"{case_id}: outcome {outcome}")
        require(set(degradations) == set(case.get("expected_degradations", [])), f"{case_id}: degradations {degradations}")
        if outcome == "stop":
            require(case.get("expected_stop_reason") == "CAPABILITY_UNSUPPORTED", f"{case_id}: stop reason")
        if "exact_text" in case.get("mandatory_capabilities", []):
            require("text" in case.get("deterministic_post_processing", []), f"{case_id}: exact text post-processing")

    text = CONTRACT.read_text(encoding="utf-8")
    for phrase in (
        "Do not present regeneration as targeted editing",
        "Do not silently ignore extra references",
        "Exact text and exact logos remain deterministic post-processing",
        "Output bytes or a tool result are not user-visible delivery",
        "CAPABILITY_UNSUPPORTED",
        "Provider quality claims never replace Gate 4 manual inspection",
    ):
        require(phrase in text, f"contract phrase: {phrase}")
    for term in BANNED:
        require(term not in text.casefold(), f"brand leakage: {term}")

    print(f"adapter checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("result: PASS")
    print("validated: evidence-backed profiles, status matrix, routing, degradations, fallback, stop and delivery boundaries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
