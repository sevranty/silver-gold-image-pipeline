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

## ADR-0004: Require intermediate analysis, locks, and typed prompt contracts

Status: proposed in Draft PR #16  
Date: 2026-07-15  
Related issues: #1, #5

### Context

A direct reference-to-prompt jump hides conflicts, overstates fidelity, and makes edit iterations destructive. Multiple references also need concern ownership rather than a single global priority.

### Decision

- Every image receives an explicit role and priority.
- Reference analysis records source quality, uncertainty, transferable features, and conflicts before generation.
- Concern ownership is evaluated before numeric priority.
- `silver_gold_style_lock` is mandatory at fidelity 4.
- Scene briefs are generator-neutral and ratios must sum to 100.
- Generate and edit contracts are separate.
- Prompt assembly uses ten ordered semantic blocks.
- One targeted correction fixes one diagnostic category; budget is two corrections plus one full restart.

### Consequences

- Runtime behavior becomes auditable and generator-independent.
- Low-quality evidence cannot silently become a high-fidelity promise.
- Future adapters must map typed blocks and record unsupported capabilities.

## ADR-0005: Make quality gates and user-visible delivery hard lifecycle boundaries

Status: proposed in Draft PR #16  
Date: 2026-07-15  
Related issues: #1, #6

### Context

A high aggregate score can conceal a critical style, semantic, or delivery failure. Tool success also does not prove that the user received an image.

### Decision

- Five gates run sequentially: input, scene, prompt, visual, technical delivery.
- Pass requires at least 85/100, category minimums, all gates, and no critical defects.
- Visual QA is manual at full and target size.
- Critical defects reject independently of score.
- `DELIVERY_MISSING` is a failure state when generation succeeds but the image is not surfaced.
- Only `DELIVERED` is a successful terminal state.

### Consequences

- Static tools cannot claim subjective visual compliance.
- Runtime must retain evidence, limitations, iterations, and delivery state in the manifest.
- Empty final responses cannot be treated as successful completion.
