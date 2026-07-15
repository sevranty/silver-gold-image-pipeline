# Static validation suite evidence

Date: 2026-07-15  
Branch: `agent/issue-11-static-validation-suite`  
Base: `main@50f724f33ef830d832a405c55318969028bd6adf`  
Reviewed implementation HEAD: `0353a7f447e7decefc512fb82a8cf7febb5e7656`  
Draft PR: #20  
Scope: #11  
Validation type: local compile, unit tests, reconstructed offline contract suite, and owner-review

The evidence commit changes only this report. The final exact PR HEAD is rechecked in the PR review submission.

## Owner-review finding resolved

| Severity | Finding | Resolution |
|---|---|---|
| P1 | A regex alternative rejected the valid coordinated negative phrase `no obsidian or black-gold dominance` | Replaced naive token lookbehind with a bounded contextual negation check and added a regression fixture |

Open P0/P1/P2 after fix: **0**.

## Commands

```bash
export PYTHONPYCACHEPREFIX=/mnt/data/sgp_pycache_11
python3 -m py_compile scripts/*.py
python3 -m unittest tests/test_validation.py
python3 scripts/validate_runtime_contracts.py
python3 scripts/validate_policy.py
python3 scripts/validate_skill_runtime.py
python3 scripts/validate_adapters.py
python3 scripts/validate_skill_structure.py . --json
```

The isolated environment could not clone the public branch because outbound DNS was unavailable. The branch was reconstructed from the exact new files plus previously validated runtime trees. `validate_foundation.py` was not re-executed in that reconstruction; its unchanged contour remains part of `validate_all.py` and will be executed in final post-merge validation.

## Result

```text
py_compile: PASS
runtime contract checks: 224 — PASS
policy checks: 170 — PASS
skill runtime checks: 145 — PASS
adapter checks: 235 — PASS
skill structure: PASS
unit tests: 5/5 PASS
```

## CLI contract

- success: exit `0`;
- validation failure: exit `2`;
- invalid CLI usage: non-zero argparse usage exit;
- `--json` returns a machine-readable report;
- every report declares `subjective_visual_quality_assessed: false`.

## Coverage

- repository structure, front matter, ASCII paths, and runtime brand leakage;
- scene schemas, modes, roles, priorities, locks, ratios, profiles, dimensions, and aspect ratios;
- normalized prompt semantic groups and contextual negative-language handling;
- glossy, mirror, chrome, liquid metal, jewelry, baroque, gold-body, grunge, and Obsidian-like contamination;
- manifest IDs, UTC timestamps, versions, provenance, iterations, QA status, limitations, license status, checksums, absolute paths, and secret-like values;
- raster format, dimensions, aspect ratio, alpha, color mode, size, EXIF presence, and openability;
- non-destructive packaging, ASCII filenames, EXIF removal, file hashes, and source/private-document exclusions;
- positive and negative fixtures plus generated temporary raster fixtures.

## Limits

No static script claims subjective Silver-Gold visual quality, perceptual metal allocation, identity fidelity, anatomy, construction quality, or composition fidelity. These remain manual visual QA and #7 regression responsibilities.
