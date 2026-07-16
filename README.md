# Silver-Gold Image Pipeline

A mono-style reference-to-image pipeline for producing new 3D assets with a matte or satin silver structure and controlled gold accents.

## Current scope

The repository currently implements:

- plugin-ready repository architecture and a versioned plugin manifest;
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
- a complete offline static validation and packaging suite;
- trigger, workflow, rejection-matrix, and manual visual regression contracts with deterministic synthetic QA anchors;
- deterministic standalone ZIP packaging, archive manifests, checksums, and installation smoke tests.

The benchmarked production README is tracked by Issue #12.

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

## Evaluation

- [Manual visual rubric](docs/visual-rubric.md)
- [Trigger cases](tests/cases/trigger-cases.yaml)
- [Workflow cases](tests/cases/workflow-cases.yaml)
- [Visual regression cases](tests/cases/visual-regression-cases.yaml)
- [Rejection matrix](tests/cases/rejection-matrix.yaml)
- [Manual visual review records](docs/evidence/visual-manual-review.json)
- [Anchor provenance](skills/silver-gold-image-pipeline/assets/anchors/provenance.yaml)
- [Reproducibility manifest](skills/silver-gold-image-pipeline/assets/anchors/reproducibility-manifest.yaml)

Synthetic SVG anchors are repository-generated structural QA examples. They are not image-generator outputs and do not prove production visual quality. Every visual verdict requires manual review at full size and target size.

## Architecture

- [Repository architecture](docs/architecture.md)
- [Decision log](docs/decision-log.md)
- [Style contract](skills/silver-gold-image-pipeline/references/style-spec.md)
- [Background profiles](skills/silver-gold-image-pipeline/references/background-profiles.md)
- [Source map](docs/source-map.md)
- [Versioning](docs/style-versioning.md)
- [Roadmap](docs/roadmap.md)

## Plugin package

The release package contains only the plugin manifest, license notices, changelog, canonical runtime skill, runtime references, and runtime templates. Repository documentation, source documents, tests, visual anchors, and evaluation examples are excluded.

Build the deterministic package:

```bash
python3 scripts/build_plugin_package.py --out-dir dist
```

Validate source metadata, archive bytes, generated manifest, and checksum:

```bash
python3 scripts/validate_plugin_package.py --archive dist/silver-gold-image-pipeline-0.1.0.zip --manifest dist/silver-gold-image-pipeline-0.1.0.zip.manifest.json --checksum dist/silver-gold-image-pipeline-0.1.0.zip.sha256
```

Run the standalone installation smoke test:

```bash
python3 scripts/test_installation.py
```

Packaging prepares v0.1.0 but does not create a tag or GitHub Release. Release publication is a separate lifecycle decision.

## Validation

Run every deterministic offline check:

```bash
python3 scripts/validate_all.py
```

Individual CLIs:

```text
validate_skill_structure.py
validate_scene_spec.py
validate_prompt.py
validate_manifest.py
validate_regression_suite.py
validate_visual_evidence.py
validate_plugin_package.py
test_installation.py
inspect_image.py
package_asset.py
build_plugin_package.py
```

Static validators check structure, declared contracts, contextual prompt rules, trigger boundaries, policy actions, adapter routing, manifests, raster metadata, packaging, regression coverage, manual-review evidence, provenance, checksums, and brand-neutrality. They do not claim perceptual visual quality.

## Digital trace

Every implementation change must follow:

```text
Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision
```

The source documents are used only as provenance inputs. They are not bundled into the public runtime package.
