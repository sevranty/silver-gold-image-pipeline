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
reference_entry_schema:
  required_fields:
    - reference_id
    - primary_role
    - secondary_roles
    - priority
    - available
    - source_quality
    - observations
    - identity_critical
    - construction_critical
    - transferable
    - non_transferable
    - limitations
    - uncertainty
    - provenance
  source_quality_range: [0, 4]
  confidence_range: [0, 4]
conflict_entry_schema:
  required_fields:
    - conflict_id
    - concern
    - competing_reference_ids
    - selected_resolution
    - rationale
    - residual_risk
    - stop_generation
  allowed_concerns:
    - subject
    - identity
    - object
    - composition
    - palette
    - environment
    - text
    - mask
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
uncertainty:
  - statement: null
    confidence: 0
provenance:
  contains_text: false
  contains_logo: false
  rights_note: null
```

Each `conflicts` entry follows `conflict_entry_schema` in the YAML front matter. The front matter is the canonical machine-readable template; examples are illustrative and contain no runtime evidence until populated.
