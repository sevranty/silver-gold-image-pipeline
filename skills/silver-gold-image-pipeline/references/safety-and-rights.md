# Safety and rights policy

Policy version: 0.1.0  
Status: accepted runtime contract  
Related issue: #10

## 1. Purpose

This policy converts people, text, logo, privacy, provenance, and reference-rights risks into explicit runtime actions. It is an operational gate, not a legal opinion. The runtime records the available evidence, chooses the least-destructive compliant action, and stops when a required permission, source asset, or usable reference is missing.

Allowed actions:

- `proceed` — continue under the declared locks;
- `transform` — preserve allowed content while changing risky or unsupported treatment;
- `post_process` — reserve a deterministic production layer after generation;
- `request_asset` — require an actual authorized source file;
- `lower_fidelity` — reduce a preservation promise to the supported evidence/capability level;
- `stop` — do not generate or deliver.

## 2. Mandatory decision record

Before prompt assembly, create `assets/templates/policy-decision.yaml`. Record:

- stable decision and scene IDs;
- subject category;
- source availability and quality;
- permission or provenance status;
- requested fidelity and supported fidelity;
- text, logo, privacy, and style-reference risks;
- selected actions and rationale;
- required deterministic layers;
- public-fixture eligibility;
- stop reasons and user-visible limitation.

No unknown permission is converted into `authorized` by assumption.

## 3. People

### Categories

Classify a depicted person as exactly one of:

- `user_self`;
- `private_adult`;
- `public_person`;
- `child`;
- `fictional_character`;
- `not_applicable`.

### Identity

- Fidelity never exceeds source quality or generator capability.
- `identity_lock` lists the visible identity-critical features to preserve and the allowed deviations.
- For edit and style-transfer iterations, repeat the active identity invariants.
- When identity evidence is insufficient, use `lower_fidelity` or `stop`; do not invent certainty.
- Do not infer sensitive personal attributes from appearance.

### Living tissue

Silver-Gold applies by default to objects, clothing, accessories, props, architecture, environment, or an explicitly requested sculptural representation.

Do not turn skin, eyes, teeth, hair, wounds, or other living tissue into metal by default. When the user explicitly requests a statue, mannequin, trophy, or non-living sculptural interpretation, use `transform`, make the non-living interpretation explicit, and preserve no claim of photographic realism.

### Children

- Use conservative, age-appropriate treatment.
- Do not sexualize, mature, expose, injure, humiliate, or place a child in an exploitative context.
- Do not use a child's image as a public bundled fixture.
- If safe transformation cannot be guaranteed, use `stop`.

## 4. Exact text

Exact text is a production constraint, not a decorative hint.

- Record wording, language, case, line breaks, placement, contrast, and safe area in `text_lock`.
- If the generator cannot render exact text reliably, generate without the text and use `post_process`.
- Inspect spelling, case, punctuation, contrast, crop, and absence of pseudo-text at full and target size.
- If the exact wording is unavailable or contradictory, use `request_asset` or `stop`.
- Stochastic text output never satisfies an exact-text gate by itself.

## 5. Logos and marks

- Do not use stochastic generation as the primary method for an exact logo.
- Use only a provided or otherwise authorized logo asset.
- Record source, status, permitted use, placement rules, and file hash.
- Reserve the safe area during generation and add the logo with `post_process`.
- Never bundle third-party brand assets in the public runtime unless redistribution status is explicitly recorded.
- If authorization or the source asset is missing, use `request_asset`; if the logo is mandatory and cannot be supplied, use `stop`.
- Do not invent endorsements, certifications, partnerships, or source attribution.

## 6. References, composition, and style

- Separate subject meaning, functional construction, composition, camera, environment, and material treatment.
- Transfer only the concerns owned by the declared reference roles and locks.
- Do not copy watermarks, signatures, accidental artifacts, personal data, or irrelevant identifiers.
- Do not describe the output as an exact imitation of a named contemporary creator.
- An external `style_reference` never replaces the internal Silver-Gold contract. Use `transform` to the internal contract or `stop` when the request depends on exact external style identity.
- Avoid unnecessary replication of a protected composition or uniquely identifying decorative detail; prefer a new arrangement that preserves the requested task and function.
- Bundled anchors and examples require a provenance/status record.

## 7. Privacy and public fixtures

Before any image or metadata enters a public fixture:

- remove EXIF and geolocation;
- remove names, email addresses, phone numbers, account IDs, faces of private people, private addresses, document numbers, and other personal data;
- exclude confidential screenshots, internal documents, access tokens, private URLs, and unreleased product information;
- use synthetic, self-created, public-domain, or explicitly redistributable material;
- record source type, license/status, sanitization, and redistribution decision;
- verify that filenames and embedded metadata contain no private identifiers.

`public_fixture_eligible: true` is allowed only when provenance is known, redistribution is allowed, personal data is absent, metadata is sanitized, and no internal/confidential material remains.

## 8. Decision matrix

| Risk | Default action | Escalation |
|---|---|---|
| insufficient identity evidence | `lower_fidelity` | `stop` when fidelity is mandatory |
| private-person image without clear use basis | `request_asset` | `stop` when unresolved |
| child in unsafe or exploitative treatment | `stop` | none |
| living tissue would be metallized by default | `transform` | `stop` if non-living interpretation is rejected |
| exact text required | `post_process` | `request_asset` or `stop` when wording is missing |
| exact logo required | `request_asset` + `post_process` | `stop` when mandatory asset/authorization is missing |
| unknown reference redistribution status | `request_asset` | exclude from public fixtures |
| named contemporary creator imitation | `transform` to internal contract | `stop` if exact imitation is essential |
| PII, EXIF, geolocation, confidential material | sanitize and `transform` | `stop` if sanitization cannot be verified |
| unsupported generator capability | `lower_fidelity` or supported fallback | `stop` when a mandatory lock would be lost |

## 9. Gate integration

### Input gate

Fail or stop when:

- a required image is unavailable;
- identity fidelity exceeds evidence;
- a mandatory logo/text asset is missing;
- permission/provenance status is unresolved for a required exact asset;
- a public fixture contains private or confidential material.

### Scene and prompt gates

- carry policy actions into `preserve`, `change`, `exclude`, capability assumptions, and deterministic-layer requirements;
- keep living tissue natural unless an explicit non-living sculptural transform is selected;
- exclude stochastic exact text/logo claims;
- preserve every active identity invariant in edit-like modes.

### Delivery gate

- manifest records policy decision ID, deterministic layers, provenance status, limitations, and public-fixture eligibility;
- delivery does not imply permission or endorsement;
- do not deliver when a stop reason remains active.

## 10. Public runtime boundary

The public runtime contains only generic policy logic. It contains no organization names, internal governance, embedded brand assets, private source documents, fixed brand colors, personal data, or confidential examples.
