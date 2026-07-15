# Visual regression validation evidence

Issue: #7  
PR: #21  
Base: `main@189bda944756d134cc7d19fa1fdc1c43f27a4436`  
Branch: `agent/issue-7-visual-regression-suite`

## Validated counts

- trigger cases: 30 — 10 positive, 10 negative, 10 boundary;
- workflow cases: 24;
- deterministic synthetic SVG QA anchors: 13;
- manual full-size review records: 13;
- manual 64px review records: 13;
- mandatory rejection examples: 11;
- coverage categories: 13;
- outcome classes: accepted, rejected, ambiguous;
- regression unit tests: 4/4 PASS.

## Deterministic results

```text
regression suite: PASS
visual evidence: PASS
reproducibility snapshot: PASS
subjective_visual_quality_assessed by static validator: false
production_visual_quality_claimed by manual review: false
```

Negative mutations returned non-zero for insufficient trigger coverage, changed anchor bytes, an incorrect generator-output claim, and a changed manual-review hash.

## Manual visual review

Exact SVG bytes were rendered and inspected at native 1024px and target 64px:

- 6 accepted anchors: structural intent remained readable at both sizes;
- 5 rejected anchors: the expected critical defect remained visible at both sizes;
- 2 ambiguous anchors: weak rim light and borderline visible metal allocation remain owner decisions and were not promoted to accepted.

Known limitations are recorded per case in `docs/evidence/visual-manual-review.json`. Small labels in the edit anchor are explanatory, not production copy. Exact text/logo typography must be sized for the real target surface.

## Review findings fixed before final review

- P1: strengthened the gold-dominance rejection anchor;
- P1: strengthened the black-gold alternate-style rejection anchor;
- P1: replaced malformed provenance transfer with valid UTF-8;
- P1: corrected two reproducibility paths;
- P1: added the complete 11-item rejection matrix required by Issue #7;
- P1: added per-anchor full-size and 64px manual review records;
- P2: expanded external-brand scanning to visual manifests and rubric files;
- P2: exposed visual evidence and validation entry points in README.

## Boundary

The SVG anchors are original project-generated structural QA snapshots. They are not outputs from an image generator and do not prove production visual quality or generator reproducibility. Static validation does not assess subjective quality or exact perceived metal allocation. Production assets still require a separate manual review.

The exact reviewed HEAD is recorded in the PR review after this evidence commit. Any later HEAD invalidates the review and requires a complete rerun.
