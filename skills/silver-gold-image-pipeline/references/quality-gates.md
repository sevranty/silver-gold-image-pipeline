# Quality gates contract

QA schema version: 0.1.0  
Status: proposed runtime contract  
Related issue: #6

## 1. Principle

Quality is evaluated through five sequential gates. A later gate cannot compensate for an earlier failure. Critical defects reject the result regardless of score.

Static scripts validate structure and declared values. Manual visual QA evaluates pixels, perceptual metal allocation, identity, construction, composition, and target-size readability.

## 2. Gate 1 — input

Pass evidence:

- every required target/reference image is available;
- each image has a role and priority;
- source quality supports requested fidelity;
- crop, blur, occlusion, text, logo, and rights limitations are recorded;
- unresolved conflicts have a stop/fallback decision.

Fail when the target is missing, an opaque ID is treated as an image, or fidelity 4 is promised from insufficient evidence.

## 3. Gate 2 — scene contract

Pass evidence:

- one valid transformation mode;
- complete reference analysis card;
- required locks including `silver_gold_style_lock`;
- valid background profile;
- integer Silver/Gold ratios within range and summing to 100;
- preserve/change/exclude are explicit;
- output requirements are internally consistent;
- capability assumptions are declared.

Fail when any mandatory field is absent or contradictory.

## 4. Gate 3 — prompt preflight

Pass evidence:

- all ten prompt blocks are present in canonical order;
- required Silver-Gold meanings are expressed;
- forbidden semantic groups are absent from positive instructions;
- negative constraints cover gloss, mirror, chrome, liquid metal, jewelry, gold dominance, baroque, grunge, colored reflections, and style mixing;
- background profile matches the scene brief;
- generate and edit contracts are not mixed;
- runtime is brand-neutral.

Fail on contradiction, hidden style substitution, or missing edit invariants.

## 5. Gate 4 — visual result

Inspect at full size and target size.

### Fidelity

- correct primary subject and action;
- identity and construction match active locks;
- composition and camera match declared fidelity;
- required text/logo regions are intact or reserved for deterministic placement.

### Silver-Gold compliance

- Silver remains the dominant structural material;
- Gold remains a 15-30% accent by declared contract and perceptual manual review;
- matte/satin materials;
- no mirror or environment reflection;
- low-poly/faceted geometry;
- clean edges and sharp folds;
- controlled rim light and coherent clean shadows;
- selected background profile is respected;
- no texture noise, gradient kitsch, extra metals, jewelry, baroque, or obsidian-like drift.

### Production fit

- silhouette and critical details survive target-size reduction;
- crop and safe area remain valid;
- no visible generation defects, broken anatomy, topology, or duplicated parts.

## 6. Gate 5 — technical delivery

Pass evidence:

- final format, dimensions, aspect ratio, alpha behavior, and file size match the contract;
- ASCII filename is valid and extension matches encoded content;
- preview and final asset open successfully;
- manifest records versions, reference roles, locks, generator capability, iterations, diagnostics, known limitations, and file hashes;
- user-visible delivery is confirmed.

A successful tool call with no surfaced image is `DELIVERY_MISSING`, not pass.

## 7. Scorecard

| Category | Weight | Minimum |
|---|---:|---:|
| task/semantic fidelity | 20 | 16 |
| reference locks | 15 | 11 |
| metal allocation | 15 | 12 |
| material/reflection compliance | 15 | 12 |
| geometry | 10 | 7 |
| lighting/shadows | 10 | 7 |
| composition/background profile | 10 | 7 |
| technical delivery | 5 | 5 |

Pass threshold:

- total score at least 85/100;
- every category meets its minimum;
- every gate passes;
- no critical defect is present.

Scores are manual evidence-backed points, not automated pixel similarity.

## 8. Critical rejection criteria

- `gold_base_material` — Gold is the body or visually dominates;
- `silver_not_dominant` — Silver is not the structural majority;
- `gloss_mirror_chrome` — glossy, mirror, chrome, or liquid-metal response;
- `jewelry_baroque` — ornamental precious-object aesthetic;
- `wrong_subject_or_meaning` — primary subject/action/meaning is wrong;
- `identity_or_construction_failure` — identity, anatomy, topology, or required parts are broken;
- `background_profile_failure` — selected profile is violated;
- `required_text_or_logo_damaged` — protected or deterministic text/logo requirement is damaged;
- `delivery_missing` — final image is not available to the user.

## 9. Diagnostic-to-correction mapping

| Diagnostic | Targeted correction | Keep unchanged |
|---|---|---|
| `semantic_error` | correct subject/action/meaning | style, valid identity, composition unless implicated |
| `identity_error` | restore identity-critical features | subject, camera, style, background |
| `composition_error` | correct framing/placement/camera | subject, identity, construction, style |
| `metal_ratio_error` | reduce/increase Gold only to declared allocation | geometry, identity, composition |
| `material_error` | replace gloss/noise with matte/satin response | ratios, geometry, subject |
| `reflection_error` | remove mirror/environment reflections | lighting direction, ratios, geometry |
| `lighting_error` | correct key/rim/shadows | subject, ratios, background |
| `background_error` | apply selected profile and contrast | subject, style, camera |
| `geometry_error` | restore clean faceted construction | identity, ratios, camera |
| `text_error` | restore reserved/protected text workflow | image content outside text region |
| `technical_error` | fix file/crop/alpha/dimensions | validated visual pixels where possible |

Only one diagnostic category may be corrected per targeted iteration.

## 10. Evidence

Use `assets/templates/qa-scorecard.yaml`. Every gate records `pass`, evidence, reviewer mode (`static`, `manual`, or `mixed`), and findings. The smoke-test example is stored in `tests/expected/smoke-test-qa-scorecard.yaml`.
