# Reference analysis contract

Contract version: 0.1.0  
Status: proposed runtime contract  
Related issue: #5

## 1. Purpose

Reference analysis converts one or more available images into explicit evidence before any scene or prompt is built. It records what is visible, what must be preserved, what may change, and what remains uncertain. It does not infer style from the reference: Silver-Gold style is always loaded from `style-spec.md`.

## 2. Reference roles

Each image has exactly one primary role and may have secondary roles.

| Role | Owns | Does not own |
|---|---|---|
| `subject_reference` | subject class, action, construction, object details | Silver-Gold style |
| `identity_reference` | face, body, character, product identity | composition unless also assigned |
| `composition_reference` | framing, camera, placement, negative space | identity or material |
| `environment_reference` | spatial context and environmental structure | style materials |
| `text_reference` | exact visible wording to preserve or reproduce deterministically | generated typography quality |
| `logo_reference` | licensed/provided logo shape and placement intent | permission to invent or redraw |
| `mask_reference` | editable and protected regions | semantic meaning outside the mask |

`style_reference` is not a valid role. External visual style references cannot override the internal Silver-Gold Style Contract.

## 3. Priority and precedence

Every reference receives integer `priority` from 1 to 100. Higher values win only within the same owned concern.

Conflict resolution order:

1. explicit user instruction;
2. safety, rights, and capability stop rules;
3. higher-priority reference that owns the concern;
4. more complete and less cropped evidence;
5. unresolved conflict recorded for user-visible handling or conservative fallback.

A high-priority composition reference cannot override identity evidence. A high-priority identity reference cannot replace object construction. Concern ownership is evaluated before numeric priority.

## 4. Required analysis fields

For every reference record:

- stable `reference_id`;
- role and priority;
- source availability and quality grade;
- subject and action;
- environment;
- composition and camera;
- observed lighting;
- identity-critical features;
- construction-critical features;
- transferable features;
- non-transferable features;
- crop, occlusion, blur, compression, and resolution limitations;
- uncertainty statements;
- unresolved conflicts;
- provenance note when text or logos are present.

## 5. Quality and uncertainty scales

### Source quality: 0-4

- `0` — unavailable or unusable;
- `1` — severe crop, blur, obstruction, or tiny resolution;
- `2` — usable only for broad subject/category information;
- `3` — sufficient for most declared locks;
- `4` — clear, complete, and suitable for high-fidelity preservation.

### Confidence: 0-4

- `0` — unknown;
- `1` — weak inference;
- `2` — plausible;
- `3` — well supported;
- `4` — directly visible and unambiguous.

Analysis must not silently upgrade a low-quality source into a high-fidelity promise.

## 6. Transferability

Transferable features may inform the new image:

- subject semantics;
- functional construction;
- camera and composition;
- action and pose;
- environmental structure;
- approved exact text or logo placement intent.

Non-transferable features include:

- external style identity;
- artist-specific signature traits;
- accidental compression artifacts;
- watermarks and unlicensed marks;
- glossy, chrome, jewelry, baroque, grunge, or other material treatment that conflicts with Silver-Gold;
- irrelevant background noise.

## 7. Multi-reference conflict record

A conflict record contains:

- `conflict_id`;
- concern: `subject`, `identity`, `object`, `composition`, `palette`, `environment`, `text`, or `mask`;
- competing reference IDs;
- selected resolution;
- rationale;
- residual risk;
- whether generation must stop.

Stop when identity, exact text, logo rights, or protected edit regions cannot be resolved safely. For lower-risk composition or environment ambiguity, choose the highest-owned priority and record the decision.

## 8. Output

The canonical analysis artifact is `assets/templates/reference-analysis-card.md`. A complete card is required before locks or a scene brief are created.
