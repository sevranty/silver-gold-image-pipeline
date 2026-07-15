# Safety and rights policy validation evidence

Date: 2026-07-15  
Branch: `agent/issue-10-safety-rights-policy`  
Base: `main@61d1f8021da0606b8a12e05365ef23a67a0a66d4`  
Reviewed implementation HEAD: `0ff1ecc5e0ce603eb2d1b187cdb54df065b9ea9e`  
Draft PR: #17  
Scope: #10  
Validation type: independent owner-review + deterministic local validation

The evidence commit changes only this report. The final exact PR HEAD is rechecked and attested in the PR review submission.

## Owner-review findings resolved

| Severity | Finding | Resolution |
|---|---|---|
| P1 | `request_asset` could be represented as a passing terminal decision | Added explicit `pass` / `block` / `reject` lifecycle and required asset requests to remain blocked |
| P1 | Reference permission and redistribution risk had no dedicated policy category | Added `reference_rights` to the typed decision record, fixtures, matrix, and validator |
| P2 | No positive fixture proved the authorized exact-logo post-processing path | Added an authorized-logo fixture that requires deterministic `post_process` |

Open P0/P1/P2 findings after fixes: **0**.

## Commands

```bash
export PYTHONPYCACHEPREFIX=/tmp/sgp-pycache
python3 -m py_compile scripts/validate_policy.py
python3 scripts/validate_policy.py
```

## Result

```text
policy checks: 170
result: PASS
validated: decision lifecycle, operational actions, people, text/logo separation, reference rights, public fixture hygiene
```

## SHA-256

```text
safety-and-rights.md  fd81772d501f8773278de84f2e4b3ee5ad87338087c6a80a36519dac5f1cd1dd
policy-decision.yaml  d3a452600033776629f1fa468567754319a2bff9a0bd74b443a5af4e965710ea
policy-cases.yaml     c729f8a3235b432c83a8b576fd3d2a353f88fc5e174ee2b586e3f32a9488a63d
validate_policy.py    70fd36cda0f4838945d1ef332f623a9b0ff9216e83857fbc3b3f49fe3d0785ab
```

## Negative mutations

All mutations returned non-zero:

1. set a `request_asset` case to `pass` → FAIL: `passing terminal action`;
2. remove the request/stop action from unresolved `reference_rights` → FAIL: `reference rights`;
3. keep a public fixture eligible after clearing provenance → FAIL: `public eligibility`.

## Coverage

- six operational actions and three decision states;
- user, private adult, public person, child, fictional character, and not-applicable categories;
- identity fidelity constrained by source and capability;
- living tissue remains non-metal by default;
- conservative child stop rules;
- deterministic exact-text and exact-logo layers;
- external style references cannot replace Silver-Gold;
- reference permission and redistribution blocking;
- PII, EXIF, geolocation, confidential-material, and provenance checks;
- 14 accepted, blocked, and rejected cases;
- public runtime brand-neutrality.

## Limits

The policy records available status and runtime decisions; it does not provide a legal opinion or independently verify ownership. Visual safety and fidelity still require end-to-end manual review in #7.
