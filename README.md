# Silver-Gold Image Pipeline

A mono-style reference-to-image pipeline for producing new 3D assets with a matte or satin silver structure and controlled gold accents.

## Current scope

The repository foundation currently implements:

- plugin-ready repository architecture;
- the canonical Silver-Gold style contract;
- background delivery profiles for product and showcase surfaces;
- source provenance and normalization decisions;
- deterministic foundation validation.

The runtime `SKILL.md`, generator adapters, prompt pack, complete QA layer, packaging manifest, and visual golden set are tracked by separate issues and are intentionally not implemented in this foundation change.

## Core rule

Silver is the structural material and occupies 70-85% of the declared material allocation. Gold is an accent and occupies 15-30%. Surfaces are matte or satin, geometry is low-poly and faceted, lighting uses a controlled rim light, and reflections remain minimal.

## Architecture

- [Repository architecture](docs/architecture.md)
- [Decision log](docs/decision-log.md)
- [Style contract](skills/silver-gold-image-pipeline/references/style-spec.md)
- [Background profiles](skills/silver-gold-image-pipeline/references/background-profiles.md)
- [Source map](docs/source-map.md)
- [Versioning](docs/style-versioning.md)
- [Roadmap](docs/roadmap.md)

## Validation

Run the complete foundation validation locally:

```bash
python3 scripts/validate_foundation.py
```

The repository-only run checks structure, ASCII paths, case-insensitive brand-neutral runtime boundaries, style invariants, source-map metadata, background-profile luminance consistency, and regression semantics. When both provenance source paths are supplied, it also verifies their NFC-normalized filenames and SHA-256 bytes.

## Digital trace

Every implementation change must follow:

```text
Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision
```

The source documents are used only as provenance inputs. They are not bundled into the public runtime package.
