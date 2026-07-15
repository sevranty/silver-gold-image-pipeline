# Background profiles

Contract version: 0.1.0  
Status: accepted  
Related issue: #4

## 1. Decision

Silver-Gold is one style with two delivery profiles:

- `product-light` — default;
- `showcase-neutral` — explicit showcase profile.

A profile changes the background, contrast strategy, and crop behavior. It does not change material allocation, geometry, surface, or the Silver-Gold style identity.

## 2. Selection rules

Use `product-light` when the target is:

- product UI;
- a landing-page section with light content surfaces;
- onboarding or educational product content;
- a card, badge, status, or empty-state asset;
- unknown or unspecified.

Use `showcase-neutral` when the target is:

- a hero object;
- a presentation cover;
- repository artwork;
- an editorial preview;
- an explicitly requested dark-neutral or mid-neutral showcase.

Do not infer `showcase-neutral` only because the subject is premium. Surface and delivery context determine the profile.

## 3. Profile: product-light

### Background

- neutral white to light gray;
- recommended relative luminance: 0.82-1.00;
- no colored environment;
- no visible texture, grain, vignette, or gradient banding.

Examples of acceptable neutral backgrounds include `#F2F3F5`, `#F7F7F8`, and `#FFFFFF`. These are examples, not brand tokens.

### Object contrast

- silver must remain visibly darker than the immediate background on at least one major plane;
- gold remains 15-30% and must not become the only source of edge separation;
- the silhouette must remain readable when the image is reduced to the target size.

### Lighting

- controlled upper-rear rim light;
- restrained neutral key light;
- darker structural silver planes are allowed to preserve separation;
- no broad white glare or mirror highlight.

### Shadow

- one soft contact shadow or a tightly controlled grounding shadow;
- no dirty ambient cloud, floor texture, or hard photographic cast shadow.

### Safe area and crop

- keep critical geometry inside the central 80% width and 76% height;
- reserve at least 10% on the left and right;
- reserve at least 12% on the top and bottom;
- crop may remove non-critical shadow falloff but must not remove gold logic points or silhouette-defining edges.

### Rejection criteria

Reject when:

- the silver object dissolves into the background;
- the result reads as white plastic instead of silver;
- gold is used to compensate for missing silver contrast;
- the background contains a colored scene or visual noise;
- mirror glare replaces controlled material shading.

## 4. Profile: showcase-neutral

### Background

- neutral mid-gray to dark graphite;
- recommended relative luminance: 0.018-0.36;
- pure black `#000000` is not allowed;
- no colored environment, material texture, or luminous gradient.

Examples of acceptable neutral backgrounds include `#24262B`, `#34373D`, `#4B4F56`, and `#62666D`. These are examples, not brand tokens.

### Object contrast

- silver remains the dominant structural material family;
- at least one major silver plane and the outer silhouette must separate from the background;
- the result must not read as black material with gold accents.

### Lighting

- controlled neutral key light plus restrained rim light;
- enough light to reveal silver structure and faceting;
- no black-gold dominance;
- no warm global lighting that recolors silver.

### Shadow

- shadow may be reduced or omitted when the object is optically isolated;
- any shadow must remain neutral and subordinate;
- no black floor that merges with the background.

### Safe area and crop

- keep critical geometry inside the central 76% of both dimensions;
- reserve at least 12% on all sides;
- repository and hero crops must preserve the full primary silhouette;
- optional text space belongs outside the object safe area.

### Rejection criteria

Reject when:

- the background is pure black;
- the object reads as obsidian, black chrome, or black-gold sculpture;
- silver no longer dominates;
- warm gold light recolors the full object;
- the silhouette disappears into the background.

## 5. Transparent output

Transparent output is a delivery mode, not a third style profile.

Required process:

1. generate or edit using `product-light` unless a different source profile is explicitly needed;
2. preserve clean silhouette separation;
3. remove the background with deterministic post-processing;
4. inspect alpha edges at full size and target size;
5. retain a source render with its original profile in the output manifest.

Do not request transparency when the available generator cannot provide or support reliable alpha. Do not represent background removal as native editing when it is post-processing.

## 6. Text and logos

Exact text and logos are not generated as part of the material render.

- reserve a safe area when text is required;
- add exact text in a deterministic production step;
- use only a provided or licensed logo asset;
- record source and placement in the output manifest;
- never bundle organization logos in the universal runtime.

## 7. Profile invariants

Both profiles must preserve:

- 70-85% declared silver allocation;
- 15-30% declared gold allocation;
- matte or satin surface;
- low-poly or faceted geometry;
- clean edges and sharp folds;
- controlled rim light;
- minimal reflections;
- no jewelry, baroque, chrome, mirror, liquid-metal, or gold-dominant result.
