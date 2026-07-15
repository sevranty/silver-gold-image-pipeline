# Prompt patterns contract

Prompt schema version: 0.1.0  
Status: accepted runtime contract  
Related issue: #5

## 1. Purpose

Prompt patterns convert an approved scene brief into generator-neutral semantic blocks. They do not own the Silver-Gold visual rules or background values; those remain in `style-spec.md` and `background-profiles.md`.

## 2. Canonical block order

1. `asset_and_use_case`;
2. `primary_subject_and_action`;
3. `required_construction_details`;
4. `composition_and_camera`;
5. `silver_gold_material_allocation`;
6. `geometry_and_edges`;
7. `background_profile`;
8. `lighting_shadows_reflections`;
9. `negative_constraints`;
10. `output_constraints`.

Blocks remain separate in `generation-spec.yaml`; a model adapter may serialize them, but may not reorder or omit them without a recorded limitation.

## 3. Required semantic markers

The assembled prompt must express all of the following meanings:

- matte or satin silver structural base;
- subtle and subordinate gold accents;
- declared Silver 70-85% and Gold 15-30%;
- low-poly, faceted, or deliberately planar object;
- clean edges and sharp folds or controlled bevels;
- controlled rim light and coherent neutral key light;
- dense clean shadows;
- minimal local highlights with no environment reflection;
- selected background profile ID and its delivery intent;
- target aspect ratio, size intent, safe area, and crop constraints.

## 4. Negative semantic groups

Negative constraints must cover meanings, not only exact tokens.

| Group | Disallowed meanings and examples |
|---|---|
| gloss | glossy, wet-look, lacquered, polished glare |
| reflection | reflective environment, mirrored surroundings, broad glare |
| chrome | chrome, black chrome, mirror metal |
| liquid metal | molten, fluid metal, mercury-like |
| jewelry | gemstone, jewelry advertising, ornamental sparkle |
| gold dominance | gold-covered, full gold coating, gold body |
| baroque | ornate, filigree, baroque decoration |
| surface noise | grunge, dirt, scratches, corrosion, brushed noise |
| colored reflection | rainbow reflections, neon metal contamination |
| style mixing | obsidian-like, black-gold secrecy, unrelated style pack |

The phrase `minimal reflections` is valid only as a bounded positive rule and must coexist with explicit rejection of mirror and environment reflections.

## 5. Generate pattern

Generate-like modes describe a new image. They must:

- use the scene brief as the only content source;
- name required construction details;
- include active locks by meaning;
- request the Silver-Gold contract without referencing organizations or external design systems;
- reserve exact text and logos for deterministic post-processing when required;
- avoid edit-only language such as “keep unchanged” unless a composite source requires it.

## 6. Edit pattern

Image-preserving modes `edit` and `style_transfer` use two sections:

### Change only

- one diagnostic category;
- one visible correction target;
- editable region or mask;
- expected change.

### Keep unchanged

- actual invariants copied from the active-lock snapshot;
- primary subject and identity;
- object construction not implicated in the correction;
- camera and composition unless `composition_error` is selected;
- all Silver-Gold style invariants;
- selected background profile unless `background_error` is selected;
- protected text, logo, and mask regions;
- dimensions and crop unless `technical_error` is selected.

An edit prompt must not introduce a second diagnostic category or replace the active-lock snapshot with a generic checklist.

## 7. Prompt contradiction checks

Reject preflight when:

- positive blocks request gloss, chrome, mirror, liquid metal, jewelry, baroque, grunge, or gold body;
- `silver_ratio + gold_ratio != 100`;
- material ratios in prompt blocks differ from the scene brief;
- the background profile is absent or not one of `product-light` and `showcase-neutral`;
- generate and edit instructions are mixed;
- `style_transfer` is routed as generate;
- an edit omits active `keep_unchanged` invariants;
- exact text or a logo is requested through stochastic generation despite a deterministic requirement;
- the prompt contains source-brand identifiers or an external style resolver.

## 8. Adapter boundary

This contract does not define model names, tool syntax, token limits, mask encoding, or multi-reference API fields. Those belong to #9 generator adapters. An adapter must record any omitted block, unsupported lock, or fallback in the output manifest.
