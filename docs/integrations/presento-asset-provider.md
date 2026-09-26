# Presento asset-provider boundary

## Status

SGP adopts the Presento asset-provider request/result boundary as an optional local integration contract. This does not create a runtime dependency from SGP to Presento and does not transfer generation ownership away from SGP.

Source contract:

- `presento.asset-provider.request.v1` / `1.0.0`
- `presento.asset-provider.result.v1` / `1.0.0`
- https://github.com/sevranty/presento/blob/main/src/assets/providers/contract.py

## SGP provider identity

```json
{
  "schema_version": "1.0.0",
  "provider_id": "silver-gold-image-pipeline",
  "project_id": "SILVER_GOLD_IMAGE_PIPELINE",
  "repository": "https://github.com/sevranty/silver-gold-image-pipeline",
  "mode": "external-local-runtime",
  "capabilities": {
    "asset_kinds": ["raster-image"],
    "materialization": "local-file",
    "requires_external_execution": true
  },
  "invocation": {
    "contract_id": "presento.asset-provider.request.v1",
    "contract_version": "1.0.0",
    "required_fields": ["request_id", "asset_kind", "requirements", "config"]
  },
  "result": {
    "contract_id": "presento.asset-provider.result.v1",
    "contract_version": "1.0.0",
    "required_fields": ["provider_revision", "config_sha256", "checksum", "path"]
  }
}
```

## Request mapping

The integration adapter accepts the versioned Presento request envelope and maps it into the existing SGP pipeline. The adapter must not bypass SGP safety, reference analysis, locks, adapter decision, generation/edit, visual QA, technical validation, or delivery rules.

Required request fields are `request_id`, `provider_id`, `asset_kind`, `prompt_profile`, `requirements`, and `config`. `provider_id` must equal `silver-gold-image-pipeline`; `asset_kind` must be `raster-image`.

## Result mapping

A successful local-file result returns the Presento result fields and must include:

- exact SGP `provider_revision` used for the result;
- SHA-256 of the canonically serialized request `config` as `config_sha256`;
- SHA-256 of the materialized asset bytes as `checksum`;
- local materialized `path`;
- MIME type and dimensions when known;
- machine-readable `diagnostics`.

The result is evidence of a provider invocation only. It does not imply publication, deployment, or acceptance of visual quality outside the normal SGP gates.

## Failure mapping

Failures are machine-readable and must preserve a stable code plus a concise diagnostic message. At minimum the adapter distinguishes unsupported contract version, provider mismatch, unsupported asset kind, unavailable execution capability, invalid output, and failed SGP validation/QA.

No paid call, secret, token, production environment, or Presento runtime is required to validate the contract boundary itself.

## Dependency direction

```text
Presento local integration adapter
-> versioned request
-> SGP-owned execution boundary
-> SGP runtime and QA
-> versioned result + provenance
```

SGP does not import Presento runtime code. Presento does not own SGP generation semantics. Contract compatibility is tested with local fixtures and deterministic validation.