#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from yaml_compat import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/silver-gold-image-pipeline/SKILL.md"
OPENAI = ROOT / "skills/silver-gold-image-pipeline/agents/openai.yaml"
STATE = ROOT / "skills/silver-gold-image-pipeline/assets/templates/runtime-state.yaml"
CASES = ROOT / "tests/cases/trigger-cases.yaml"

REFERENCE_PATHS = {
    "references/reference-analysis.md",
    "references/safety-and-rights.md",
    "references/workflow-and-locks.md",
    "references/style-spec.md",
    "references/background-profiles.md",
    "references/prompt-patterns.md",
    "references/quality-gates.md",
    "references/output-delivery.md",
}
MODES = {"generate", "edit", "style_transfer", "reinterpretation", "composite", "sketch_to_render"}
STAGES = [
    "Confirm that every required image is actually available",
    "Select exactly one supported transformation mode",
    "Assign reference roles and concern-specific priorities",
    "Create the reference analysis card",
    "Run the safety and rights decision",
    "Create all active locks",
    "Select one background profile and create the scene brief",
    "Route generate-like modes",
    "Assemble the prompt and run preflight QA",
    "Invoke an available image-generation or image-edit capability",
    "Inspect the result manually at full and target size",
    "Diagnose one error category",
    "Run technical validation and write the output manifest",
    "Surface the final image to the user",
]
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "#ff0508")
NONTRIGGER_MARKERS = ("analy", "resize", "convert", "without generating", "watercolor", "do not generate", "no image", "caption")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.DOTALL)
    if not match:
        raise ValueError("missing YAML front matter")
    return yaml.safe_load(match.group(1)), match.group(2)


def main() -> int:
    errors: list[str] = []
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    for path in (SKILL, OPENAI, STATE, CASES):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    text = SKILL.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    require(metadata.get("name") == "silver-gold-image-pipeline", "skill name")
    description = metadata.get("description", "")
    require(isinstance(description, str) and 250 <= len(description) <= 700, "description length")
    for phrase in ("available reference images", "Do not use", "crop/resize", "analysis-only"):
        require(phrase in description, f"description marker: {phrase}")
    require(len(body.split()) < 900, "SKILL.md must remain compact")
    for path in REFERENCE_PATHS:
        require(path in body, f"missing reference map: {path}")
    for mode in MODES:
        require(f"`{mode}`" in body, f"missing mode: {mode}")
    positions = [body.find(stage) for stage in STAGES]
    require(all(position >= 0 for position in positions), "missing workflow stage")
    require(positions == sorted(positions), "workflow order")
    for phrase in (
        "Continue only on `pass`; pause on `block`; stop on `reject`",
        "at most two targeted corrections; allow one full restart",
        "`Change`", "`Keep unchanged`", "`May vary`", "`Must not appear`",
        "Only a validated artifact that is visibly surfaced to the user may end as `DELIVERED`",
        "`DELIVERY_MISSING`",
        "Do not offer a style chooser",
        "Never pretend an unavailable image was inspected",
    ):
        require(phrase in body, f"missing runtime rule: {phrase}")
    for term in BANNED:
        require(term not in text.casefold(), f"brand leakage: {term}")

    interface = yaml.safe_load(OPENAI.read_text(encoding="utf-8")).get("interface", {})
    require(set(interface) == {"display_name", "short_description", "default_prompt"}, "openai interface fields")
    require(interface.get("display_name") == "Silver-Gold Image Pipeline", "display name")
    require("@silver-gold-image-pipeline" in interface.get("default_prompt", ""), "default prompt invocation")

    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    require(state.get("schema_version") == "1.0.0", "state schema")
    require(state.get("skill_version") == "0.1.0", "state skill version")
    require(state.get("stage") == "input_availability", "state initial stage")
    require(state.get("delivery_state") == "PLANNED", "state delivery")
    require(state.get("targeted_corrections_used") == 0, "state corrections")
    require(state.get("full_restart_used") is False, "state restart")

    fixture = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = fixture.get("cases", [])
    require(fixture.get("schema_version") == "1.1.0", "case schema")
    require(fixture.get("skill_version") == "0.1.0", "case skill version")
    require(len(cases) >= 14, "case count")
    ids = [case.get("id") for case in cases]
    require(len(ids) == len(set(ids)), "duplicate case ids")
    trigger_cases = [case for case in cases if case.get("expected") == "trigger"]
    nontrigger_cases = [case for case in cases if case.get("expected") == "non_trigger"]
    require(len(trigger_cases) >= 6, "trigger count")
    require(len(nontrigger_cases) >= 8, "non-trigger count")
    for case in cases:
        require(case.get("expected") in {"trigger", "non_trigger"}, f"{case.get('id')}: expected")
        require(isinstance(case.get("request"), str) and len(case["request"]) >= 20, f"{case.get('id')}: request")
    folded_nontriggers = " ".join(case["request"].casefold() for case in nontrigger_cases)
    for marker in NONTRIGGER_MARKERS:
        require(marker in folded_nontriggers, f"non-trigger coverage: {marker}")

    for path in ROOT.rglob("*"):
        if path.is_file():
            checks += 1
            try:
                path.relative_to(ROOT).as_posix().encode("ascii")
            except UnicodeEncodeError:
                errors.append(f"non-ASCII path: {path.relative_to(ROOT)}")

    print(f"skill runtime checks: {checks}")
    if errors:
        print("result: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("result: PASS")
    print("validated: front matter, trigger boundaries, contract map, workflow order, stop/correction/delivery rules, metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
