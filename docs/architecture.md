# Architecture

Status: accepted foundation  
Architecture version: 0.1.0  
Related issues: #1, #3, #4

## 1. Purpose

`silver-gold-image-pipeline` is a standalone mono-style Agent Skill repository. It transforms one or more visual references into a new image while preserving explicitly locked content and applying one internal Silver-Gold style contract.

The architecture must work in two distribution modes:

1. a standalone Agent Skill;
2. a Codex plugin package that points to the same skill directory.

Packaging metadata must never become the source of truth for runtime behavior.

## 2. Non-goals

This foundation does not:

- implement a generator API or model-specific client;
- implement the final `SKILL.md`;
- provide a style chooser;
- provide pixel-perfect automatic style scoring;
- embed organization logos, brand colors, or internal design-system governance;
- publish a production release.

## 3. Repository layers

```text
repository documentation
        |
        v
runtime orchestration (future SKILL.md)
        |
        +--> reference analysis and locks
        +--> Silver-Gold style contract
        +--> background delivery profiles
        +--> generator-neutral generation specification
        +--> prompt patterns and adapters
        +--> quality gates and output delivery
        |
        v
assets, scripts, tests, evidence
```

Dependency direction is one-way. Detailed reference files may be loaded by the runtime. Reference files must not depend on repository marketing content or private source documents.

## 4. Target repository structure

```text
silver-gold-image-pipeline/
|-- README.md
|-- AGENTS.md
|-- LICENSE
|-- CHANGELOG.md
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   `-- silver-gold-image-pipeline/
|       |-- SKILL.md
|       |-- agents/
|       |   `-- openai.yaml
|       |-- references/
|       |   |-- style-spec.md
|       |   |-- background-profiles.md
|       |   |-- reference-analysis.md
|       |   |-- workflow-and-locks.md
|       |   |-- prompt-patterns.md
|       |   |-- generator-adapters.md
|       |   |-- quality-gates.md
|       |   |-- output-delivery.md
|       |   `-- safety-and-rights.md
|       |-- assets/
|       |   |-- templates/
|       |   |-- anchors/
|       |   `-- examples/
|       `-- scripts/
|-- scripts/
|-- tests/
|   |-- cases/
|   |-- fixtures/
|   `-- expected/
`-- docs/
    |-- architecture.md
    |-- decision-log.md
    |-- source-map.md
    |-- style-versioning.md
    |-- roadmap.md
    `-- evidence/
```

Only files implemented by the current issues are created in this change. Future paths remain owned by their dedicated issues.

## 5. Source-of-truth matrix

| Concern | Canonical file | Consumers | Must not be duplicated in |
|---|---|---|---|
| Repository boundaries and dependency direction | `docs/architecture.md` | contributors, future runtime | README, plugin manifest |
| Accepted architecture decisions | `docs/decision-log.md` | all modules | issue comments as sole record |
| Visual style invariants | `skills/silver-gold-image-pipeline/references/style-spec.md` | prompts, QA, evals, adapters | future `SKILL.md` |
| Background selection and delivery behavior | `skills/silver-gold-image-pipeline/references/background-profiles.md` | scene spec, prompts, QA, evals | style selector |
| Source provenance and normalization | `docs/source-map.md` | maintainers, reviewers | runtime package |
| Version semantics | `docs/style-versioning.md` | manifest, changelog, evidence | model-specific adapters |
| Full workflow order | future `SKILL.md` | runtime | style contract |
| Reference analysis and locks | future `reference-analysis.md`, `workflow-and-locks.md` | runtime, tests | style contract |
| Prompt construction | future `prompt-patterns.md` | adapters | architecture |
| Manual visual QA | future `quality-gates.md` | runtime, evals | static scripts |
| User-visible output | future `output-delivery.md` | runtime | tool logs only |

## 6. Runtime load order

The future runtime must load contracts in this order:

1. validate input availability;
2. load reference-analysis rules;
3. create locks and a scene brief;
4. load `style-spec.md`;
5. select a background profile from `background-profiles.md`;
6. build a generator-neutral specification;
7. apply a generator adapter;
8. run preflight checks;
9. generate or edit;
10. perform manual visual QA;
11. apply targeted correction within the iteration budget;
12. run technical validation;
13. surface the final image to the user.

## 7. Contract boundaries

### Style contract

Owns material roles, numeric allocation, geometry, surface, lighting, reflection limits, composition, emotional tone, and rejection criteria.

### Background profiles

Owns default selection, allowed tonal ranges, contrast, lighting adaptation, contact shadow behavior, safe areas, crop behavior, transparent-output handling, and background-specific rejection criteria.

### Runtime orchestration

Will own trigger selection, stop conditions, workflow sequence, and tool invocation. It must reference style and background contracts instead of restating them.

### Static validation

May validate structure, fields, declared ratios, required markers, forbidden runtime leakage, files, and checksums. It must not claim subjective visual compliance.

## 8. Brand-neutral runtime boundary

The public runtime package must not include:

- organization or product names;
- internal design-system identifiers;
- embedded logos;
- fixed brand accent colors;
- internal ownership or RACI;
- platform-specific governance inherited from source documents.

Generic material rules, geometry, light, composition, and QA criteria may be normalized into the runtime.

## 9. Digital trace

Every change must retain:

- linked Issue numbers;
- dedicated branch;
- intentional commits;
- Draft PR;
- validation command and result;
- source hashes when provenance changes;
- review decision;
- changelog entry when release scope begins.

## 10. Maturity model

### Foundation

Architecture, style contract, background decision, provenance, and basic static validation.

### Runtime MVP

`SKILL.md`, analysis and lock contracts, prompt pack, output delivery, policy layer, and at least one supported generator capability.

### Production candidate

Full validation scripts, trigger suite, visual regression set, packaging, installation test, and owner review.

### Release

Version tag and release notes only after a separate lifecycle decision.
