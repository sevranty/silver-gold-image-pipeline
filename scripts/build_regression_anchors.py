#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "skills/silver-gold-image-pipeline/assets"
ANCHOR_PATHS = (
    "examples/accepted/product-light.svg",
    "examples/accepted/showcase-neutral.svg",
    "examples/accepted/transparency.svg",
    "examples/accepted/edit-preservation.svg",
    "examples/accepted/people-nonmetal-tissue.svg",
    "examples/accepted/text-logo-postprocess.svg",
    "examples/rejected/gold-dominance.svg",
    "examples/rejected/chrome-gloss.svg",
    "examples/rejected/obsidian-drift.svg",
    "examples/rejected/noisy-texture.svg",
    "examples/rejected/unreadable-silhouette.svg",
    "examples/ambiguous/weak-rim-light.svg",
    "examples/ambiguous/borderline-metal-allocation.svg",
)


def build(output_root: Path = ASSET_ROOT) -> dict[str, str]:
    """Materialize the canonical project-generated QA snapshot byte-for-byte."""
    hashes: dict[str, str] = {}
    for rel in ANCHOR_PATHS:
        source = ASSET_ROOT / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        data = source.read_bytes()
        target = output_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.resolve() != source.resolve():
            target.write_bytes(data)
        hashes[rel] = hashlib.sha256(data).hexdigest()
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize the canonical deterministic Silver-Gold QA anchor snapshot."
    )
    parser.add_argument("--output-root", type=Path, default=ASSET_ROOT)
    args = parser.parse_args()
    for path, digest in sorted(build(args.output_root).items()):
        print(f"{digest}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
