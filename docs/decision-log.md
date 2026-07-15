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
