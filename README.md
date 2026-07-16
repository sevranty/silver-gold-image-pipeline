# Silver-Gold Image Pipeline

A mono-style reference-to-image Agent Skill that turns one or more available references into a new or edited image through explicit analysis, locks, generator routing, manual visual QA, correction, technical validation, and user-visible delivery.

> This repository defines an orchestration and QA pipeline. It does not bundle an image model, guarantee perceptual quality, or represent an official marketplace publication.

## Quick start

Clone the repository and install the skill into the local Agent Skills directory:

```bash
git clone https://github.com/sevranty/silver-gold-image-pipeline.git
mkdir -p "$HOME/.agents/skills"
cp -R silver-gold-image-pipeline/skills/silver-gold-image-pipeline "$HOME/.agents/skills/"
```

Invoke it with an available reference image:

```text
$silver-gold-image-pipeline
Transform the supplied reference into a controlled Silver-Gold image and complete every QA and delivery stage.
```

The trigger requires an accessible visual reference and a request to generate or edit an image. Analysis-only requests, format conversion, and missing or opaque image targets do not trigger the skill.

## Pipeline

```text
reference -> analysis -> policy -> locks -> scene brief -> adapter -> generation/edit -> full-size QA -> target-size QA -> correction -> technical validation -> user-visible delivery
```

1. Confirm that every required image is available
2. Assign reference roles, priorities, and evidence
3. Resolve safety, rights, text, logo, privacy, and provenance decisions
4. Freeze semantic, identity, object, composition, text, palette, and mandatory Silver-Gold style locks
5. Select a background profile and create a generator-neutral scene brief
6. Route the request through an evidence-backed generator adapter
7. Generate or edit, then inspect manually at full size and target size
8. Correct one diagnosed category at a time within the iteration budget
9. Validate the artifact and output manifest
10. Surface the final image to the user

A successful tool call is not completion. Only a validated, user-visible artifact may end as `DELIVERED`.

## Style DNA

| Contract | Required |
|---|---|
| Silver | 70-85% structural material |
| Gold | 15-30% accent material |
| Surface | matte or satin |
| Geometry | clean, faceted, low-poly |
| Lighting | controlled rim light and dense clean shadows |
| Reflections | minimal reflections, local only |
| Tone | engineered value without jewelry or luxury ornament |

Declared ratios are contract inputs, not pixel-accurate measurements. A human must confirm that Silver visually dominates at full and target size.

## Do and don't

| Do | Don't |
|---|---|
| Preserve explicit subject, identity, object, composition, and text locks | Replace the reference meaning to make the style easier |
| Use Silver as the structural base and Gold as a local signal | Produce a gold-dominant object |
| Keep surfaces matte or satin | Use chrome, mirror, liquid-metal, or glossy surfaces |
| Use clean faceted geometry and controlled negative space | Add noisy texture, scratches, grunge, or baroque ornament |
| Keep a neutral or light product-compatible environment | Drift into black-gold Obsidian-like aesthetics |
| Add exact text and logos as deterministic production overlays | Claim stochastic rendering preserves exact text or logos |

## Supported cases

Supported transformation modes:

- `generate`
- `edit`
- `style_transfer`
- `reinterpretation`
- `composite`
- `sketch_to_render`

Supported references may define subject, identity, geometry, composition, palette constraints, text, and delivery requirements. Multi-reference conflicts are resolved per concern through explicit precedence rather than one global priority.

## Unsupported and blocked cases

The workflow stops or blocks when:

- a required target or reference is missing, inaccessible, invented, or unusable
- permission, identity, text, logo, mask, or provenance evidence is unresolved
- references conflict with a mandatory lock and no safe precedence can preserve it
- material ratios do not sum to 100
- no available generator capability can preserve mandatory constraints
- a policy decision is `block` or `reject`
- a critical quality defect remains
- the artifact cannot be opened or is not visible to the user

The pipeline does not provide automatic pixel-perfect style similarity scoring or automatic perceptual approval.

## Background profiles

- `product-light` is the default for product surfaces and light interfaces
- `showcase-neutral` supports hero and presentation artwork without black-gold dominance
- transparent delivery is a production mode with its own technical checks, not a third visual style

See the [background profile contract](skills/silver-gold-image-pipeline/references/background-profiles.md).

## Runtime contracts

- [Canonical runtime](skills/silver-gold-image-pipeline/SKILL.md)
- [Style contract](skills/silver-gold-image-pipeline/references/style-spec.md)
- [Reference analysis](skills/silver-gold-image-pipeline/references/reference-analysis.md)
- [Safety and rights](skills/silver-gold-image-pipeline/references/safety-and-rights.md)
- [Workflow and locks](skills/silver-gold-image-pipeline/references/workflow-and-locks.md)
- [Prompt patterns](skills/silver-gold-image-pipeline/references/prompt-patterns.md)
- [Generator adapters](skills/silver-gold-image-pipeline/references/generator-adapters.md)
- [Quality gates](skills/silver-gold-image-pipeline/references/quality-gates.md)
- [Output delivery](skills/silver-gold-image-pipeline/references/output-delivery.md)

## Contract examples

The [accepted contract smoke](docs/examples/accepted-contract-smoke.yaml) describes a valid 80/20 Silver-Gold reinterpretation. It explicitly states that no image generator was executed and that production visual quality is not proven.

The [rejected gold-dominance case](docs/examples/rejected-gold-dominance.yaml) stops before delivery because Gold becomes the structural material. Both examples are deterministic contract fixtures, not generated visual evidence.

## Output manifest

Each delivered asset records versions, active locks, runtime capabilities, iterations, QA results, file hashes, dimensions, limitations, and user-visible delivery state.

See the [output manifest template](skills/silver-gold-image-pipeline/assets/templates/output-manifest.yaml).

A valid terminal record must include:

```yaml
quality:
  critical_defects: []
files:
  final:
    required: true
    path: output/final.png
    sha256: null
delivery:
  state: DELIVERED
  user_visible: true
```

`sha256` is populated from the actual produced file. The example remains `null` because this README does not claim a generator run.

## Validation

Install the only Python dependencies required by the current validators:

```bash
python3 -m pip install PyYAML Pillow
```

Run the README contract:

```bash
python3 scripts/validate_readme.py
```

Run every deterministic offline check and unit test:

```bash
python3 scripts/validate_all.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Static checks validate structure, schemas, declared contracts, links, fixtures, manifests, packaging, checksums, provenance, and brand-neutrality. They do not replace manual visual QA.

## Plugin package

Build the deterministic package twice when producing release evidence:

```bash
rm -rf dist-first dist-second
python3 scripts/build_plugin_package.py --out-dir dist-first
python3 scripts/build_plugin_package.py --out-dir dist-second
sha256sum dist-first/silver-gold-image-pipeline-0.1.0.zip
sha256sum dist-second/silver-gold-image-pipeline-0.1.0.zip
```

Validate the package manifest and checksum:

```bash
python3 scripts/validate_plugin_package.py --archive dist-first/silver-gold-image-pipeline-0.1.0.zip --manifest dist-first/silver-gold-image-pipeline-0.1.0.zip.manifest.json --checksum dist-first/silver-gold-image-pipeline-0.1.0.zip.sha256
python3 scripts/test_installation.py
```

Packaging prepares version `0.1.0`; a tag and GitHub Release are separate closure gates.

## Repository structure

```text
.codex-plugin/                         plugin metadata
skills/silver-gold-image-pipeline/    runtime skill, contracts, templates
scripts/                               deterministic validators and packaging tools
tests/                                 positive, negative, workflow, and regression fixtures
docs/                                  architecture, decisions, benchmarks, and evidence
release/                               package and release contracts
```

Repository documentation, tests, source documents, and synthetic visual anchors are not bundled into the runtime ZIP.

## Versioning

The repository versions pipeline, style, background profiles, prompt, QA, manifest, skill, and plugin contracts independently. See [style and contract versioning](docs/style-versioning.md) and the [package contract](release/package-contract.yaml).

## Provenance and license

The public runtime is normalized and brand-neutral. Source documents remain provenance inputs and are not packaged. Synthetic QA anchors are project-generated structural examples and are not presented as model outputs.

- [Source map](docs/source-map.md)
- [License](LICENSE)
- [Notice](NOTICE.md)

## Contributing

Use one scoped Issue, one task branch, intentional commits, one Draft PR, exact-HEAD validation evidence, independent review, and guarded merge. Do not write directly to `main`.

## Digital trace

```text
Issue -> branch -> commits -> Draft PR -> validation evidence -> review decision -> guarded merge
```

Review evidence must identify the exact HEAD. Any later commit invalidates the previous review and requires a complete re-run.

## Known limitations

- Generator capabilities are routed from documented or runtime-detected evidence and may change
- Masks and reference preservation are not assumed to be pixel-exact
- Exact text and logos require deterministic overlays
- Declared material ratios require manual visual confirmation
- Synthetic SVG anchors prove repository structure, not production image quality
- Final delivery still depends on an available image tool and a user-visible attachment channel
