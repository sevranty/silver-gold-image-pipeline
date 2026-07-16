# Roadmap

## Phase A: foundation

- [ ] #1 orchestration remains open until final release verification
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

- [x] #8 plugin packaging and release contract merged through PR #22
- [x] #23 current plugin-manifest schema repair merged through PR #24
- [x] #12 benchmarked production README and validation merged through PR #27
- [ ] #13 repository social preview, Settings publication and public-card proof

## Orchestration handoff

- [x] #25 local WebFactoryOS ownership and routing handoff merged through PR #28
- [ ] #30 post-merge foundation marker compatibility repair
- WebFactoryOS owns external registration and route lookup only
- SGP owns implementation, package, QA, assets, validation and releases
- External relations grant no write access and add no runtime or CI dependency

## Release constraint

No tag or GitHub Release is created until #13 and #30 are complete, exact-main post-merge validation passes, package bytes and checksum are rebuilt from the final main SHA, and project closure #1 is verified. The final sequence is tracked by #26.
