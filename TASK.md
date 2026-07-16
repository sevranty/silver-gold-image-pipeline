# SGP-025 WebFactoryOS local handoff

Issue: #25
Branch: `orchestration/sgp-25-webfactoryos-migration`
Base: `main@23cc79258b58b3b164362dc5414677437a9f8f1a`

## Scope

SGP records only the local ownership boundary needed for WebFactoryOS orchestration.

SGP owns skill code, runtime package, QA contracts, assets, validation, and releases in this repository.

WebFactoryOS owns external registry, routing status, and cross-project relation records outside this repository.

External WebFactoryOS relations grant no write access to SGP files, settings, releases, or runtime behavior.

SGP has no WebFactoryOS runtime, CI, package, grammar, workflow, or registry dependency.

Do not copy WebFactoryOS registry records, grammar, workflows, code, or dependencies into SGP.

## Routing links

SGP debt ledger: https://github.com/sevranty/silver-gold-image-pipeline/issues/26

SGP parent closure: https://github.com/sevranty/silver-gold-image-pipeline/issues/1

Reference source: https://github.com/JuliusBrussee/caveman

## Review blockers

Remote verification, branch push, and GitHub Draft PR creation are blocked in this environment by `CONNECT tunnel failed, response 403`.

The exact external WebFactoryOS WFO#67 registry URL is not present in local SGP state; do not infer it.

The exact external WebFactoryOS WFO#65 naming URL is not present in local SGP state; do not infer it.
