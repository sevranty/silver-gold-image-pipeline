# Decision log

## ADR-0001: Use a mono-style plugin-ready repository architecture

Status: accepted  
Date: 2026-07-15  
Related issue: #1

### Context

The repository must remain independently installable while supporting both a plain Agent Skill and Codex plugin packaging. Detailed style and QA rules must not inflate the runtime orchestration file.

### Decision

- The repository contains exactly one style: Silver-Gold.
- Runtime orchestration, detailed references, assets, scripts, tests, and repository documentation are separate layers.
- Each rule has one canonical owner file.
- The future `SKILL.md` is a short orchestrator and does not duplicate detailed contracts.
- Runtime files remain brand-neutral.
- Every implementation follows `Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision`.

### Consequences

- Neighboring mono-style repositories can evolve independently.
- Packaging can change without changing the visual contract.
- Contributors must update source-of-truth files rather than copying rules.

## ADR-0002: Resolve background ambiguity with two delivery profiles

Status: accepted  
Date: 2026-07-15  
Related issues: #1, #4

### Context

The source style specification allows a dark or neutral background. The broader visual architecture positions the style for light-theme product integration. Enforcing either rule globally would remove a legitimate use case.

### Decision

- Silver-Gold remains one style.
- `product-light` is the default profile.
- `showcase-neutral` is selected only for hero, presentation, repository, editorial preview, or explicitly requested neutral showcase surfaces.
- Pure black is not a production background for this style.
- Transparent output is a post-processing delivery mode, not a third visual profile.
- Logos and exact text are separate deterministic production steps.

### Consequences

- Product use has a predictable default.
- Showcase use remains possible without drifting into black-gold or obsidian-like aesthetics.
- Prompts, QA, adapters, and regression cases must reference a profile ID.

## ADR-0003: Normalize source rules into a brand-neutral style contract

Status: accepted  
Date: 2026-07-15  
Related issues: #1, #3

### Context

The source documents combine reusable style rules with organization-specific ownership, product scope, platform guidance, and internal artifact names.

### Decision

- Reusable visual rules are normalized into `style-spec.md`.
- Source files and their checksums are recorded in `docs/source-map.md`.
- Organization names, internal RACI, internal artifact IDs, fixed brand colors, and product-specific governance remain outside runtime.
- The source documents are not shipped in the runtime package.
- Declared metal allocation is machine-checkable; actual visual allocation is verified manually.

### Consequences

- The public skill can be reused across projects.
- Provenance remains auditable without leaking internal operating context.
- Static tooling cannot claim pixel-perfect material measurement.
