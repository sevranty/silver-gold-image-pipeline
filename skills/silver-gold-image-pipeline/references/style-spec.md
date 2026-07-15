# Silver-Gold style contract

Style core version: 0.1.0  
Status: accepted  
Related issue: #3  
Background contract: `background-profiles.md`

## 1. Definition

Silver-Gold is a mono-style 3D system in which matte or satin silver forms the structural body of the subject and gold is used only for controlled edges, symbols, seams, connectors, or logic points.

The style uses low-poly or faceted geometry, clean edges, sharp folds, controlled symmetry, restrained rim lighting, dense clean shadows, and minimal reflections. The intended tone is stable, engineered, and valuable without demonstrative luxury.

## 2. Material roles

### Silver

Silver is the structural material.

- declared allocation: 70-85%;
- forms the body, mass, load-bearing planes, and primary silhouette;
- remains visually dominant under both background profiles;
- may vary from light silver to dark silver planes while remaining recognizably metallic.

### Gold

Gold is an accent material.

- declared allocation: 15-30%;
- marks boundaries, symbols, seams, connectors, interfaces, or deliberate attention points;
- cannot become the base body material;
- cannot be used as a full-object coating;
- must remain subordinate when viewed at target size.

### Allocation verification

Machine-readable scene contracts must declare integer `silver_ratio` and `gold_ratio` values that:

- sum to 100;
- keep silver within 70-85;
- keep gold within 15-30.

Declared ratios do not prove visual compliance. Final visual allocation requires manual QA at full size and target size.

## 3. Geometry

Required:

- low-poly, faceted, or deliberately planar construction;
- clean edges;
- sharp folds or controlled bevels;
- readable primary silhouette;
- controlled symmetry or intentional geometric balance;
- minimal decorative micro-detail.

Allowed:

- one primary object;
- one visually connected object group when the group reads as a single asset;
- simplified mechanical or architectural construction;
- controlled asymmetry when required by the reference.

Reject:

- soft amorphous liquid-metal forms;
- baroque ornament;
- jewelry-like faceting used only for sparkle;
- noisy microgeometry;
- realistic manufacturing clutter that destroys the silhouette.

## 4. Surface

Required:

- matte or satin silver;
- matte or satin gold accent;
- controlled micro-roughness;
- clean, untextured material response.

Reject:

- glossy;
- mirror;
- chrome-like;
- highly reflective;
- liquid metal;
- glitter;
- scratched, dirty, grunge, brushed-noise, or corroded surfaces;
- rainbow or colored reflections.

A small local highlight may exist to explain form. It must not become a mirrored environment reflection.

## 5. Lighting and shadows

Required:

- one coherent lighting direction;
- controlled rim light that explains silhouette or major folds;
- restrained neutral key light;
- dense, clean, intentional shadows;
- no uncontrolled HDR response.

The rim light supports geometry. It must not create a glowing outline around every edge.

Reject:

- multiple conflicting key lights;
- blown highlights;
- mirror-bright white bands;
- warm global light that recolors silver;
- noisy ambient shadows;
- photographic environment reflections.

## 6. Composition

Required:

- one dominant subject or one visually connected group;
- controlled negative space;
- clear hierarchy;
- readable silhouette at target size;
- background profile selected from `background-profiles.md`.

The reference may control subject, identity, construction, camera, and composition through future locks. It cannot override the Silver-Gold material and surface contract.

## 7. Emotional tone

The result should communicate:

- structure;
- stability;
- technological control;
- elevated value;
- restraint.

The result must not communicate:

- ostentatious wealth;
- jewelry advertising;
- baroque luxury;
- casino aesthetics;
- black-gold secrecy;
- decorative precious-metal excess.

## 8. Asset profiles

These are asset subtypes, not separate styles.

### Icon or object

- one compact subject;
- strong silhouette;
- reduced detail;
- target-size readability is critical.

### Badge or status

- clear outer geometry;
- gold marks status logic rather than filling the badge;
- text is added separately when exact wording is required.

### Hero object

- larger controlled negative space;
- more visible planar construction;
- requests `showcase-neutral` only when the delivery context satisfies `background-profiles.md`.

### Product-surface object

- requests `product-light` according to `background-profiles.md`;
- preserves UI and text contrast;
- keeps shadow and detail subordinate to the surrounding interface.

## 9. Background behavior

`background-profiles.md` is the exclusive source of truth for profile IDs, default selection, tonal ranges, safe areas, crop behavior, transparency, and background-specific rejection criteria.

This style contract only requires that a valid profile be selected and that profile selection never changes material allocation, geometry, surface, or lighting invariants.

## 10. Critical rejection criteria

Reject the result regardless of other quality scores when any of the following is present:

- silver is not the dominant structural material;
- gold is the body or visually dominates;
- declared ratios are outside the allowed ranges;
- glossy, mirror, chrome, or liquid-metal surface;
- jewelry, baroque, or ornament-first aesthetic;
- black-gold or obsidian-like reading;
- noisy texture, scratches, dirt, grunge, or colored reflection;
- missing readable silhouette;
- wrong primary subject or lost reference-critical construction;
- selected background profile is violated.

## 11. Tolerated variation

The following may vary when the scene contract does not lock them:

- exact silver tone;
- exact gold temperature within a natural metallic range;
- camera angle;
- amount of negative space;
- bevel width;
- shadow softness;
- position of rim light;
- degree of symmetry.

Variation is acceptable only when all critical invariants remain intact.

## 12. Verification matrix

| Invariant | Static verification | Manual visual QA |
|---|---|---|
| Declared silver 70-85 | required | confirm silver visually dominates |
| Declared gold 15-30 | required | confirm gold remains accent |
| Ratios sum to 100 | required | not applicable |
| Matte or satin surface intent | required contract marker | confirm no gloss or mirror response |
| Low-poly or faceted geometry | required contract marker | confirm readable planar structure |
| Clean edges and sharp folds | required contract marker | confirm silhouette and construction |
| Controlled rim light | required contract marker | confirm light is restrained and coherent |
| Minimal reflections | required contract marker | confirm no environment reflection |
| Background profile | required profile ID | confirm contrast, safe area, and crop |
| Emotional restraint | not deterministic | confirm no jewelry or luxury drift |

## 13. Runtime neutrality

This contract contains no organization-specific logo, brand color, internal ownership model, product list, or design-system artifact identifier. Such source context is retained only in `docs/source-map.md`.
