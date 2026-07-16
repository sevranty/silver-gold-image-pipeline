# Roadmap

## Phase A: foundation

- [ ] #1 orchestration remains open; foundation architecture merged through PR #15
- [x] #4 background delivery profiles and ADR merged through PR #15
- [x] #3 canonical Silver-Gold style contract and source map merged through PR #15

## Phase B: runtime contracts

- [x] #5 reference analysis, locks, scene contracts, and prompt pack merged through PR #16
- [x] #6 quality gates and final delivery merged through PR #16
- [x] #10 people, text, logo, and rights policy merged through PR #17
- [x] #2 canonical `SKILL.md` merged through PR #18
- [x] #9 generator capability matrix merged through PR #19

## Phase C: proof

- [x] #11 complete static validation suite merged through PR #20
- [x] #7 trigger, workflow, rejection matrix, and manual visual regression suite merged through PR #21

## Phase D: distribution

- [ ] #8 plugin packaging and release contract implemented in Draft PR #22; exact-HEAD review pending
- [ ] #12 benchmarked production README
- [ ] #13 repository social preview

## Release constraint

The packaging task does not publish a version tag or GitHub Release. Ready transitions and merges require exact-HEAD validation and owner review. Release v0.1.0 is created only after #8, #12, #13, post-merge validation, and project closure #1.
