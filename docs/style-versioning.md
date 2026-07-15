# Style and contract versioning

## Independent versions

- `skill_version`: runtime orchestration and trigger behavior;
- `pipeline_core_version`: workflow contract and stage ordering;
- `style_core_version`: Silver-Gold visual invariants;
- `background_profiles_version`: profile selection and delivery behavior;
- `prompt_schema_version`: scene and prompt contract schema;
- `qa_schema_version`: QA scorecard and rejection model;
- `manifest_schema_version`: output evidence manifest;
- `plugin_manifest_version`: distribution metadata schema.

## Current contract versions

```yaml
skill_version: 0.1.0
pipeline_core_version: 0.2.0
style_core_version: 0.1.0
background_profiles_version: 0.1.0
prompt_schema_version: 0.1.0
qa_schema_version: 0.1.0
manifest_schema_version: 0.1.0
plugin_manifest_version: 1.0.0
```

The first repository release is `0.1.0`. Contract versions remain independent from the repository release version.

## SemVer interpretation

### Major

Breaking changes include material ranges or roles, profile IDs/defaults, reference roles or lock semantics, prompt block ordering or required fields, critical rejection rules, runtime stage ordering, delivery terminal-state meaning, plugin ID, canonical skill path, or package layout.

### Minor

Backward-compatible additions include new optional asset subtypes, neutral ranges, optional locks or diagnostics, generator adapters, optional manifest evidence, or additive package metadata.

### Patch

Clarifications that do not change accepted runtime behavior, such as wording, examples, typo corrections, additional evidence, or non-behavioral packaging fixes.

## Change requirements

Every version change requires a linked Issue, decision-log entry when behavior changes, updated source map when provenance changes, validation evidence, and a changelog entry. A release tag is a separate lifecycle action and is never implied by a packaging commit.
