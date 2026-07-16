# Plugin manifest schema repair evidence

## Scope

- Issue: #23 / SGP#14
- Pull request: #24
- Base: `main@6e9b809c208ce9bccbb443e6725fc646efd62000`
- Validated implementation HEAD: `ffede2b7c6021f43dc3bcdce15db5a04ac576cc3`
- Checked: 2026-07-16

## Primary evidence

Current OpenAI plugin guidance and the current `openai/plugins` examples use:

- top-level `name`;
- plugin-root-relative `skills: "./skills/"`;
- optional install-surface `interface` metadata.

The previous internal `id`, top-level `schema_version`, and array `skills` shape is rejected by the repaired validator.

## Exact-byte validation

All seven changed implementation files were reconstructed from immutable GitHub file bytes and verified with `git hash-object` against their remote Git blob SHA values before execution.

Results:

```text
compileall: PASS
source package validation: PASS
plugin package tests: 7/7 PASS
deterministic double build: PASS
archive manifest validation: PASS
checksum validation: PASS
standalone installation smoke: PASS
archive files: 25
installed files: 25
standalone root: skills/silver-gold-image-pipeline
archive SHA-256: b7a525ea9c8664b2510c98d2909bbcbf6885a410c4642c7cf50eb1cb1f2d589e
```

The two independently built ZIP archives were byte-identical.

## Negative mutations

All eight mutations returned validation exit code `2`:

1. legacy `id` field;
2. array `skills` path;
3. non-relative `skills/` path without `./`;
4. brand-specific metadata;
5. missing runtime reference;
6. version mismatch;
7. repository docs inserted into archive;
8. archive bytes changed without matching manifest/checksum.

Result: `8/8 expected failures`.

## Boundary

This repair changes plugin distribution metadata, package validation, standalone installation resolution, fixtures, tests, and changelog only. It does not change Silver-Gold style, prompts, QA, visual evidence, runtime routing, tag, or GitHub Release.

GitHub Checks/statuses were not published and are not claimed.