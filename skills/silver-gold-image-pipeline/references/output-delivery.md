# Output delivery contract

Manifest schema version: 0.1.0  
Status: accepted runtime contract  
Related issue: #6

## 1. Completion definition

The workflow is complete only when a validated final image is visibly delivered to the user. Tool success, an internal file path, a manifest without an asset, or a blank final response is not completion.

## 2. Delivery states

- `PLANNED` — scene and output requirements exist;
- `GENERATED` — an image artifact exists but QA is incomplete;
- `QA_PASSED` — all gates pass and no critical defect remains;
- `DELIVERED` — final image is surfaced to the user and confirmed in the manifest;
- `DELIVERY_MISSING` — generation succeeded but no user-visible image is present;
- `REJECTED` — a gate or critical defect prevents delivery.

Only `DELIVERED` is a successful terminal state.

## 3. Required assets

- final image;
- preview when the final format is not directly viewable or is too large;
- output manifest;
- optional source render for transparent post-processing;
- optional deterministic text/logo overlay source when requested.

The final image and preview must be real accessible artifacts, not invented paths.

## 4. Technical requirements

- ASCII filename using lowercase letters, numbers, hyphens, and one extension;
- format and extension agree;
- dimensions and aspect ratio match the scene brief within declared tolerance;
- alpha state is explicit;
- file opens and has non-zero dimensions;
- hash and file size are recorded;
- target-size preview is inspected;
- crop preserves required safe areas and logic points.

Recommended filename pattern:

```text
silver-gold-{asset-type}-{short-subject}-{width}x{height}.{ext}
```

## 5. Manifest requirements

`output-manifest.yaml` records:

- schema and contract versions;
- skill, pipeline, style, background, prompt, QA, and manifest versions;
- transformation mode and background profile;
- reference IDs, roles, priorities, and active locks;
- generator/tool/model/mode and capability limitations;
- iterations and diagnostic categories;
- gate results, score, critical defects, and known limitations;
- final, preview, source-render, and deterministic-overlay file records with hashes, sizes, dimensions, formats, and alpha;
- delivery state and `user_visible` boolean.

Optional file records remain present with `required: false` and null metadata until produced. No limitation may be omitted to make a fallback look equivalent to the requested mode.

## 6. User response

The final response must contain the actual image/tool result or a valid artifact link supported by the runtime. It may briefly state format and dimensions. It must not expose internal reasoning or claim delivery when `user_visible` is false.

When the image cannot be surfaced:

1. set `delivery_state: DELIVERY_MISSING`;
2. do not mark Gate 5 passed;
3. attempt one supported delivery repair without regenerating pixels;
4. if still missing, report the failure explicitly and retain the validated artifact path in evidence only when it actually exists.

## 7. Transparent output

Transparency follows `background-profiles.md`:

- generate a source render with a valid profile;
- perform deterministic background removal when supported;
- inspect alpha edges;
- record source render and post-processing method;
- do not claim native alpha generation when it was post-processed.

## 8. Text and logos

Exact text and logos are deterministic production layers:

- use only provided/authorized content;
- preserve the reserved safe area;
- record source asset and placement;
- inspect the composite at full and target size;
- record the deterministic overlay as a file object in the output manifest;
- damage to required text/logo is a critical defect.

## 9. Stop rules

Do not deliver when:

- any quality gate fails;
- a critical defect remains;
- final or preview file cannot be opened;
- manifest contradicts the actual artifact;
- the result is not visible to the user.
