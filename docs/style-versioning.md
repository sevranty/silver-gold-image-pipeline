# Style and contract versioning

## Independent versions

The project versions these contracts independently:

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
pipeline_core_version: 0.2.0
style_core_version: 0.1.0
background_profiles_version: 0.1.0
prompt_schema_version: 0.1.0
qa_schema_version: 0.1.0
manifest_schema_version: 0.1.0
```

`skill_version` begins with #2. `plugin_manifest_version` begins with #8.

## SemVer interpretation

### Major

A breaking change to:

- numeric material ranges;
- required material role;
- profile IDs or their default-selection behavior;
- reference-role or lock semantics;
- prompt block order or required machine-readable fields;
- critical rejection criteria or pass thresholds;
- runtime stage ordering;
- delivery terminal-state meaning.

### Minor

A backward-compatible addition such as:

- a new asset subtype;
- an additional allowed neutral range;
- a new optional lock or QA diagnostic;
- a new generator adapter;
- an optional manifest evidence field.

### Patch

A clarification that does not change accepted output behavior, such as wording, examples, typo correction, or additional evidence.

## Change requirements

Every version change requires:

1. linked Issue;
2. decision-log entry when behavior changes;
3. updated source map when provenance changes;
4. validation evidence;
5. changelog entry after packaging is implemented.
