# Release checklist — v0.1.0

This checklist prepares but does not publish the release.

- [ ] Exact main SHA recorded after all child Issues merge.
- [ ] `python3 scripts/validate_all.py` passes from a clean checkout.
- [ ] `python3 scripts/validate_plugin_package.py --json` passes.
- [ ] `python3 scripts/test_installation.py --json` passes.
- [ ] Trigger, scene, prompt, manifest, package, and regression fixtures pass.
- [ ] One reference-to-image workflow smoke record reaches user-visible delivery.
- [ ] Manual full-size and target-size visual evidence is reviewed.
- [ ] Package archive file list matches `release/package-contract.yaml`.
- [ ] Archive and source-file checksums are generated and verified.
- [ ] Owner review is anchored to the exact release candidate SHA.
- [ ] CHANGELOG and release notes match the release candidate.
- [ ] No source documents, private fixtures, secrets, EXIF, or external brand assets are packaged.
- [ ] Annotated tag `v0.1.0` is created only after the final release decision.
- [ ] GitHub Release is public, non-draft, and non-prerelease only after final validation.
