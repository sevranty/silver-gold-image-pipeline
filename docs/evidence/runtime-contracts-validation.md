# Runtime contracts validation evidence

Date: 2026-07-15  
Branch: `agent/issues-5-6-runtime-contracts`  
Base: `main@9a82929d09a9f4537a1e537bc4c0884d42c00fcd`  
Initial implementation HEAD: `596a0cf82c0e9ca86dc389c3b5a5f4b79c88b1b3`  
Draft PR: #16  
Scope: #5, #6  
Validation type: local deterministic contract validation  
Network required: no

The final exact PR HEAD must be rechecked during owner-review. This evidence records the complete staged tree, including repository documentation and this report, before the evidence commit is created.

## Commands

```bash
python3 -m py_compile scripts/validate_runtime_contracts.py
python3 scripts/validate_runtime_contracts.py
```

## Result

```text
runtime contract checks: 165
result: PASS
validated: reference analysis, locks, scene/prompt contracts, QA gates, critical defects, delivery
```

Validator SHA-256:

```text
88a85b0ba993c16bf6b5200f59d4b0637f229e4f6d2a5971e1480236abfe8cca
```

Clean validation-output SHA-256:

```text
5bf316a0af8f7b2918f06844c325956cff11c574286ed495e965614f9097f614
```

## Coverage

- 16 required runtime-contract artifacts;
- ASCII repository paths;
- case-insensitive brand-neutral runtime scan;
- YAML front matter for the analysis card;
- seven required locks and mandatory style lock fidelity 4;
- Silver 70-85 / Gold 15-30 and sum 100;
- ten prompt blocks in canonical order;
- required prompt meanings and ten negative semantic groups;
- generate/edit mode separation;
- two targeted corrections and one full restart;
- 6 valid and 6 invalid runtime fixtures;
- five quality gates;
- QA weights total 100 and threshold 85;
- category minimums and filled smoke scorecard at 92/100;
- nine critical defects with accepted/rejected examples;
- manifest versions and explicit delivery state;
- `DELIVERY_MISSING` and blank-response prohibition.

## Negative mutation tests

### Brand leakage

A temporary copy appended lowercase source-brand text to `prompt-patterns.md`.

```text
result: FAIL
- runtime brand leakage: finuslugi
```

### Invalid metal ratio

A temporary copy changed the scene template from 80/20 to 80/25.

```text
result: FAIL
- scene ratio sum
```

### Missing critical defect

A temporary copy removed the `delivery_missing` fixture.

```text
result: FAIL
- critical defect fixture set
```

All three mutation runs returned non-zero. Temporary copies were not committed.

## Limits

This validation does not generate or inspect image pixels. Perceptual metal allocation, identity, construction, composition, anatomy, target-size readability, and actual user-visible delivery remain manual evidence requirements during end-to-end execution and #7 evaluation.
