# Workflow and locks contract

Contract version: 0.1.0  
Pipeline core version: 0.2.0  
Status: proposed runtime contract  
Related issue: #5

## 1. Mandatory stage order

```text
input availability
-> reference roles
-> reference analysis card
-> conflict resolution
-> locks
-> scene brief
-> generation or edit specification
-> prompt preflight
-> generation/edit
-> visual QA
-> targeted correction
-> technical validation
-> user-visible delivery
```

No stage may be skipped because a generator accepts a direct free-form prompt.

## 2. Transformation modes

Exactly one mode is selected:

- `generate` — create a new image from semantic and visual evidence;
- `edit` — modify an available target image while preserving protected content;
- `style_transfer` — preserve content/composition while replacing incompatible material treatment with Silver-Gold;
- `reinterpretation` — preserve semantic intent with controlled freedom in construction or composition;
- `composite` — combine owned concerns from multiple references;
- `sketch_to_render` — turn a sketch or simplified form into a coherent Silver-Gold render.

`generate` uses `generation-spec.yaml`. `edit` and edit-like corrections additionally require `edit-contract.yaml`.

## 3. Locks

Every lock has:

- `enabled`;
- `fidelity` from 0 to 4;
- `source_reference_ids`;
- explicit `preserve` statements;
- explicit allowed deviations;
- evidence and uncertainty.

### Fidelity scale

- `0` — unlocked;
- `1` — preserve broad category only;
- `2` — preserve major recognizable attributes;
- `3` — preserve detailed structure and arrangement;
- `4` — preserve as closely as capability permits; stop when evidence is insufficient.

### Required locks

- `semantic_lock` — subject, action, purpose, narrative meaning;
- `identity_lock` — person, character, product, or unique object identity;
- `object_lock` — construction, topology, parts, count, orientation;
- `composition_lock` — camera, framing, placement, scale, negative space;
- `palette_lock` — non-metal environmental palette only; cannot override style materials;
- `text_lock` — exact wording, language, placement, and deterministic production requirement;
- `silver_gold_style_lock` — mandatory, always enabled, fidelity 4.

The style lock preserves:

- Silver 70-85% as structural material;
- Gold 15-30% as accent;
- matte or satin response;
- low-poly/faceted geometry;
- clean edges and sharp folds;
- controlled rim light;
- minimal reflections;
- no chrome, mirror, liquid metal, jewelry, baroque, grunge, or gold dominance.

## 4. Lock precedence

When locks conflict:

1. safety/rights/capability stop rules;
2. `silver_gold_style_lock` for material and style concerns;
3. `text_lock` and `identity_lock` for exact protected content;
4. `object_lock`;
5. `semantic_lock`;
6. `composition_lock`;
7. `palette_lock` and environment preferences.

The conflict must be recorded; no lock is silently weakened.

## 5. Scene brief

The scene brief is generator-neutral and must contain:

- `schema_version` and `contract_version`;
- asset type and target surface;
- transformation mode;
- selected background profile from `background-profiles.md`;
- subject, action, environment;
- camera, composition, safe area;
- declared `silver_ratio` and `gold_ratio`, summing to 100;
- references to style/material/geometry/lighting rules rather than duplicated prose;
- `preserve`, `change`, and `exclude` lists;
- output aspect ratio, width, height, alpha requirement, and target-size check;
- capability assumptions and unresolved risks.

## 6. Edit contract

An edit contract must identify:

- target image and mask when available;
- protected regions;
- editable regions;
- one diagnostic category to fix;
- `keep_unchanged` invariants copied from active locks;
- expected visible change;
- stop condition;
- iteration number and remaining budget.

An edit instruction that says only “improve the image” is invalid.

## 7. Iteration protocol

Diagnostic categories:

- `semantic_error`;
- `identity_error`;
- `composition_error`;
- `metal_ratio_error`;
- `material_error`;
- `reflection_error`;
- `lighting_error`;
- `background_error`;
- `geometry_error`;
- `text_error`;
- `technical_error`.

Rules:

- correct one category per targeted iteration;
- repeat every `keep_unchanged` invariant on each edit;
- allow at most two targeted corrections;
- allow at most one full restart after targeted corrections fail or the primary subject is wrong;
- stop rather than silently relax identity, text, style, or delivery constraints.

## 8. Completion boundary

Generation tool success is not workflow completion. Completion requires Gate 5 in `quality-gates.md` and a user-visible image according to `output-delivery.md`.
