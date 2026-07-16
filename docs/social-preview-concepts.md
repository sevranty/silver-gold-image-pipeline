# Social preview concepts

## Rubric

| Criterion | Weight |
|---|---:|
| Pipeline meaning at first glance | 30 |
| Small-size readability | 25 |
| Silver-Gold contract fidelity | 20 |
| GitHub crop resilience | 15 |
| Originality and provenance simplicity | 10 |

Each criterion is scored from 0 to its weight. A concept with any critical style defect is rejected regardless of total.

## Concepts

| Concept | Pipeline | Small | Style | Crop | Provenance | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| A. Transparent Gate Pipeline | 29 | 23 | 20 | 15 | 10 | 97 | selected |
| B. Split Before/After | 22 | 24 | 19 | 14 | 10 | 89 | rejected: hides analysis and QA |
| C. Exploded Contract Assembly | 27 | 16 | 20 | 12 | 10 | 85 | rejected: too dense at small size |

## Selected concept

Concept A uses one wireframe reference, three large gates, and one finished faceted object. The path reads left to right:

```text
REFERENCE -> ANALYZE -> LOCKS -> QA -> FINAL ASSET
```

The object is approximately 80% Silver and 20% Gold by declared design allocation. Silver planes carry structure. Gold appears only on two edges, one central signal, and the ratio legend.

## Visual constraints

- 1280 x 640 production canvas
- solid light-neutral background
- no external logo
- no embedded raster or remote SVG reference
- no critical text below 19 px in the 1280 x 640 source
- no chrome, mirror, gloss, jewelry, black-gold, grunge, or rainbow reflection
- safe content frame inside 48 px horizontal and 32 px vertical margins
- original project geometry and text only

## Claim boundary

The source is a deterministic project-created SVG rendered to PNG. It is not an image-generator output and does not prove model visual quality. Manual review covers only the repository-preview asset itself.
