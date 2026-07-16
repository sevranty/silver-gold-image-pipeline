# Repository agent instructions

## Scope

This repository contains one mono-style reference-to-image pipeline: Silver-Gold. Do not add a style selector, external style resolver, or runtime dependency on neighboring style repositories.

## Canonical sources

Each rule has one owner file:

- runtime trigger, stage order, stop conditions, and completion boundary: `skills/silver-gold-image-pipeline/SKILL.md`;
- repository boundaries and dependency direction: `docs/architecture.md`;
- accepted architecture decisions: `docs/decision-log.md`;
- Silver-Gold visual invariants: `skills/silver-gold-image-pipeline/references/style-spec.md`;
- background selection and delivery behavior: `skills/silver-gold-image-pipeline/references/background-profiles.md`;
- reference roles and evidence fields: `skills/silver-gold-image-pipeline/references/reference-analysis.md`;
- workflow, locks, precedence, and iteration budget: `skills/silver-gold-image-pipeline/references/workflow-and-locks.md`;
- prompt block assembly and contradictions: `skills/silver-gold-image-pipeline/references/prompt-patterns.md`;
- QA gates, scorecard, and diagnostic mapping: `skills/silver-gold-image-pipeline/references/quality-gates.md`;
- output states and user-visible delivery: `skills/silver-gold-image-pipeline/references/output-delivery.md`;
- people, text, logo, privacy, provenance, and public-fixture decisions: `skills/silver-gold-image-pipeline/references/safety-and-rights.md`;
- generator capability evidence, routing, degradation, and fallback: `skills/silver-gold-image-pipeline/references/generator-adapters.md`;
- runtime package include/exclude boundaries and release gates: `release/package-contract.yaml`;
- plugin identity and distribution metadata: `.codex-plugin/plugin.json`;
- manual visual verdict rules: `docs/visual-rubric.md`;
- trigger, workflow, visual coverage, anchor hashes, and provenance: `tests/cases/` plus `skills/silver-gold-image-pipeline/assets/anchors/`;
- provenance and normalization: `docs/source-map.md`;
- version semantics: `docs/style-versioning.md`.

`SKILL.md` orchestrates these contracts by reference. It must not duplicate their detailed rules.

## Runtime neutrality

Files under `skills/` must not contain organization names, internal design-system names, embedded logos, fixed brand colors, internal RACI, or product-specific governance. Source provenance belongs in `docs/source-map.md`, outside the runtime package.

Synthetic visual anchors must be marked as project-generated QA examples. Never describe them as outputs from an image generator or as proof of production visual quality.

## Package boundary

Build the runtime archive only through `scripts/build_plugin_package.py`. The builder must derive its file set from `release/package-contract.yaml`. Repository docs, source documents, tests, release planning, visual anchors, and evaluation examples must not enter the standalone runtime archive.

A package is valid only when archive bytes, generated manifest, checksum, required runtime references, and standalone installation all pass validation. Packaging does not imply tag or GitHub Release publication.

## Required workflow boundary

The final runtime must support this direction:

```text
reference analysis
-> safety and rights decision
-> locks
-> scene brief
-> adapter decision
-> generation or edit specification
-> prompt preflight
-> generation or edit
-> full-size visual QA
-> target-size visual QA
-> targeted correction
-> technical validation
-> user-visible final image
```

A successful generation call without surfacing the final image to the user is not completion. Record it as `DELIVERY_MISSING`.

## Change discipline

- Use ASCII file and directory names.
- Use one Issue per coherent implementation scope.
- Create changes on a dedicated branch.
- Keep commits intentional and reference the relevant Issue.
- Open a Draft PR before lifecycle review.
- Attach validation evidence to the repository and PR.
- Do not mark work ready or merge without a separate decision.

## WebFactoryOS orchestration handoff

- SGP owns this repository's skill code, runtime package, QA contracts, assets, validation, and releases.
- WebFactoryOS owns any external registry, routing status, and cross-project relation records.
- External WebFactoryOS relations grant no write access to SGP files, settings, releases, or runtime behavior.
- SGP has no WebFactoryOS runtime, CI, package, grammar, workflow, or registry dependency.
- Link external WebFactoryOS sources instead of copying their registry records, grammar, workflow, or implementation into this repository.

## Validation

Run the complete offline suite:

```bash
python3 scripts/validate_all.py
```

Validate and install the standalone package:

```bash
python3 scripts/build_plugin_package.py --out-dir dist
python3 scripts/validate_plugin_package.py --archive dist/silver-gold-image-pipeline-0.1.0.zip --manifest dist/silver-gold-image-pipeline-0.1.0.zip.manifest.json --checksum dist/silver-gold-image-pipeline-0.1.0.zip.sha256
python3 scripts/test_installation.py
```

Individual CLIs support `--json` and return `0` on pass, `2` on validation failure, and argparse's non-zero usage code for invalid invocation.

Static validation does not claim visual quality. Perceptual material allocation, identity, construction, composition, full-size quality, and target-size readability require manual visual QA.
