#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from validation_common import ascii_path, emit

REQUIRED = (
    "skills/silver-gold-image-pipeline/SKILL.md",
    "skills/silver-gold-image-pipeline/references/style-spec.md",
    "skills/silver-gold-image-pipeline/references/background-profiles.md",
    "skills/silver-gold-image-pipeline/references/reference-analysis.md",
    "skills/silver-gold-image-pipeline/references/workflow-and-locks.md",
    "skills/silver-gold-image-pipeline/references/prompt-patterns.md",
    "skills/silver-gold-image-pipeline/references/quality-gates.md",
    "skills/silver-gold-image-pipeline/references/output-delivery.md",
    "skills/silver-gold-image-pipeline/references/safety-and-rights.md",
    "skills/silver-gold-image-pipeline/references/generator-adapters.md",
    "skills/silver-gold-image-pipeline/agents/openai.yaml",
)
BANNED = ("finuslugi", "финуслуги", "moex", "finkit", "#ff0508")


def validate(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"missing required path: {relative}")
    non_ascii = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and not ascii_path(p.relative_to(root))]
    errors.extend(f"non-ASCII path: {path}" for path in non_ascii)
    skill = root / "skills/silver-gold-image-pipeline/SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
        if not match:
            errors.append("SKILL.md missing YAML front matter")
        else:
            front = match.group(1)
            if "name: silver-gold-image-pipeline" not in front:
                errors.append("SKILL.md name mismatch")
            if "description:" not in front:
                errors.append("SKILL.md description missing")
    runtime_root = root / "skills/silver-gold-image-pipeline"
    runtime = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in runtime_root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".yaml", ".yml", ".json"}
    ).casefold() if runtime_root.exists() else ""
    for term in BANNED:
        if term in runtime:
            errors.append(f"runtime brand leakage: {term}")
    return errors, {"required_paths": len(REQUIRED), "non_ascii_paths": len(non_ascii)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors, details = validate(root)
    return emit("validate_skill_structure", str(root), errors, details=details, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
