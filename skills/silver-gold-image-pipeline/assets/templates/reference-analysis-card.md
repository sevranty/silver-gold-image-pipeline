---
schema_version: 1.0.0
contract_version: 0.1.0
template_id: silver-gold-reference-analysis-card
analysis_status: incomplete
reference_set_id: null
references: []
conflicts: []
set_level:
  primary_subject: null
  intended_action: null
  intended_environment: null
  identity_owner_reference_id: null
  construction_owner_reference_id: null
  composition_owner_reference_id: null
  exact_text_required: false
  logo_asset_required: false
  unresolved_stop_conditions: []
---

# Reference analysis card

Each `references` entry uses this machine-readable shape:

```yaml
reference_id: ref-001
primary_role: subject_reference
secondary_roles: []
priority: 50
available: true
source_quality: 3
observations:
  subject: null
  action: null
  environment: null
  composition: null
  camera: null
  lighting: null
identity_critical: []
construction_critical: []
transferable: []
non_transferable: []
limitations:
  crop: null
  occlusion: null
  blur: null
  compression: null
  resolution: null
uncertainty: []
provenance:
  contains_text: false
  contains_logo: false
  rights_note: null
```

The YAML front matter is the canonical machine-readable document. The example defines entry shape and contains no runtime evidence until populated.
