# Generator adapter validation evidence

Date: 2026-07-15  
Branch: `agent/issue-9-generator-capability-matrix`  
Base: `main@8963cea4e3290bb667d352eb033a022e25b1aa5b`  
Reviewed implementation HEAD: `12cd0e7ddbbf10461e2b75588d745f808be10b9c`  
Draft PR: #19  
Scope: #9  
Validation type: official-source review + local deterministic semantic validation

The evidence commit changes only this report. The final exact PR HEAD is rechecked in the PR review submission.

## Official evidence

Checked on 2026-07-15:

- OpenAI official image-generation guide: generation, edits, multi-turn editing, image inputs, one or more reference images, prompt-guided masks, size/quality/format controls, and model-dependent transparency. The guide explicitly notes imperfect mask-shape precision and no transparent backgrounds for `gpt-image-2`.
- Google official Gemini image-generation guide: Nano Banana model family, text-to-image, text-and-image editing, multiple-image composition, conversational iteration, aspect-ratio and image-size controls, model-specific reference limits, and SynthID behavior.

Profiles remain snapshots. Runtime availability and selected model/version must be verified for every execution.

## Owner-review finding resolved

| Severity | Finding | Resolution |
|---|---|---|
| P1 | Four routing fixtures expected direct `route` despite mandatory capabilities declared `partial` | Changed outcomes to `fallback`, preserving explicit degradation evidence |

Open P0/P1/P2 after fix: **0**.

## Commands

```bash
export PYTHONPYCACHEPREFIX=/mnt/data/sgp_pycache_user
python3 -m py_compile scripts/validate_adapters.py
python3 scripts/validate_adapters.py
```

The public branch could not be cloned directly in the isolated Python runtime because outbound DNS was unavailable. The validator was executed locally against a semantic reconstruction of the exact YAML contracts and fixtures; remote file schemas and Git blob identities were checked through GitHub before review.

## Result

```text
adapter checks: 235
result: PASS
validated: evidence-backed profiles, status matrix, routing, degradations, fallback, stop and delivery boundaries
```

## Negative mutations

All returned non-zero:

1. change a capability status to unknown → FAIL;
2. falsely mark stable seed support as supported → FAIL and invalidates stop fixture;
3. change unsupported exact-mask routing from stop to route → FAIL.

## Coverage

- 14 canonical capabilities;
- `supported`, `partial`, `unsupported` statuses with evidence and limitations;
- OpenAI, Nano Banana 2, and future runtime-detected profiles;
- 10 routing, fallback, deterministic post-processing, and stop cases;
- exact text/logo production boundary;
- mask precision and transparency limitations;
- multi-reference preservation and no silent input loss;
- runtime availability and user-visible delivery requirements;
- eight Silver-Gold-specific manual QA risks.

## Limits

The adapter matrix does not prove that a provider or model is available in a particular runtime and does not claim visual quality. Actual tool presence, model version, provider limits, output behavior, and Gate 4 visual compliance must be recorded per run.
