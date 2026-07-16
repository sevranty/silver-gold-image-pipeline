# README benchmark

Checked: 2026-07-16

Primary documentation and repositories were reviewed at exact refs. The benchmark extracts documentation patterns only; no source wording, identity, or third-party visual assets are reused.

## Sources and decisions

| Source | Exact ref | Useful pattern | Applied to SGP | Limitation |
|---|---|---|---|---|
| OpenAI Build skills | https://developers.openai.com/codex/skills/create-skill | `SKILL.md`, discovery metadata, progressive disclosure | separate short discovery metadata from detailed runtime contracts | platform guide, not a visual QA specification |
| OpenAI Build plugins | https://developers.openai.com/codex/plugins/build | required manifest, plugin-root-relative component paths | current `name`, `skills: "./skills/"`, explicit local/package boundaries | SGP is not yet an official marketplace entry |
| `openai/plugins` | `11c74d6ba24d3a6d48f54a194cd00ef3beea18f9` | package identity, components, publisher and install-surface metadata | restrained manifest with author, license, keywords and starter prompt | connector/app fields are out of scope |
| `openai/skills` | `49f948faa9258a0c61caceaf225e179651397431` | deprecation notice and migration to plugins | deprecated repository is not treated as the current distribution source | historical install examples only |
| `anthropics/skills` | `9d2f1ae187231d8199c64b5b762e1bdf2244733d` | self-contained skills, minimal frontmatter, examples, license distinctions, disclaimer | separate runtime, examples, fixture status and limitations | Claude install commands are not reused |
| `huggingface/diffusers` | `612036aa14e416902fc38c3f3ef30fe8357acf7f` | concise purpose, isolated installation, runnable quickstart, task map | purpose and pipeline precede complete setup and validation commands | SGP does not bundle a model runtime |
| `Comfy-Org/ComfyUI` | `03978e1e81475f19eebd7edc065cc55cb4e15e10` | workflow-first framing, saved workflows, capability catalog, stability notes | intermediate contracts and manifests are explained as workflow artifacts | SGP is an orchestration skill, not an execution engine |
| `openai/openai-cookbook` | `20793784ac467f06ed67f3e3e9349dc9596894e0` | generation/edit separation and image-evaluation harnesses | separate modes, adapters, preflight, visual QA and deterministic contract smoke | API-specific runtime code is not copied |
| `sevranty/modern-flat-image-pipeline` | `1ef9f8f3d9ed4544b22e8e697c695a576f36648e` | family naming, ordered pipeline, invocation, capability boundaries and validation | family consistency with an independent Silver-Gold contract | visual and prompt rules are different |
| `sevranty/obsidian-gold-image-pipeline` | `25348669684b5bcf6b0aa8c3c79f466e94e63a42` | mono-style repository separation and release trace | consistent project lifecycle and package evidence | checked README is too small to guide production documentation |

## Selected patterns

1. Explain the problem before listing files.
2. Show the ordered reference-to-image pipeline before generator capabilities.
3. Give complete commands with the real repository URL and no placeholders.
4. Separate local skill discovery, deterministic package build, and marketplace publication.
5. State what references preserve, what changes, and what triggers rejection.
6. Make manual visual QA and user-visible delivery explicit completion gates.
7. Include one accepted deterministic contract smoke and one rejected contract case.
8. Separate runtime package, repository evidence, and synthetic visual fixtures.
9. Pin repository sources to exact commits.
10. Do not infer unavailable generator capabilities.

## Rejected patterns

- decorative claims without a runnable workflow;
- one opaque prompt presented as source of truth;
- model support claims without runtime capability evidence;
- commands copied from another host platform;
- unlicensed screenshots or third-party visual assets;
- synthetic anchors described as production generator outputs;
- badges implying CI, release, or marketplace status without evidence.
