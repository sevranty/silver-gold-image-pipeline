# Runtime contracts validation evidence

Date: 2026-07-15  
Branch: `agent/issues-5-6-runtime-contracts`  
Base: `main@9a82929d09a9f4537a1e537bc4c0884d42c00fcd`  
Initial implementation HEAD: `2fc097ad43d5d6aa50e20d0e2d2d27eace05622c`  
Reviewed implementation HEAD: `d63002e1ccc84c0a0d954361afb79610994e0cdb`  
Draft PR: #16  
Scope: #5, #6  
Validation type: independent owner-review + deterministic local validation  
Network required by validators: no

The evidence commit changes only repository evidence. The exact final PR HEAD is rechecked after this report is committed and is attested in the PR review submission.

## Owner-review findings resolved

| Severity | Finding | Resolution |
|---|---|---|
| P1 | Scene lock template omitted contract-required `allowed_deviation`, `evidence`, and `uncertainty` fields | Added all required list fields to every lock and validator coverage for each field |
| P1 | `style_transfer` was routed as generate, allowing preservation constraints to be lost | Classified `edit` and `style_transfer` as image-preserving modes and added positive/negative routing fixtures |
| P1 | Output manifest did not model deterministic text/logo overlays and used untyped null file slots | Added typed records for final, preview, source render, and deterministic overlay files |
| P2 | Edit template used a generic checklist rather than a machine-readable active-lock snapshot | Added exact lock snapshots and `keep_unchanged.from_active_locks` mapping |
| P2 | New runtime contracts and ADRs remained marked `proposed` despite successful owner-review | Marked reference contracts and ADR-0004/ADR-0005 accepted |

Open P0/P1/P2 findings after fixes: **0**.

## Commands

```bash
export PYTHONPYCACHEPREFIX=/tmp/sgp-pycache
python3 -m py_compile scripts/runtime_contract_validation.py scripts/validate_runtime_contracts.py
python3 scripts/validate_runtime_contracts.py
```

## Runtime result

```text
runtime contract checks: 190
result: PASS
validated: analysis schemas, complete locks, safe mode routing, prompt/QA contracts, manifest files, delivery
```

Validator SHA-256:

```text
runtime_contract_validation.py  7e1e9a05485ce35632391193adc7ceb828a6eb2313b1de5b8743bb185abe62c4
validate_runtime_contracts.py    365b55fc33ba48f4b50ab4317e549a85f22d5d4f6f92a5a87467cd8d837fbc65
```

Remote Git blob identities match the locally validated bytes, including:

```text
runtime_contract_validation.py  74c1e7f791ac620c12d5b0539355da2d4a16b993
validate_runtime_contracts.py    69667277d7d64107a0b00aaf9d62b2f193e536b2
scene-brief.yaml                 67f0a9eea88b927e1622406746df751c1e61e361
edit-contract.yaml               77123cb714f3990b46c70aaee37ab378a55e8819
output-manifest.yaml             271ea8779cde6c0026c1cb12120cd1cca9cb366e
```

## Foundation regression review

The foundation validator blob remains unchanged at:

```text
165f4442c3f6ee38981f2cda99079bc356e1d041
```

Its remote input matrix was rechecked for this PR:

- all required foundation paths remain present;
- modified repository paths are ASCII;
- canonical source-of-truth rows remain in `docs/architecture.md`;
- the user-visible final-image requirement remains explicit;
- ADR-0001 through ADR-0003 remain present;
- orchestration Issue #1 remains open in the roadmap;
- style contract, background profiles, source map, and background regression fixture are unchanged from the previously validated main;
- runtime brand-neutrality is covered by the strengthened runtime validator.

The connector-only environment did not provide a network-backed local Git checkout for a second direct invocation of `validate_foundation.py`; the exact checks affected by PR#16 were reproduced against remote files and unchanged blob identities instead. No foundation regression was found.

## Negative mutation tests

All mutations returned non-zero:

1. remove one lock's `evidence`/`uncertainty` fields → FAIL;
2. route valid `style_transfer` fixture through `generate` → FAIL;
3. remove `deterministic_overlay` from manifest files → FAIL.

Representative output:

```text
- semantic_lock uncertainty
- semantic_lock evidence
- valid fixture valid-style-transfer-preserve-route failed: ['mode_mismatch']
- manifest file set
```

## Coverage

- machine-readable reference and conflict entry schemas;
- complete seven-lock schema and mandatory style-lock evidence;
- concern precedence and fidelity limits;
- safe generate-like vs image-preserving mode routing;
- Silver 70-85 / Gold 15-30 and sum 100;
- ten prompt blocks and semantic negative groups;
- active-lock edit snapshots and correction budget;
- 6 valid and 7 invalid runtime fixtures;
- five quality gates, category minimums, and threshold 85;
- nine critical defects and 92/100 smoke scorecard;
- typed manifest file records including deterministic overlays;
- `DELIVERY_MISSING` and blank-response prohibition;
- case-insensitive runtime brand-neutrality.

## Limits

This validation does not generate or inspect image pixels. Perceptual metal allocation, identity, construction, composition, anatomy, target-size readability, and actual user-visible delivery remain manual evidence requirements during end-to-end execution and #7 evaluation.
