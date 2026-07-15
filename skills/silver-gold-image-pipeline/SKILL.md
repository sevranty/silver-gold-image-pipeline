---
name: silver-gold-image-pipeline
description: Transform one or more available reference images into a new or edited Silver-Gold image while preserving explicit subject, identity, object, composition, text, and delivery constraints. Use for reference-to-image generation, edits, style transfer, reinterpretation, composites, and sketch-to-render. Do not use for analysis-only requests, simple crop/resize/compression/format conversion, or when no usable target/reference image is available.
---

# Silver-Gold Image Pipeline

Use this skill only when the user expects a generated or edited image in the internal Silver-Gold style. Do not offer a style chooser and do not load external style packs.

## Load contract map

Load only the files needed for the active stage:

- input evidence and reference roles: `references/reference-analysis.md`;
- people, text, logo, privacy, and rights decisions: `references/safety-and-rights.md`;
- modes, locks, precedence, scene brief, and iteration budget: `references/workflow-and-locks.md`;
- visual invariants: `references/style-spec.md`;
- background selection: `references/background-profiles.md`;
- prompt assembly: `references/prompt-patterns.md`;
- quality gates and diagnostics: `references/quality-gates.md`;
- manifest and user-visible delivery: `references/output-delivery.md`;
- generator routing: `references/generator-adapters.md` when it exists.

Never replace these contracts with remembered wording.

## Trigger

Run for a request that both:

1. supplies or clearly identifies at least one usable visual target/reference; and
2. asks to create, transform, restyle, reinterpret, composite, render, or edit an image in Silver-Gold.

Supported modes:

- `generate`;
- `edit`;
- `style_transfer`;
- `reinterpretation`;
- `composite`;
- `sketch_to_render`.

## Do not trigger

Do not run for:

- analysis, critique, captioning, classification, or prompt-only work without image generation;
- crop, resize, compression, format conversion, metadata removal, or background removal without a generative transformation;
- requests for a different style;
- text-only ideation with no requested image output;
- a claimed target that is missing, inaccessible, invented, or represented only by an opaque identifier.

For a missing target/reference, request the actual image or stop. Never pretend an unavailable image was inspected.

## Required runtime

1. Confirm that every required image is actually available.
2. Select exactly one supported transformation mode.
3. Assign reference roles and concern-specific priorities.
4. Create the reference analysis card.
5. Run the safety and rights decision. Continue only on `pass`; pause on `block`; stop on `reject`.
6. Create all active locks, including the mandatory style lock.
7. Select one background profile and create the scene brief.
8. Route generate-like modes to the generation specification and image-preserving modes to the edit contract.
9. Assemble the prompt and run preflight QA.
10. Invoke an available image-generation or image-edit capability through the adapter contract.
11. Inspect the result manually at full and target size.
12. Diagnose one error category and apply at most two targeted corrections; allow one full restart.
13. Run technical validation and write the output manifest.
14. Surface the final image to the user.

Do not skip intermediate contracts because a tool accepts a free-form prompt.

## Hard invariants

Reference `references/style-spec.md` for detail. At runtime, ensure the declared material allocation remains Silver 70-85% and Gold 15-30%, surfaces remain matte or satin, reflections remain minimal, geometry remains clean and faceted, and lighting uses a controlled rim light.

Exact text and exact logos are deterministic production layers. Do not count stochastic rendering as exact.

## Stop conditions

Stop or block before generation when:

- the target/reference is missing or unusable;
- required identity, text, logo, permission, or mask evidence is unresolved;
- reference conflicts would silently weaken an active lock;
- Silver/Gold ratios do not sum to 100;
- no available capability can preserve mandatory locks;
- the policy decision is `block` or `reject`.

Stop before delivery when any quality gate fails, a critical defect remains, the artifact cannot be opened, or the final image is not user-visible.

## Edit discipline

For `edit` and `style_transfer`, state:

- `Change`;
- `Keep unchanged`;
- `May vary`;
- `Must not appear`.

Copy actual active-lock invariants into `Keep unchanged`. Correct one diagnostic category per iteration. Do not silently switch an image-preserving request to free generation.

## Completion

A successful tool call is not completion. Only a validated artifact that is visibly surfaced to the user may end as `DELIVERED`. Record a missing user-facing result as `DELIVERY_MISSING` and attempt one delivery repair without regenerating pixels.
