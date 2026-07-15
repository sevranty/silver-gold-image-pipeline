# Repository agent instructions

## Scope

This repository contains one mono-style reference-to-image pipeline: Silver-Gold. Do not add a style selector, external style resolver, or runtime dependency on neighboring style repositories.

## Canonical sources

Each rule has one owner file:

- repository boundaries and dependency direction: `docs/architecture.md`;
- accepted architecture decisions: `docs/decision-log.md`;
- Silver-Gold visual invariants: `skills/silver-gold-image-pipeline/references/style-spec.md`;
- background selection and delivery behavior: `skills/silver-gold-image-pipeline/references/background-profiles.md`;
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
-> generation specification
-> preflight QA
-> generation or edit
-> visual QA
-> targeted correction
-> technical validation
-> user-visible final image
```

A successful generation call without surfacing the final image to the user is not completion.

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
```

Do not claim visual quality from static validation. Material allocation and visual style compliance require manual visual QA in later tasks.
