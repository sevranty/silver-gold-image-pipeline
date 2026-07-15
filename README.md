# Silver-Gold Image Pipeline

A mono-style reference-to-image pipeline for producing new 3D assets with a matte or satin silver structure and controlled gold accents.

## Foundation status

This branch begins the repository foundation with the plugin-ready architecture from #1. The Silver-Gold style contract and background delivery profiles are implemented as subsequent commits linked to #3 and #4.

The runtime `SKILL.md`, generator adapters, prompt pack, complete QA layer, packaging manifest, and visual golden set remain owned by separate issues.

## Architecture

- [Repository architecture](docs/architecture.md)
- [Decision log](docs/decision-log.md)
- [Versioning](docs/style-versioning.md)
- [Roadmap](docs/roadmap.md)

## Digital trace

Every implementation change must follow:

```text
Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision
```

The source documents are provenance inputs only and are not bundled into the public runtime package.
