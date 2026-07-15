# Repository agent instructions

## Scope

This repository contains one mono-style reference-to-image pipeline: Silver-Gold. Do not add a style selector, external style resolver, or runtime dependency on neighboring style repositories.

## Canonical sources

Each rule has one owner file:

- repository boundaries and dependency direction: `docs/architecture.md`;
- accepted architecture decisions: `docs/decision-log.md`;
- Silver-Gold visual invariants: `skills/silver-gold-image-pipeline/references/style-spec.md`;
- background selection and delivery behavior: `skills/silver-gold-image-pipeline/references/background-profiles.md`;
- reference roles and evidence fields: `skills/silver-gold-image-pipeline/references/reference-analysis.md`;
- workflow, locks, precedence, and iteration budget: `skills/silver-gold-image-pipeline/references/workflow-and-locks.md`;
- prompt block assembly and contradictions: `skills/silver-gold-image-pipeline/references/prompt-patterns.md`;
- QA gates, scorecard, and diagnostic mapping: `skills/silver-gold-image-pipeline/references/quality-gates.md`;
- output states and user-visible delivery: `skills/silver-gold-image-pipeline/references/output-delivery.md`;
- provenance and normalization: `docs/source-map.md`;
- version semantics: `docs/style-versioning.md`.

Do not duplicate detailed rules in future `SKILL.md`. The runtime file must orchestrate these contracts by reference.

## Runtime neutrality

Files under `skills/` must not contain organization names, internal design-system names, embedded logos, fixed brand colors, internal RACI, or product-specific governance. Source provenance belongs in `docs/source-map.md`, outside the runtime package.

## Required workflow boundary

The final runtime must support this direction:

```text
reference analysis
-> locks
-> scene brief
-> generation or edit specification
-> prompt preflight
-> generation or edit
-> visual QA
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

## Validation

Run:

```bash
python3 scripts/validate_foundation.py
python3 scripts/validate_runtime_contracts.py
```

Static validation does not claim visual quality. Perceptual material allocation, identity, construction, composition, and target-size readability require manual visual QA.
