# Generator adapters and capability routing

Adapter contract version: 0.1.0  
Status: accepted runtime contract  
Related issue: #9

## 1. Boundary

The pipeline produces one generator-neutral scene, generation, or edit contract. An adapter maps that contract to a currently available image capability. Generator names, model IDs, API flags, size enums, mask syntax, and provider-specific prompt syntax live only in adapter profiles.

Never infer support from a product name alone. At each run, select a versioned profile, verify required capabilities against current runtime evidence, and record the selected profile and every degradation in the output manifest.

Capability status is one of:

- `supported` — official documentation or direct runtime evidence confirms the requirement;
- `partial` — available with fidelity, precision, surface, or workflow limitations;
- `unsupported` — unavailable or not documented strongly enough to rely on;
- `unknown` is not allowed in an executable profile; unresolved capabilities are treated as `unsupported` until verified.

## 2. Canonical capabilities

Every profile declares:

- `text_to_image`;
- `reference_image_generation`;
- `image_editing`;
- `mask_or_region_editing`;
- `multi_reference`;
- `identity_preservation`;
- `composition_preservation`;
- `transparent_output`;
- `exact_text`;
- `aspect_ratio_control`;
- `resolution_control`;
- `seed_reproducibility`;
- `visible_final_output`;
- `iterative_editing`.

Each entry contains `status`, `evidence`, and `limitations`.

## 3. Routing

1. Load the generator-neutral contract.
2. Determine mandatory capabilities from mode, locks, mask, references, text/logo layers, alpha, ratio, resolution, and delivery surface.
3. Load candidate profiles from `assets/templates/capability-profiles.yaml`.
4. Reject profiles that mark any mandatory capability `unsupported`.
5. Rank remaining profiles by number of `supported` mandatory capabilities, then by fewer degradations.
6. Write `assets/templates/adapter-decision.yaml` before invoking a tool.
7. Serialize only through the selected adapter section.
8. Record actual tool/model/version and output behavior after invocation.

A profile is not evidence that a tool is present in the current environment. Runtime availability must also be true.

## 4. Hard routing rules

- Do not present regeneration as targeted editing.
- `edit` and `style_transfer` require image-editing support; fallback to generation is allowed only after explicit fidelity reduction and must not claim preserved pixels.
- Do not silently ignore extra references. If multi-reference is unsupported, either select a concern-preserving deterministic sequence, reduce fidelity explicitly, or stop.
- A prompt-guided mask is `partial` unless exact region boundaries are confirmed.
- Exact text and exact logos remain deterministic post-processing even when a model has strong text rendering.
- Native alpha may be used only when the selected model/version confirms it. Otherwise use a valid background profile and a verified deterministic removal step.
- Output bytes or a tool result are not user-visible delivery. The runtime must surface the artifact and confirm `DELIVERED`.
- Undocumented seed controls are treated as unsupported; reproducibility relies on contract, prompt, inputs, versions, and manifest evidence instead.

## 5. Fallback hierarchy

1. Native generation/edit capability satisfying all mandatory locks.
2. A supported capability with explicit fidelity reduction and no false preservation claim.
3. Split generation and deterministic post-processing for text, logos, transparency, crop, or format.
4. Stop with `CAPABILITY_UNSUPPORTED` when a mandatory lock would be lost.

Every fallback lists lost, preserved, and post-processed requirements.

## 6. Silver-Gold risk controls

Each adapter must repeat these manual QA risks:

- chrome or mirror amplification;
- Gold overfill;
- loss of matte/satin roughness;
- weak or uncontrolled rim light;
- noisy metallic texture;
- background-profile drift;
- black-gold or Obsidian-like drift;
- geometry smoothing that removes clean facets;
- identity/composition drift after iterative edits.

Provider quality claims never replace Gate 4 manual inspection.

## 7. Evidence baseline

Profiles are evidence snapshots, not permanent product guarantees.

### OpenAI native image generation

Checked 2026-07-15 against the official OpenAI image-generation guide. The guide documents text-to-image, image edits, image inputs, multi-turn editing, one or more reference images, prompt-guided masks, output size/quality/format controls, and model-dependent transparent backgrounds. It also states that mask shape adherence may be imprecise and that the current `gpt-image-2` does not support transparent backgrounds.

### Google Nano Banana / Gemini native image generation

Checked 2026-07-15 against the official Gemini API image-generation guide. The guide documents conversational text/image generation, image editing, multiple-reference composition, output aspect ratio and image-size controls, and multiple Nano Banana model profiles. SynthID and model/version behavior are provider properties, not SGP delivery evidence.

Official evidence URLs and retrieval dates live in `assets/templates/capability-profiles.yaml`.

## 8. Future adapters

A future profile starts from `generic-runtime-detected`. It must not copy optimistic statuses from another provider. Promote a capability only with official documentation or direct runtime evidence, add routing fixtures, and rerun adapter validation.
