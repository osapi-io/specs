______________________________________________________________________

## description: "Task list for the osapi-orchestrator baseline"

# Tasks: A baseline for osapi-orchestrator

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), both in this branch

**Tests**: none. Fourteen commands, one reconciliation loop run in both
directions, and a reading.

## What is different about this one

It is the last of the six, and the first written after memory became
documentation. So T015 writes prose under seven headings rather than archiving a
requirements list, and `just test` now runs `memory-check` over the result.

Every command in a measurement table must stand alone. `memory-check` runs each
one in isolation and cannot resolve "the same, plus X" against the row above,
and six counts in earlier memories had to be rewritten for exactly that.

**Nothing lands in the `osapi-orchestrator` repository.** T012 verifies it.

______________________________________________________________________

## Phase 1: Setup

- [ ] T001 Confirm the commit:
  `git -C ~/git/osapi-io/osapi-orchestrator log --oneline -1` shows `727ab40` or
  later.

## Phase 2: The counts

Run from `~/git/osapi-io/osapi-orchestrator`.

- [ ] T002 Go counts: 81 files, 59 excluding tests.
- [ ] T003 The package's surface, tests excluded: 12 non-test files, 16 exported
  functions, 13 exported types, 127 exported methods, **0 interfaces**.
- [ ] T004 The operation count, **and the wrong way to take it**. Confirm
  `grep -cE '^func \(o \*Orchestrator\) [A-Z]' pkg/orchestrator/ops.go` returns
  101, and confirm that adding `.*\) \*Step \{$` to that pattern returns **2**
  because signatures span lines. Both results matter: the second is what a
  plausible-looking command produces.
- [ ] T005 [P] Documentation counts: 140 pages, 101 operation pages, 24
  directory indexes, 14 feature pages, 41 examples, 119 README lines.

## Phase 3: User Story 1 — what the orchestrator is for (Priority: P1)

- [ ] T006 [US1] Confirm FR-002 names the four things it adds rather than what
  it exposes. A layer over an existing SDK is described by what it adds.
- [ ] T007 [US1] Confirm FR-008 states both kinds of conditional and the
  difference. Guards ask what earlier work did; predicates ask what a host is. A
  reader who conflates them will write `OnlyIfChanged` expecting `When`.
- [ ] T008 [US1] Run the SC-001 reading. Three questions from the corpus alone:
  what is a `Step`, name three ways to make one conditional, and what does `Run`
  do? **Record what it proves and what it does not.**

## Phase 4: User Story 2 — how deeply the SDK reaches (Priority: P1)

- [ ] T009 [US2] Confirm the four files in `internal/engine` that import
  `osapi/pkg/sdk/client`, by name, and that FR-014 says the package name
  describes visibility rather than independence.
- [ ] T010 [US2] Confirm `pkg/orchestrator` declares zero interfaces, and that
  FR-015 connects that to FR-014: no seam means nothing could be substituted
  even if somebody wanted to.
- [ ] T011 [US2] Verify the single edge from both ends, `go.mod` here and the
  absence of this module in every other `go.mod`.
- [ ] T012 Confirm `git -C ~/git/osapi-io/osapi-orchestrator status --porcelain`
  is empty.

## Phase 5: User Story 3 — the documentation reconciles (Priority: P2)

- [ ] T013 [US3] Run the reconciliation **in both directions**. For every one of
  the 101 operation pages, take its `H1` and grep `ops.go` for that method. Then
  for every one of the 101 methods, grep the pages for an `H1` matching it.
  Expect zero orphans each way. **Comparing the two totals is not this check**:
  101 against 101 says nothing about whether they are the same 101.
- [ ] T014 [US3] Confirm FR-018 records that nothing enforces the mapping. The
  repository with the best documentation coverage in the organization has no
  gate behind it, and that is worth stating precisely because it reads as a
  strength.

## Phase 6: Verification and archival

- [ ] T015 Run `cd specs && mise exec -- just test`, `memory-check` included.
- [ ] T016 Archive once this branch has merged. Memory holds only a
  constitution, so the run **seeds**. Write it as documentation under seven
  headings, per `global/baseline`, and run `unslop` over it before committing.
  Every command in the measurement table must stand alone.
- [ ] T017 Mark `system`'s 002 as having all six components baselined, which
  makes its SC-001 answerable for the first time: whether a reader who has read
  none of them can read all six and state what each repository is for. Record
  that it is now answerable, not that it passed.

______________________________________________________________________

## Dependencies & Execution Order

- **Phase 2** blocks everything.
- **T004 must be run both ways.** The point is the difference between 101 and 2.
- **T013** is independent of the other phases and is the longest-running task.
- **Phase 6** last; T016 needs this branch merged.

## Notes

- No Go code changes. No change of any kind in `osapi-orchestrator`.
- All three gaps imply a change that repository must make, and naming a change
  is not making it.
