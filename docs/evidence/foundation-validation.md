# Foundation validation evidence

Date: 2026-07-15  
Branch: `agent/issues-1-4-3-foundation`  
Base: `main@ae8cfaf84db04e2edd5c8394a905825568cd22ff`  
Initial review anchor: `28fe01eedb98a829f1c8aa06c210ad4c3673eb54`  
Validated implementation HEAD: `516aa4618a86d23bbadbf18614b176d6237767a8`  
Scope: #1, #4, #3  
Validation type: owner review + local deterministic validation  
Network required: no

The evidence commit is created after validation and changes only this report. The exact final PR HEAD is revalidated and attested in the PR review comment before Ready and merge.

## Review findings resolved

| Severity | Finding | Resolution |
|---|---|---|
| P1 | Source map used translated rather than exact source filenames | Recorded exact/NFC-normalized filenames and filename-normalization policy |
| P1 | Validator checked only that SHA strings existed | Added optional source-byte verification with exact filename and SHA-256 checks |
| P1 | Regression fixture validation checked IDs only | Added schema, profile, outcome, ratio, list-content, and background-luminance checks |
| P2 | Runtime brand scan was case-sensitive | Added case-insensitive token-aware matching and self-tests |
| P1 | `#24262B` contradicted the declared showcase luminance floor | Corrected the range to `0.018-0.36` and added luminance validation |
| P1 | Silver was incorrectly required to be the brightest material family | Replaced with structural/material dominance |
| P2 | Style contract duplicated background and delivery ownership | Restored `background-profiles.md` and future output delivery as canonical owners |
| P2 | Roadmap marked orchestration Issue #1 complete | Kept #1 open while marking only its foundation slice implemented |

## Repository-only validation

Command:

```bash
python3 scripts/validate_foundation.py
```

Result:

```text
foundation checks: 130
source-byte verification: not requested
result: PASS
validated: architecture, ownership boundaries, style contract, background profiles, provenance metadata, regression semantics
```

Output SHA-256: `35aa83ba5bcc4b465cc0e392ab5f53bb6af2b18ddb9d4aa035c2617ed92606b7`

## Source-byte validation

Command:

```bash
python3 scripts/validate_foundation.py \
  --style-source "/mnt/data/FDS [visual-style] Стиль Silver-Gold v3.1 (2026-02-24).docx" \
  --architecture-source "/mnt/data/FDS [visual-architecture] Архитектура визуальных стилей Финуслуг v2 (август 2025).docx"
```

Result:

```text
foundation checks: 136
source-byte verification: enabled
result: PASS
validated: architecture, ownership boundaries, style contract, background profiles, provenance metadata, regression semantics
```

Output SHA-256: `5331308400baf118ec8a08d97bae048ad73878c5f421acb171746e9c8e522060`

Verified source SHA-256:

- style source: `9ba60cb1454efd657f8457f74b930c538eeba49637aa03d14984ffd8ff3961e4`;
- architecture source: `8bfc102c9f52597a5696f4717d37add41057caa79f047401134e799d5dde589b`.

Validator SHA-256: `8eb4c48bb9c77ee597374942d895fa21cfd8c30397ce0d95ac1de73db37da00a`

## Negative mutation tests

### Lowercase brand leakage

A temporary copy appended `lowercase finuslugi leak` to the runtime style contract. Validation failed as required:

```text
runtime brand leakage in skills/silver-gold-image-pipeline/references/style-spec.md: Finuslugi
```

### Invalid showcase pass background

A temporary copy changed `showcase-neutral-pass` to `#000000`. Validation failed as required:

```text
showcase-neutral-pass pass background outside profile luminance range
```

Temporary mutation copies were not committed.

## Limits

This validation does not evaluate generated pixels, perceptual material allocation, reference fidelity, or visual quality. Those checks remain owned by #6, #7, and #11.
