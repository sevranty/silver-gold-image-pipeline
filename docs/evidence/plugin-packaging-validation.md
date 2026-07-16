# Plugin packaging validation evidence

## Scope

- Issue: #8
- Pull request: #22
- Base: `main@2d312e5f1b680bcc8e811a09ab92759d4ecaaa91`
- Validated implementation HEAD: `4c1f58e31bb00f40591b464503ed47b91edba84c`
- Package version: `0.1.0`
- Plugin manifest schema: `1.0.0`

## Exact-byte reconstruction

The container could not resolve GitHub through normal DNS and the repository did not publish GitHub Actions runs. The affected packaging tree was therefore reconstructed from GitHub file responses at the immutable implementation HEAD. Every reconstructed file used by the builder, validator, installation smoke, and package tests was checked with `git hash-object` against its remote Git blob SHA before execution.

This evidence does not claim that GitHub Checks passed. No GitHub Checks/statuses were published for the validated HEAD.

## Validation

Commands executed against the reconstructed implementation tree:

```text
python3 -m compileall -q scripts tests
python3 scripts/validate_plugin_package.py --root . --json
python3 -m unittest -v tests/test_plugin_package.py
python3 scripts/build_plugin_package.py --root . --out-dir /mnt/data/sgp8-final-first --json
python3 scripts/build_plugin_package.py --root . --out-dir /mnt/data/sgp8-final-second --json
python3 scripts/validate_plugin_package.py --root . --archive <archive> --manifest <manifest> --checksum <checksum> --json
python3 scripts/test_installation.py --root . --json
```

Results:

```text
compileall: PASS
source package validation: PASS
plugin package unit tests: 6/6 PASS
deterministic double build: PASS
archive manifest validation: PASS
checksum validation: PASS
standalone installation smoke: PASS
archive files: 25
installed files: 25
archive SHA-256: 4a1e7f4c222e3e4095fb6a5768514f9862770fef9cc929c45ce801623c220fc3
```

The two independently built archives were byte-identical.

## Negative mutations

All seven required mutations returned exit code `2`:

1. wrong plugin ID;
2. more than one skill path;
3. brand-specific agent metadata;
4. missing required runtime reference;
5. cross-file version mismatch;
6. repository documentation injected into the archive;
7. archive bytes changed without matching manifest/checksum.

Result: `7/7 expected failures`.

## Package boundary

The archive contains only:

- `.codex-plugin/plugin.json`;
- `LICENSE`, `NOTICE.md`, and `CHANGELOG.md`;
- the canonical `SKILL.md`;
- `agents/openai.yaml`;
- runtime templates;
- runtime reference contracts.

The archive excludes repository docs, tests, release planning, source documents, visual anchors, visual regression examples, caches, and compiled Python files. Installed `SKILL.md` reference links were resolved inside the unpacked standalone package.

## Review findings resolved

- P1: dynamic module imports could fail in a clean unittest process;
- P1: archive validation did not verify generated manifest and checksum together;
- P1: package builder duplicated include/exclude logic instead of deriving the file set from the package contract;
- P2: README and roadmap still described packaging and PR #21 as pending;
- P2: an unexecuted workflow could be mistaken for CI evidence.

All findings were corrected before this evidence was recorded. The unexecuted workflow was removed. No tag or GitHub Release is created by Issue #8.

## Limitation

The complete historical `validate_all.py` suite was not re-executed from a network clone because neither container GitHub access nor GitHub Actions execution was available. Non-packaging runtime and visual contracts were not modified by this task except the corrected `style_core_version`, `qa_schema_version`, and malformed ratio keys in the visual regression case file. Those changed version fields were included in package validation. Previous merged exact-HEAD evidence remains the source for unchanged foundation, runtime, policy, adapter, static-validation, and manual-visual contours.
