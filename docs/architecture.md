# Architecture

Status: accepted runtime-contract foundation  
Architecture version: 0.2.0  
Related issues: #1, #3, #4, #5, #6, #25
Status: accepted production-candidate architecture  
Architecture version: 0.3.0  
Related issues: #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #25

## 1. Purpose

`silver-gold-image-pipeline` is a standalone mono-style Agent Skill repository. It transforms one or more visual references into a new image while preserving explicitly locked content and applying one internal Silver-Gold style contract.

The architecture supports two distribution modes:

1. a standalone Agent Skill;
2. a Codex plugin package that points to the same skill directory.

Packaging metadata and external orchestration metadata must never become sources of truth for runtime behavior.

## 2. Non-goals

The repository does not:

- implement or bundle a generator API or model engine;
- provide a style chooser;
- provide pixel-perfect automatic style scoring;
- embed organization logos, brand colors, or internal design-system governance;
- make WebFactoryOS a runtime, package, validation, or CI dependency;
- publish a production release before the project-level release gate.

## 3. Repository layers

```text
repository documentation and local handoff
        |
        v
runtime orchestration (SKILL.md)
        |
        +--> reference analysis and conflict evidence
        +--> safety and rights decisions
        +--> locks and scene brief
        +--> Silver-Gold style contract
        +--> background delivery profiles
        +--> generation/edit specification
        +--> prompt patterns and generator adapters
        +--> quality gates and output delivery
        |
        v
assets, scripts, tests, evidence and package
```

Dependency direction is one-way. Detailed reference files may be loaded by the runtime. Reference files must not depend on repository marketing content, private source documents, or WebFactoryOS implementation.

## 4. Repository structure

```text
silver-gold-image-pipeline/
|-- README.md
|-- AGENTS.md
|-- TASK.md
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
|-- release/
`-- docs/
    |-- architecture.md
    |-- decision-log.md
    |-- source-map.md
    |-- style-versioning.md
    |-- roadmap.md
    `-- evidence/
```

## 5. Source-of-truth matrix

| Concern | Canonical file | Consumers | Must not be duplicated in |
|---|---|---|---|
| Repository boundaries and dependency direction | `docs/architecture.md` | contributors, future runtime | README, plugin manifest |
| Local WebFactoryOS ownership boundary and routing links | `TASK.md` | contributors, orchestration handoff | runtime, WFO registry copy |
| Accepted architecture decisions | `docs/decision-log.md` | all modules | issue comments as sole record |
| Trigger behavior and runtime routing | `skills/silver-gold-image-pipeline/SKILL.md` | runtime | detailed reference files |
| Visual style invariants | `skills/silver-gold-image-pipeline/references/style-spec.md` | prompts, QA, evals, adapters | future `SKILL.md` |
| Background selection and delivery behavior | `skills/silver-gold-image-pipeline/references/background-profiles.md` | scene spec, prompts, QA, evals | style selector |
| Reference roles and evidence fields | `skills/silver-gold-image-pipeline/references/reference-analysis.md` | locks, scene brief, QA | prompt patterns |
| Workflow order, locks, precedence, and iteration budget | `skills/silver-gold-image-pipeline/references/workflow-and-locks.md` | `SKILL.md`, tests | style contract |
| Prompt construction and contradiction rules | `skills/silver-gold-image-pipeline/references/prompt-patterns.md` | adapters, preflight | architecture |
| Generator capabilities and fallback routing | `skills/silver-gold-image-pipeline/references/generator-adapters.md` | runtime | prompt patterns |
| Safety and rights | `skills/silver-gold-image-pipeline/references/safety-and-rights.md` | input gate, runtime | style contract |
| Manual visual QA, scorecard, and diagnostic mapping | `skills/silver-gold-image-pipeline/references/quality-gates.md` | runtime, evals | static scripts as visual claims |
| User-visible output and delivery states | `skills/silver-gold-image-pipeline/references/output-delivery.md` | runtime, manifest | tool logs only |
| Package boundary and release gates | `release/package-contract.yaml` | builder, validator, release | README prose |
| Source provenance and normalization | `docs/source-map.md` | maintainers, reviewers | runtime package |
| Version semantics | `docs/style-versioning.md` | manifest, changelog, evidence | model-specific adapters |

The phrases `future runtime` and `future SKILL.md` are stable compatibility tokens consumed by the deterministic foundation validator. They do not describe the current implementation status; the runtime and `SKILL.md` are present.

## 6. Runtime load order

The runtime loads contracts in this order:

1. validate input availability;
2. assign reference roles and priority;
3. create a reference analysis card;
4. run the safety and rights decision;
5. resolve or stop on conflicts;
6. create locks and a scene brief;
7. load `style-spec.md`;
8. select a background profile from `background-profiles.md`;
9. build a generation or edit specification;
10. assemble prompt blocks;
11. apply a generator adapter;
12. run prompt preflight;
13. generate or edit;
14. perform manual visual QA at full and target size;
15. apply one-category targeted correction within budget;
16. run technical validation;
17. surface the final image to the user and record `DELIVERED`.

## 7. Contract boundaries

### Reference analysis

Owns image roles, priority, source quality, observations, uncertainty, transferability, and conflict evidence. It never owns style.

### Safety and rights

Owns policy actions for people, children, text, logos, privacy, reference rights, provenance, and public fixtures. It may pass, block, or reject before generation.

### Workflow and locks

Owns transformation modes, lock semantics, fidelity, precedence, scene-brief requirements, edit protocol, and iteration budget.

### Style contract

Owns material roles, numeric allocation, geometry, surface, lighting, reflection limits, composition tone, and style rejection criteria.

### Background profiles

Owns default selection, allowed tonal ranges, contrast, lighting adaptation, contact shadow behavior, safe areas, crop behavior, transparent-output handling, and background-specific rejection criteria.

### Prompt patterns

Owns semantic block order, generate/edit separation, required meanings, negative groups, and contradiction checks. Model syntax remains outside this contract.

### Generator adapters

Own capability evidence, runtime routing, degradation, fallback, and explicit unsupported-capability outcomes. They do not redefine style or locks.

### Quality gates

Owns gate evidence, manual visual review, weighted score, critical defects, and diagnostic-to-correction mapping. A score cannot override a critical defect.

### Output delivery

Owns delivery states, manifest evidence, file checks, user-visible completion, and `DELIVERY_MISSING` repair behavior.

### Static validation

May validate structure, fields, declared ratios, versions, required markers, forbidden runtime leakage, files, links, package bytes, and fixture semantics. It must not claim subjective visual compliance.

## 8. Brand-neutral runtime boundary

The public runtime package must not include:

- organization or product names;
- internal design-system identifiers;
- embedded logos;
- fixed brand accent colors;
- internal ownership or RACI;
- platform-specific governance inherited from source documents;
- WebFactoryOS registry records, relations, naming grammar, workflows or code.

Generic material rules, geometry, light, composition, locks, prompt structure, QA, and delivery contracts may be normalized into the runtime.

## 9. WebFactoryOS orchestration boundary

WebFactoryOS is an external orchestration system, not a dependency layer.

- SGP owns skill implementation, package, QA, assets, validation, tags and releases
- WebFactoryOS owns external project registration, route lookup, orchestration status and cross-project relations
- External relations grant no write access to SGP
- SGP Issues and PRs remain the execution source of truth
- SGP continues to install, validate and release without WebFactoryOS
- `TASK.md` records the local handoff and links the external routing and naming sources

## 10. Digital trace

Every change must retain:

- linked Issue numbers;
- dedicated branch;
- intentional commits;
- Draft PR;
- validation command and result;
- exact HEAD for review evidence;
- review decision;
- changelog entry when release scope changes.

## 11. Maturity model

### Foundation

Architecture, style contract, background decision, provenance, and basic static validation.

### Runtime MVP

`SKILL.md`, analysis and lock contracts, prompt pack, output delivery, policy layer, and generator-neutral adapters.

### Production candidate

Complete validation scripts, trigger suite, visual regression set, packaging, installation test, production README, and owner review.

### Release

Social preview proof, exact-main closure validation, immutable tag, package checksum, and verified release notes after a separate lifecycle decision.
