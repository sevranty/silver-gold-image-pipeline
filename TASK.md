# SGP-025: Record WebFactoryOS orchestration handoff and local ownership boundaries

Issue: #25
Name: `Record WebFactoryOS orchestration handoff and local ownership boundaries`
Status: `conflicts resolved locally; remote verification and publication blocked from this environment`
PR name: `Record WebFactoryOS orchestration handoff and local ownership boundaries (Issue #25)`
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

No merge conflict markers are present in the touched files.

Remote verification, branch push, and GitHub Draft PR creation are blocked in this environment by `CONNECT tunnel failed, response 403`.

The exact external WebFactoryOS WFO#67 registry URL is not present in local SGP state; do not infer it.

The exact external WebFactoryOS WFO#65 naming URL is not present in local SGP state; do not infer it.
# SGP orchestration handoff

```text
PROJECT_ID: SILVER_GOLD_IMAGE_PIPELINE
SHORT_ID: SGP
PROJECT_NAME: silver-gold-image-pipeline
REPOSITORY_URL: https://github.com/sevranty/silver-gold-image-pipeline
TASKS_URL: https://github.com/sevranty/silver-gold-image-pipeline/issues
ORCHESTRATION_SYSTEM: WebFactoryOS
LOCAL_HANDOFF_ISSUE: https://github.com/sevranty/silver-gold-image-pipeline/issues/25
REMOTE_ROUTING_ISSUE: https://github.com/sevranty/web-factory-os/issues/67
NAMING_SOURCE: https://github.com/sevranty/web-factory-os/issues/65
```

## Ownership

| Concern | Owner |
|---|---|
| Skill runtime, references, assets and prompts | SGP repository |
| QA, validators, fixtures and evidence | SGP repository |
| Plugin package, checksums, tags and releases | SGP repository |
| Project registry and route lookup | WebFactoryOS |
| Cross-project task relations and orchestration status | WebFactoryOS |
| Chat-title grammar | WebFactoryOS naming contract |

## Boundary

- WebFactoryOS relations do not grant write access to this repository
- SGP remains independently installable and testable
- Do not copy the WebFactoryOS registry, naming grammar, workflows or implementation into SGP
- Do not add a WebFactoryOS runtime, CI, package or pinned dependency to SGP
- External orchestration does not change local Issue, branch, PR, review or release gates

## Local execution

Every SGP implementation change uses:

```text
Issue -> task branch -> commits -> Draft PR -> exact-HEAD validation -> review -> guarded merge
```

Run local validation from the reviewed HEAD:

```bash
python3 scripts/validate_all.py
```

Release work remains governed by [SGP#26](https://github.com/sevranty/silver-gold-image-pipeline/issues/26) and closes only after the project-level gate in [SGP#1](https://github.com/sevranty/silver-gold-image-pipeline/issues/1).
