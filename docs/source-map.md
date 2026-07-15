# Source map

Status: accepted foundation  
Related issue: #3

## 1. Provenance inputs

### Primary style source

- file (exact display name): `FDS [visual-style] Стиль Silver-Gold v3.1 (2026-02-24).docx`
- source version: 3.1
- source date: 2026-02-24
- SHA-256: `9ba60cb1454efd657f8457f74b930c538eeba49637aa03d14984ffd8ff3961e4`
- role: primary visual-rule provenance

### Architecture cross-check source

- file (NFC-normalized display name): `FDS [visual-architecture] Архитектура визуальных стилей Финуслуг v2 (август 2025).docx`
- source version: 2
- normalized update date: 2026-02-24
- SHA-256: `8bfc102c9f52597a5696f4717d37add41057caa79f047401134e799d5dde589b`
- role: cross-check for product-surface compatibility and background conflict

The source files are not committed to this repository and are not included in the runtime package.

### Filename normalization

The architecture source filename may be stored by a filesystem with decomposed Unicode characters. Filename verification compares Unicode NFC-normalized names, while SHA-256 remains the byte-level identity check.

Independent source-byte verification command used by owner review:

```bash
python3 scripts/validate_foundation.py \
  --style-source "/mnt/data/FDS [visual-style] Стиль Silver-Gold v3.1 (2026-02-24).docx" \
  --architecture-source "/mnt/data/FDS [visual-architecture] Архитектура визуальных стилей Финуслуг v2 (август 2025).docx"
```

## 2. Mapping rules

| Source section | Source rule | Runtime treatment | Destination |
|---|---|---|---|
| Summary, 2.3 | Silver 70-85%, Gold 15-30% | preserved as declared material allocation | `style-spec.md` sections 2 and 12 |
| 2.1 | low-poly forms, clear edges, symmetry, digital plasticity | normalized into generator-neutral geometry rules | `style-spec.md` section 3 |
| 2.2 | matte or satin surfaces | preserved; expanded with critical reflection rejection | `style-spec.md` section 4 |
| 2.2 | minimal reflections, no mirror gloss | preserved; clarified as local form highlight only | `style-spec.md` sections 4 and 5 |
| 2.2 | controlled rim light and clean dense shadows | preserved and made testable | `style-spec.md` section 5 |
| 3 | stability, reliability, individual value | normalized to restrained engineered emotional tone | `style-spec.md` section 7 |
| 5, 6.1 | central object, dark or neutral background, negative space | split into asset composition rules and background ADR | `style-spec.md` section 6; `background-profiles.md` |
| 6.2 | silver body, gold boundaries and attention points | preserved as material-role contract | `style-spec.md` section 2 |
| 6.3 | no mirror gloss, excess reflections, jewelry overload, gradient kitsch, gold overload | preserved and expanded as critical rejection criteria | `style-spec.md` sections 4 and 10 |
| 6.4 | soft rim light, clean bevels, restrained volume | preserved as allowed implementation behavior | `style-spec.md` sections 3 and 5 |
| 7 | base generation formula | decomposed into style invariants; full prompt ownership deferred to #5 | `style-spec.md`; future `prompt-patterns.md` |
| 8 | design review for expanded gold use | converted from organization governance to contract rejection outside 15-30 | `style-spec.md` sections 2 and 10 |
| 9.4 | web allowed, mobile limited, Storybook required | excluded from universal runtime as organization-specific platform governance | this source map only |
| Visual architecture catalog | Silver-Gold positioned for light-theme product use | resolved with `product-light` as default | `background-profiles.md`; ADR-0002 |
| Style guide composition | dark or neutral background allowed | retained through explicit `showcase-neutral` profile | `background-profiles.md`; ADR-0002 |

## 3. Conscious exclusions

The following source content is not copied into runtime:

- organization and product names;
- internal design-system names and artifact IDs;
- owner and co-owner names;
- RACI and internal review roles;
- product-area coverage and platform governance;
- fixed brand palette;
- internal Storybook requirements;
- claims about premium financial products as the only valid use case;
- the phrase `premium fintech aesthetic` as a mandatory prompt marker.

Reason: these rules describe one operating environment, not the reusable visual style.

## 4. Normalization decisions

### Background conflict

The primary style source allows dark or neutral backgrounds. The architecture source positions Silver-Gold for light-theme product integration.

Resolution:

- one style;
- `product-light` default;
- `showcase-neutral` explicit;
- pure black rejected;
- no style selector.

### Material allocation

The source defines numeric ranges but not an automatic measurement method.

Resolution:

- scene contracts must declare ratios;
- static validation checks ranges and total;
- manual visual QA confirms perceptual dominance;
- no pixel-perfect automated claim in the foundation.

### Reflection language

The source prompt guidance warns against `glossy` and `reflective` while also using `minimal reflections`.

Resolution:

- the contract allows minimal local highlights that explain form;
- mirror, chrome, environment reflection, and broad glare remain critical defects;
- future prompt validation must understand negative context instead of using naive substring rejection.

## 5. Traceability policy

When a source-derived rule changes:

1. update the destination contract;
2. update this mapping;
3. record an ADR when output behavior changes;
4. increment the relevant contract version;
5. attach validation evidence to the Draft PR.
