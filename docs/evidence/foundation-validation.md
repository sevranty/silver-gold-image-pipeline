# Foundation validation evidence

Date: 2026-07-15  
Branch: `agent/issues-1-4-3-foundation`  
Scope: #1, #4, #3  
Validation type: local deterministic foundation validation  
Network required: no

## Command

```bash
python3 scripts/validate_foundation.py
```

## Result

```text
foundation checks: 64
result: PASS
validated: architecture, style contract, background profiles, provenance, regressions
```

## Evidence coverage

- required repository files exist;
- all committed paths are ASCII;
- runtime reference files contain no known source-brand identifiers;
- style contract contains material allocation, surface, geometry, lighting, reflection, and profile invariants;
- background decision defines the default profile, showcase profile, safe areas, transparency behavior, and rejection criteria;
- source map contains SHA-256 hashes for both provenance inputs;
- four background regression cases exist;
- architecture contains a source-of-truth matrix and user-visible final-image requirement;
- no unfinished `TODO`, `TBD`, or placeholder markers are present.

## Limits

This validation does not evaluate generated pixels, perceptual material allocation, reference fidelity, or visual quality. Those checks remain owned by #6, #7, and #11.
