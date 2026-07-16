# Architecture

Status: accepted runtime-contract foundation  
Architecture version: 0.2.0  
Related issues: #1, #3, #4, #5, #6, #25

## 1. Purpose

`silver-gold-image-pipeline` is a standalone mono-style Agent Skill repository. It transforms one or more visual references into a new image while preserving explicitly locked content and applying one internal Silver-Gold style contract.

The architecture supports two distribution modes:

1. a standalone Agent Skill;
2. a Codex plugin package that points to the same skill directory.

Packaging metadata must never become the source of truth for runtime behavior.

## 2. Non-goals

The current runtime-contract foundation does not:

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
        +--> reference analysis and conflict evidence
        +--> locks and scene brief
        +--> Silver-Gold style contract
        +--> background delivery profiles
        +--> generation/edit specification
        +--> prompt patterns and future adapters
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

Future paths remain owned by their dedicated issues.

## 5. Source-of-truth matrix

| Concern | Canonical file | Consumers | Must not be duplicated in |
|---|---|---|---|
| Repository boundaries and dependency direction | `docs/architecture.md` | contributors, future runtime | README, plugin manifest |
| Accepted architecture decisions | `docs/decision-log.md` | all modules | issue comments as sole record |
| Visual style invariants | `skills/silver-gold-image-pipeline/references/style-spec.md` | prompts, QA, evals, adapters | future `SKILL.md` |
| Background selection and delivery behavior | `skills/silver-gold-image-pipeline/references/background-profiles.md` | scene spec, prompts, QA, evals | style selector |
| Reference roles and evidence fields | `skills/silver-gold-image-pipeline/references/reference-analysis.md` | locks, scene brief, QA | prompt patterns |
| Workflow order, locks, precedence, and iteration budget | `skills/silver-gold-image-pipeline/references/workflow-and-locks.md` | future `SKILL.md`, tests | style contract |
| Prompt construction and contradiction rules | `skills/silver-gold-image-pipeline/references/prompt-patterns.md` | future adapters, preflight | architecture |
| Manual visual QA, scorecard, and diagnostic mapping | `skills/silver-gold-image-pipeline/references/quality-gates.md` | runtime, evals | static scripts as visual claims |
| User-visible output and delivery states | `skills/silver-gold-image-pipeline/references/output-delivery.md` | runtime, manifest | tool logs only |
| Source provenance and normalization | `docs/source-map.md` | maintainers, reviewers | runtime package |
| Version semantics | `docs/style-versioning.md` | manifest, changelog, evidence | model-specific adapters |
| Trigger behavior and runtime routing | future `SKILL.md` | runtime | detailed reference files |
| Generator capabilities and fallback routing | future `generator-adapters.md` | runtime | prompt patterns |
| Safety and rights | future `safety-and-rights.md` | input gate, runtime | style contract |

## 6. Runtime load order

The future runtime must load contracts in this order:

1. validate input availability;
2. assign reference roles and priority;
3. create a reference analysis card;
4. resolve or stop on conflicts;
5. create locks and a scene brief;
6. load `style-spec.md`;
7. select a background profile from `background-profiles.md`;
8. build a generation or edit specification;
9. assemble prompt blocks;
10. apply a generator adapter;
11. run prompt preflight;
12. generate or edit;
13. perform manual visual QA at full and target size;
14. apply one-category targeted correction within budget;
15. run technical validation;
16. surface the final image to the user and record `DELIVERED`.

## 7. Contract boundaries

### Reference analysis

Owns image roles, priority, source quality, observations, uncertainty, transferability, and conflict evidence. It never owns style.

### Workflow and locks

Owns transformation modes, lock semantics, fidelity, precedence, scene-brief requirements, edit protocol, and iteration budget.

### Style contract

Owns material roles, numeric allocation, geometry, surface, lighting, reflection limits, composition tone, and style rejection criteria.

### Background profiles

Owns default selection, allowed tonal ranges, contrast, lighting adaptation, contact shadow behavior, safe areas, crop behavior, transparent-output handling, and background-specific rejection criteria.

### Prompt patterns

Owns semantic block order, generate/edit separation, required meanings, negative groups, and contradiction checks. Model syntax remains outside this contract.

### Quality gates

Owns gate evidence, manual visual review, weighted score, critical defects, and diagnostic-to-correction mapping. A score cannot override a critical defect.

### Output delivery

Owns delivery states, manifest evidence, file checks, user-visible completion, and `DELIVERY_MISSING` repair behavior.

### Static validation

May validate structure, fields, declared ratios, versions, required markers, forbidden runtime leakage, files, and fixture semantics. It must not claim subjective visual compliance.

## 8. Brand-neutral runtime boundary

The public runtime package must not include:

- organization or product names;
- internal design-system identifiers;
- embedded logos;
- fixed brand accent colors;
- internal ownership or RACI;
- platform-specific governance inherited from source documents.

Generic material rules, geometry, light, composition, locks, prompt structure, QA, and delivery contracts may be normalized into the runtime.

## 9. WebFactoryOS orchestration boundary

SGP owns this repository's skill code, runtime package, QA contracts, assets, validation, and releases.

WebFactoryOS owns external registry, routing status, and cross-project relation records. Those external relations grant no write access to SGP files, settings, releases, or runtime behavior.

SGP has no WebFactoryOS runtime, CI, package, grammar, workflow, or registry dependency. Link WebFactoryOS sources instead of copying their contracts into this repository.

## 10. Digital trace

Every change must retain:

- linked Issue numbers;
- dedicated branch;
- intentional commits;
- Draft PR;
- validation command and result;
- exact HEAD for review evidence;
- review decision;
- changelog entry when release scope begins.

## 11. Maturity model

### Foundation

Architecture, style contract, background decision, provenance, and basic static validation.

### Runtime-contract foundation

Reference analysis, locks, scene/prompt contracts, quality gates, delivery contract, focused fixtures, and runtime validation.

### Runtime MVP

`SKILL.md`, safety/rights policy, generator adapters, and at least one proven end-to-end generator path.

### Production candidate

Complete validation scripts, trigger suite, visual regression set, packaging, installation test, and owner review.

### Release

Version tag and release notes only after a separate lifecycle decision.
