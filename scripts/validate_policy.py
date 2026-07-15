#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "skills/silver-gold-image-pipeline/references/safety-and-rights.md"
TEMPLATE = ROOT / "skills/silver-gold-image-pipeline/assets/templates/policy-decision.yaml"
CASES = ROOT / "tests/cases/policy-cases.yaml"
ACTIONS = {"proceed", "transform", "post_process", "request_asset", "lower_fidelity", "stop"}
SUBJECTS = {"user_self", "private_adult", "public_person", "child", "fictional_character", "not_applicable"}
RISKS = {"identity", "living_tissue", "child_safety", "exact_text", "logo", "privacy", "reference_rights", "external_style"}
PUBLIC_FIELDS = {"eligible", "pii_absent", "exif_removed", "geolocation_removed", "confidential_material_absent", "redistribution_allowed", "provenance_recorded"}
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "#ff0508")
DECISION_STATES = {"pass", "block", "reject"}


def main() -> int:
    errors: list[str] = []
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    for path in (POLICY, TEMPLATE, CASES):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    text = POLICY.read_text(encoding="utf-8")
    folded = text.casefold()
    for term in BANNED:
        require(term not in folded, f"brand leakage: {term}")
    for action in sorted(ACTIONS):
        require(f"`{action}`" in text, f"missing action: {action}")
    for state in sorted(DECISION_STATES):
        require(f"`{state}`" in text, f"missing decision state: {state}")
    for phrase in (
        "Do not turn skin, eyes, teeth, hair, wounds, or other living tissue into metal by default",
        "Stochastic text output never satisfies an exact-text gate by itself",
        "Do not use stochastic generation as the primary method for an exact logo",
        "Do not describe the output as an exact imitation of a named contemporary creator",
        "`public_fixture_eligible: true` is allowed only",
        "`request_asset` is never a passing terminal decision",
    ):
        require(phrase in text, f"missing rule: {phrase}")

    template = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    require(template.get("schema_version") == "1.0.0", "template schema")
    require(template.get("policy_version") == "0.1.0", "template policy version")
    require(template.get("decision_state") in DECISION_STATES, "template decision state")
    require(template.get("subject_category") in SUBJECTS, "template subject")
    require(isinstance(template.get("actions"), list), "template actions")
    require(isinstance(template.get("rationale"), list), "template rationale")
    require(set(template.get("risks", {})) == RISKS, "template risk set")
    require(set(template.get("public_fixture", {})) == PUBLIC_FIELDS, "public fixture fields")

    fixture = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = fixture.get("cases", [])
    require(fixture.get("schema_version") == "1.0.0", "cases schema")
    require(fixture.get("policy_version") == "0.1.0", "cases version")
    require(len(cases) >= 14, "case count")
    ids = [case.get("id") for case in cases]
    require(len(ids) == len(set(ids)), "duplicate case ids")

    for case in cases:
        case_id = case.get("id")
        require(case.get("subject_category") in SUBJECTS, f"{case_id}: subject")
        require(isinstance(case.get("source_quality"), int) and 0 <= case["source_quality"] <= 4, f"{case_id}: quality")
        requested = case.get("requested_fidelity", 0)
        supported = case.get("supported_fidelity", requested)
        require(isinstance(requested, int) and 0 <= requested <= 4, f"{case_id}: requested fidelity")
        require(isinstance(supported, int) and 0 <= supported <= 4, f"{case_id}: supported fidelity")
        risks = set(case.get("risks", []))
        actions = set(case.get("actions", []))
        require(risks <= RISKS, f"{case_id}: risks")
        require(bool(actions) and actions <= ACTIONS, f"{case_id}: actions")
        expected = case.get("expected")
        require(expected in DECISION_STATES, f"{case_id}: expected")
        require(("stop" in actions) == (expected == "reject"), f"{case_id}: stop outcome")
        if expected == "block":
            require("request_asset" in actions, f"{case_id}: blocking asset request")
        if expected == "pass":
            require("stop" not in actions and "request_asset" not in actions, f"{case_id}: passing terminal action")
        if requested > supported:
            require("lower_fidelity" in actions or "stop" in actions, f"{case_id}: unsupported fidelity")
        if "child_safety" in risks:
            require("stop" in actions, f"{case_id}: child safety")
        if "exact_text" in risks:
            require("post_process" in actions, f"{case_id}: exact text")
        if "logo" in risks:
            if case.get("permission_status") != "authorized":
                require("request_asset" in actions or "stop" in actions, f"{case_id}: logo asset")
            else:
                require("post_process" in actions, f"{case_id}: logo post process")
        if "reference_rights" in risks and case.get("permission_status") != "authorized":
            require("request_asset" in actions or "stop" in actions, f"{case_id}: reference rights")
        if case.get("public_fixture"):
            public = case["public_fixture"]
            require(set(public) == PUBLIC_FIELDS, f"{case_id}: public fields")
            eligibility = all(public[key] for key in PUBLIC_FIELDS - {"eligible"})
            require(public["eligible"] == eligibility, f"{case_id}: public eligibility")
            if case.get("subject_category") == "child":
                require(public["eligible"] is False, f"{case_id}: child public fixture")

    print(f"policy checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("result: PASS")
    print("validated: decision lifecycle, operational actions, people, text/logo separation, reference rights, public fixture hygiene")
    return 0


if __name__ == "__main__":
    sys.exit(main())
