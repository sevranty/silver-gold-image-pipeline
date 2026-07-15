# Visual regression validation evidence

Issue: #7
Base: main@189bda944756d134cc7d19fa1fdc1c43f27a4436
Branch: agent/issue-7-visual-regression-suite

Validated counts:
- trigger cases: 30 (10 positive, 10 negative, 10 boundary)
- workflow cases: 24
- deterministic SVG QA anchors: 13
- coverage categories: 13
- outcome classes: accepted, rejected, ambiguous
- unit tests: 4/4 PASS

Negative mutations returned non-zero for insufficient trigger coverage, changed anchor bytes, and an incorrect source claim.

Review findings fixed before evidence:
- strengthened two rejection anchors;
- restored valid UTF-8 provenance;
- corrected two manifest paths;
- expanded external-brand scanning.

The SVG anchors are original project-generated structural QA snapshots. They are not outputs from an image generator and do not prove production visual quality. Static validation does not assess subjective quality or exact perceived metal allocation. Full-size and target-size manual review remain mandatory.

The exact reviewed HEAD is recorded in the PR after this evidence commit. Any later HEAD invalidates the review.
