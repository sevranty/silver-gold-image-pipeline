# Silver-Gold Image Pipeline

A mono-style reference-to-image pipeline for producing new 3D assets with a matte or satin silver structure and controlled gold accents.

## Current scope

The repository currently implements:

- plugin-ready repository architecture;
- canonical `SKILL.md` runtime orchestration and OpenAI presentation metadata;
- the canonical Silver-Gold style contract;
- `product-light` and `showcase-neutral` background profiles;
- source provenance and normalization decisions;
- reference roles, priority, multi-reference precedence, and source-quality evidence;
- semantic, identity, object, composition, palette, text, and mandatory style locks;
- generator-neutral scene, generation, and edit contracts;
- a ten-block prompt pack with semantic negative groups;
- five quality gates, a weighted QA scorecard, and critical rejection criteria;
- output manifest and explicit user-visible delivery states;
- operational safety/rights decisions for people, text, logos, privacy, provenance, and public fixtures;
- evidence-backed OpenAI, Nano Banana, and future-generator capability routing;
- deterministic foundation, runtime-contract, policy, skill-runtime, and adapter validation.

The complete static validation suite, visual evaluation suite, plugin packaging, and production README are tracked by separate issues.

## Core rule

Silver is the structural material and occupies 70-85% of the declared material allocation. Gold is an accent and occupies 15-30%. Surfaces are matte or satin, geometry is low-poly and faceted, lighting uses a controlled rim light, and reflections remain minimal.

## Runtime

- [Canonical SKILL.md](skills/silver-gold-image-pipeline/SKILL.md)
- [Reference analysis](skills/silver-gold-image-pipeline/references/reference-analysis.md)
- [Workflow and locks](skills/silver-gold-image-pipeline/references/workflow-and-locks.md)
- [Prompt patterns](skills/silver-gold-image-pipeline/references/prompt-patterns.md)
- [Quality gates](skills/silver-gold-image-pipeline/references/quality-gates.md)
- [Output delivery](skills/silver-gold-image-pipeline/references/output-delivery.md)
- [Safety and rights](skills/silver-gold-image-pipeline/references/safety-and-rights.md)
- [Generator adapters](skills/silver-gold-image-pipeline/references/generator-adapters.md)

## Architecture

- [Repository architecture](docs/architecture.md)
- [Decision log](docs/decision-log.md)
- [Style contract](skills/silver-gold-image-pipeline/references/style-spec.md)
- [Background profiles](skills/silver-gold-image-pipeline/references/background-profiles.md)
- [Source map](docs/source-map.md)
- [Versioning](docs/style-versioning.md)
- [Roadmap](docs/roadmap.md)

## Validation

```bash
python3 scripts/validate_foundation.py
python3 scripts/validate_runtime_contracts.py
python3 scripts/validate_policy.py
python3 scripts/validate_skill_runtime.py
python3 scripts/validate_adapters.py
```

Static validators check structure, declared contracts, trigger boundaries, policy actions, adapter routing, fixtures, and brand-neutrality. They do not claim perceptual visual quality.

## Digital trace

Every implementation change must follow:

```text
Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision
```

The source documents are used only as provenance inputs. They are not bundled into the public runtime package.
