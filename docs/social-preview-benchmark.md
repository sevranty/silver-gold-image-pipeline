# Repository social preview benchmark

Checked: 2026-07-16

## Official GitHub contract

Primary source:

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview

Verified requirements:

- accepted formats: PNG, JPG, GIF
- file size: under 1 MB
- minimum recommended size: 640 x 320
- best-display size: 1280 x 640
- upload route: repository Settings -> Social preview -> Edit -> Upload an image
- transparent PNG is supported, but GitHub recommends a solid background when cross-platform rendering is uncertain

SGP decision: use a solid-background, original 1280 x 640 RGB PNG below 1 MB. Repository merge does not prove that the Settings image is published.

## Comparative sample

The sample records public repository-card and repository-hero patterns only. No image, logo, wording, or identity is copied.

| Repository | Category | Composition pattern | Hierarchy/readability | Weakness | SGP use |
|---|---|---|---|---|---|
| https://github.com/openai/plugins | plugin platform | system identity plus restrained developer-tool framing | short name and one focal message | platform breadth can hide one workflow | keep one pipeline and one object |
| https://github.com/anthropics/skills | Agent Skills | repository identity with modular-skill framing | strong category recognition | weak transformation narrative | show stages instead of a skill collection |
| https://github.com/openai/openai-cookbook | examples | clear title with technical context | recognizable at small size | example-library density | avoid a grid of unrelated features |
| https://github.com/huggingface/diffusers | image pipeline | model/pipeline identity and visual output association | category reads quickly | can imply bundled model execution | state pipeline without model claims |
| https://github.com/Comfy-Org/ComfyUI | node workflow | connected workflow metaphor | graph structure explains process | nodes become noisy in a small card | limit SGP to three gates |
| https://github.com/invoke-ai/InvokeAI | image tooling | finished image plus product identity | visually expressive | output art can dominate workflow meaning | use an engineered object, not decorative art |
| https://github.com/AUTOMATIC1111/stable-diffusion-webui | image UI | recognizable tool/category framing | immediate category signal | UI screenshots crop poorly | no screenshot in SGP preview |
| https://github.com/langchain-ai/langchain | developer framework | compact brand mark and framework identity | readable at small size | abstract identity does not explain flow | combine title with explicit stage arrow |
| https://github.com/microsoft/semantic-kernel | orchestration | system identity with modular architecture | professional and controlled | broad architecture may feel generic | use one concrete reference-to-asset route |
| https://github.com/vercel/ai | SDK | high-contrast title and restrained graphic system | excellent small-size hierarchy | minimal graphic may not explain transformation | retain large title but show object evolution |
| https://github.com/ollama/ollama | developer tool | single memorable object/identity | highly recognizable | object alone does not show pipeline | final object must remain secondary to gates |
| https://github.com/sevranty/modern-flat-image-pipeline | mono-style pipeline | family naming and controlled style identity | supports repository-family recognition | another style cannot define Silver-Gold rules | reuse only family-level clarity and asset discipline |

## Selected patterns

1. Large project name in the first reading zone
2. One horizontal left-to-right transformation
3. Three process gates maximum
4. One final engineered object
5. Large labels only; no small critical copy
6. Solid neutral background
7. Silver structure as the dominant visual mass
8. Gold used only for two edges, one node, and the ratio marker
9. No screenshots, third-party logos, external artwork, or platform chrome
10. Proofs for full, crop, small, light, and dark surroundings

## Rejected patterns

- black-and-gold luxury composition
- chrome or mirror object
- generic gold object without workflow
- UI screenshot
- dense node graph
- tiny technical annotations
- logos from benchmarked repositories
- transparent background without cross-background proof
