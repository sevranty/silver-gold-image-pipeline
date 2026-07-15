# Canonical skill runtime validation evidence

Date: 2026-07-15  
Branch: `agent/issue-2-canonical-skill-runtime`  
Base: `main@e26bb489ce51fba7303009c80316d4610d7482d6`  
Reviewed implementation HEAD: `2f69fa08fc53d5c2d663862781a0d001448cb398`  
Draft PR: #18  
Scope: #2  
Validation type: independent owner-review + deterministic local validation

The evidence commit changes only this report. The final exact PR HEAD is rechecked and attested in the PR review submission.

## Owner-review result

Open P0/P1/P2 findings: **0**.

Review confirmed:

- YAML front matter has canonical name and precise trigger/non-trigger description;
- runtime body is a short orchestrator rather than a duplicate style/prompt/QA specification;
- every currently implemented contract has a load-map entry;
- six transformation modes are explicit;
- the 14 runtime stages remain ordered;
- missing images and opaque identifiers stop before analysis;
- policy `pass` / `block` / `reject` behavior is explicit;
- edit-like modes require Change / Keep unchanged / May vary / Must not appear;
- correction budget is two targeted corrections plus one full restart;
- successful tool execution without visible output is `DELIVERY_MISSING`;
- presentation metadata does not own runtime behavior.

## Commands

```bash
export PYTHONPYCACHEPREFIX=/tmp/sgp-pycache
python3 -m py_compile scripts/validate_skill_runtime.py
python3 scripts/validate_skill_runtime.py
```

## Result

```text
skill runtime checks: 98
result: PASS
validated: front matter, trigger boundaries, contract map, workflow order, stop/correction/delivery rules, metadata
```

## SHA-256

```text
SKILL.md                  dee039cb758fa41e6f7271fccd97f2530adb62df88f691869577a95e3f5c71a8
agents/openai.yaml        e106e30abd9cd978c5c22d4c3d2c64feae33cba3dd2085a6e63dcb6da1c69b0c
runtime-state.yaml        06b966a641f50385ef7ba3b496f5ddc58854a8227c95df040a174a61beb13b9c
trigger-cases.yaml        e7c9bb1c992522e65b8ff216645b0383d37d94990ccfa7cfaa17d73f5dcc09cd
validate_skill_runtime.py 7e466f91d2435f8476f21d0c05f80e760ae2510a378863a795a0aabbc3dc382a
```

## Negative mutations

All mutations returned non-zero:

1. remove the visible `DELIVERED` completion rule → FAIL;
2. swap the first two workflow stages → FAIL: `workflow order`;
3. remove the missing-image non-trigger case → FAIL on case count, non-trigger count, and coverage.

## Coverage

- 6 trigger cases;
- 8 non-trigger cases;
- image availability and unsupported request boundaries;
- contract map and progressive loading;
- stage ordering and typed runtime state;
- style lock, policy, QA, correction, manifest, and delivery boundaries;
- ASCII paths and runtime brand-neutrality.

## Limits

This validator checks the declarative runtime contract and fixtures. Actual trigger selection and end-to-end image behavior are evaluated in #7; generator capabilities and fallbacks are owned by #9.
