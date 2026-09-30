______________________________________________________________________

## description: "Task list for the nats-client baseline"

# Tasks: A baseline for nats-client

**Input**: Design documents from
`components/nats-client/specs/001-nats-client-baseline/`

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md) — both written in this
branch, per CONTRIBUTING's lifecycle table

**Tests**: none. There is no code. What stands in is nine commands that must
reproduce their figures, an edge verified from both ends, and a reading.

## Why the nine commands are the whole of Phase 2

Two of this baseline's own measurements were wrong on the first run, and neither
was wrong by arithmetic. The documentation page count included a vendored file
under `docs/node_modules/`, and the exported-type count included fourteen
`*TestSuite` types from `_test.go` files — overstating the contract by more than
half, in the direction that reads plausible.

Both were caught by *running* the command rather than by re-reading a number. So
the tasks below re-run every one, and FR-016 states both errors rather than
presenting the corrected figures as though they had been the first ones.

**Nothing lands in the `nats-client` repository.** T011 verifies that.

______________________________________________________________________

## Phase 1: Setup

- [ ] T001 Confirm the measurements are against the commit the specification
  names: `git -C ~/git/osapi-io/nats-client log --oneline -1` must show
  `cfe12f6` or later. A later commit is fine; a figure that has moved is
  recorded as a new measurement with its date rather than worked around.

______________________________________________________________________

## Phase 2: Foundational — the re-measurement

Run from `~/git/osapi-io/nats-client`. Each command comes from FR-013.

- [ ] T002 The Go counts — FR-013:
  `find . -name '*.go' -not -path './.git/*' | wc -l` → `33`, and with
  `-not -name '*_test.go'` → `20`.
- [ ] T003 The package's shape — FR-001 and FR-013:
  `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' | wc -l` →
  `11`.
- [ ] T004 The contract's three counts, **with tests excluded** — FR-010 and
  FR-013. 25 `Client` methods, 9 exported types, 1 exported function. **Run each
  without the exclusion as well** and confirm the exported-type count rises to
  23: that difference is FR-016's second error and it is worth seeing rather
  than trusting.
- [ ] T005 The documentation page count, **with `node_modules` excluded** —
  FR-013 and FR-016:
  `find docs -name '*.md' -not -path '*/node_modules/*' | wc -l` → `8`. Run it
  without the exclusion too and confirm it returns 9. `system`'s 002 recorded 8
  and was right.
- [ ] T006 [P] The remaining counts — FR-013: README lines `62`, runnable
  examples `5`, and one interface in the package.

**Checkpoint**: every figure produced by a command rather than trusted, and both
of FR-016's errors reproduced deliberately so a reader can see what the
exclusion is worth.

______________________________________________________________________

## Phase 3: User Story 1 — a consumer knows what the wrapper gives them (Priority: P1)

- [ ] T007 [US1] Confirm FR-002 states what the wrapper **adds** rather than
  what it exposes, and that FR-007 states what leaks through it. A wrapper
  described by its surface alone has been described as a package rather than as
  a dependency: a consumer depends on `jetstream.Msg` whether or not this
  repository names it.

- [ ] T008 [US1] Confirm the three authentication modes and what each needs are
  stated — FR-011 — since that is the part of the contract a consumer must
  satisfy before anything works.

- [ ] T009 [US1] Run the SC-001 reading. Give somebody who has not opened
  `pkg/client` the specification alone and three questions: what does the
  wrapper add over the upstream library; how does a consumer authenticate; and
  what happens when the connection drops? The third is the one to watch — FR-012
  says the wrapper adds **no** retry policy of its own, and a reader who assumes
  a wrapper implies resilience has been misled. A person is preferred; a fresh
  agent given only `spec.md` is the fallback. **Record what it proves and what
  it does not.**

  **Two of three, and the third was the one this task flagged.** A fresh agent
  given only `spec.md` answered what the wrapper adds (FR-002) and how a
  consumer authenticates (FR-011), both plainly. It could **not** answer what
  happens when the connection drops — and found something worse than an
  omission: this specification's own **acceptance scenario had promised the
  answer was stated**, "rather than left to the upstream library's defaults".
  FR-012 said only what the wrapper does not add, which is the absence of a
  behaviour rather than the behaviour.

  The reading named the trap exactly: a reader taking that scenario at face
  value mistakes "the corpus states this" for "this document states this". **A
  promise in an acceptance scenario is the worst place for an unverified
  claim**, because it reads as the test rather than as the assertion under test.

  Fixed at specs#189. The code was read: the wrapper sets no reconnection
  options and registers no handlers, so the upstream default governs and a
  consumer is not notified — FR-012a. FR-012b records how the omission came to
  exist, and the scenario now says the answer turned out to be exactly what it
  had asserted it was not.

  It also reported the document reads as a checklist with footnote-style prose
  attached to each line rather than as continuous prose, with the
  measure-and-admit-the-error theme as its only throughline. Same judgement
  `osapi-justfiles`' reading returned, and it belongs to `system`'s 002 for the
  same reason.

  **What it proves and what it does not**: that two of three answers are in the
  text. Not that a consuming maintainer would find them, and not that the third
  would have been noticed by anybody who had already read the code.

______________________________________________________________________

## Phase 4: User Story 2 — a breaking change is recognisable before it is made (Priority: P1)

- [ ] T010 [US2] Verify the dependency edge **from both ends** — FR-003:
  `grep -oE "osapi-io/[a-z-]+" go.mod` here, and the same in `osapi/go.mod`.
  This is the habit `osapi-justfiles`' baseline lacked when it listed its
  consumers from one side and missed one. One edge is a small test of it;
  `osapi-orchestrator` has more.
- [ ] T011 [US2] Confirm FR-004 states **when** the break happens, not only that
  it does: osapi pins a pseudo-version commit rather than a tag, so a rename
  lands green here and breaks at the bump. Confirm the pin by reading
  `osapi/go.mod`. Also confirm nothing changed in the inventoried repository —
  `git -C ~/git/osapi-io/nats-client status --porcelain` is empty.

______________________________________________________________________

## Phase 5: User Story 3 — the seven sections read the same as every other baseline (Priority: P2)

- [ ] T012 [US3] Confirm the seven section names are `system`'s 002 FR-001 names
  **verbatim**, and that all seven are present in order — FR-018 and SC-005.
  This unit copied a corrected file rather than re-deriving the names, which is
  the propagation `osapi-justfiles`' FR-021a predicted. Record that inheriting
  worked, because a later baseline will ask.
- [ ] T013 [US3] Confirm the three gaps name both sides and an owner — FR-014
  through FR-016 — and that none is corrected here. FR-016 is this feature's own
  errors, which is the one a reader is most likely to think should have been
  quietly fixed.

______________________________________________________________________

## Phase 6: Verification and archival

- [ ] T014 Run `cd specs && mise exec -- just test` — SC-006.
- [ ] T015 Run `speckit-archive-run specs/001-nats-client-baseline` once this
  branch has merged. This project's memory holds only a constitution, so the run
  **seeds** rather than folds: `spec.md` and `plan.md` are both created and
  every requirement enters under the feature's own IDs.
- [ ] T016 Mark `system`'s 002 as having one more unit done, and leave the rest
  open: `nats-server` is unit 8, `osapi-orchestrator` unit 9 and the largest
  remaining, gohai's amendment unit 10, and two moves after them.

______________________________________________________________________

## Dependencies & Execution Order

- **Phase 2** blocks everything. Until the figures are reproduced, every later
  task compares prose against prose.
- **T004 and T005 must be run twice each** — with and without their exclusion —
  because the point is the difference.
- **Phases 3, 4 and 5** are independent of each other.
- **Phase 6** is last; T015 needs this branch merged.

### What only looks parallel

T009's reading and T007's check both concern FR-002 and FR-007, and the reading
is worth more if it happens **before** the check rather than after: a reader who
has been told what to look for is no longer a reader who has seen nothing else.

## Notes

- No Go code changes. No change of any kind in `nats-client`.
- Stages 1 to 4 are one branch and one pull request here, which is what
  CONTRIBUTING's lifecycle table specifies. The two units before this one split
  them across three pull requests, which cost two extra review cycles and gained
  nothing.
