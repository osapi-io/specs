______________________________________________________________________

## description: "Task list for the osapi-justfiles baseline"

# Tasks: A baseline for osapi-justfiles

**Input**: Design documents from
`components/osapi-justfiles/specs/001-justfiles-baseline/`

**Prerequisites**: [spec.md](spec.md) merged (specs#178) and amended
(specs#179), [plan.md](plan.md)

**Tests**: none, and this is the one place a baseline differs from every other
feature. There is no code, and the gate that matters is not `just test` — it is
whether each command in FR-016 still produces the figure beside it. A formatting
gate cannot tell a right count from a wrong one, so the re-measurement *is* the
test suite and it is Phase 2.

## Why this list exists at all

[gohai's baseline](../../../gohai/specs/001-gohai-baseline/plan.md) archived
with a specification and a plan and no task list, and nothing was obviously
lost. This one has a task list because of what the plan found: a caveat about
the contract's completeness turned out to be a one-command check, and it was
only tested because writing it down made it look testable. A baseline whose
counts are never re-run is a baseline nobody checked, and the difference between
those two is a list.

**Nothing lands in the `osapi-justfiles` repository.** No task below edits it,
and T012 verifies that.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Confirm the specification and its amendment are both on `main` before
  re-measuring anything: `git -C specs log --oneline -3` must show specs#179
  above specs#178. Measuring against an unamended specification would re-find
  FR-011a as though it were new, which is how a correction gets recorded twice.

______________________________________________________________________

## Phase 2: Foundational — the re-measurement

**This phase is the verification.** Every command below comes from FR-016 or
from the requirement it supports, and each must produce the figure the
specification states. A figure that has moved is recorded as a new measurement
with its date, **not** worked around — that is 002's FR-007 applied to this
feature's own artifacts.

Run from `~/git/osapi-io/osapi-justfiles` at `e765614` or later. Where a later
commit gives a different figure, the specification is amended in its own change
before this list is completed.

- [x] T002 Zero Go files — FR-001:
  `find . -name '*.go' -not -path './.git/*' | wc -l` → `0`. This is the
  measurement the whole unit rests on: it is why this repository tests the
  shape.
- [x] T003 Five modules, each with one `.just` file named for its directory —
  FR-006:
  `ls -d */ | while read d; do [ -f "$d$(basename $d).just" ] && echo $d; done | wc -l`
  → `5`.
- [x] T004 Thirty-eight recipes, **counted two ways that must agree** — FR-011.
  By summary:
  `for d in docusaurus go just md react; do just --justfile $d/$d.just --working-directory . --summary; done | wc -w`
  → `38`. Then by grep for recipe headers, per module, and compare the two
  per-module figures rather than only the totals: two wrong numbers can sum to a
  right one. Expect 10, 16, 2, 2, 8.
- [x] T005 The unprefixed recipe is still exactly one, and still `run` — FR-012:
  list the 38 names and check which lack their module's prefix. If a second
  appears, the contract has changed shape and FR-012's count is wrong rather
  than merely dated.
- [x] T006 The two argument-taking recipes are still those two — FR-011a: `run`
  variadic, `docusaurus-bump` requiring `version`, and the other 36 taking none.
  Read the recipe headers; a signature is not visible in `--summary` output,
  which is why FR-011a exists.
- [x] T007 The variables table is complete — FR-013a. For each module, compare
  its `{{ variable }}` references against its assignment lines; the only
  references without an assignment must be the two recipe parameters from T006.
  **This is the check that was nearly left as a caveat**, so it is a task rather
  than a note.
- [x] T008 The pinned-inner-floating-outer shape holds — FR-014: `md.just` still
  pins mdformat, mdformat-gfm and Python by version, `go.just` still pins a
  coverage target, and nothing pins any module.
- [x] T009 Line and file counts — FR-016: `wc -l */*.just` → `487` total;
  `find . -name '*.md' -not -path './.git/*' | wc -l` → `11`;
  `wc -l */README.md` → `353` total; `wc -l README.md` → `112`; and no `docs/`
  tree exists.

**Phase 2 result, 2026-09-30.** Every figure reproduced exactly at `e765614`: 0
Go files, 5 modules, 38 recipes agreeing per module by both methods
(10/16/2/2/8), 487 `.just` lines, 11 markdown files, 353 + 112 README lines, 20
variables, `run` still the only unprefixed recipe, `docusaurus-bump version` and
`run *args` still the only two taking arguments, and T007 clean across all five
modules. Nothing had moved.

**Checkpoint**: every figure in the specification has been produced by a command
rather than trusted. Anything that moved is recorded before Phase 3 begins.

______________________________________________________________________

## Phase 3: User Story 1 — a consumer knows what it is depending on (Priority: P1)

**Goal**: the contract is stated well enough to act on without opening the
repository.

**Independent test**: SC-001's reading.

- [x] T010 [US1] Verify the edges from the consumers rather than from this
  repository — FR-003 and FR-004: for each of `osapi`, `gohai`, `nats-client`,
  `nats-server`, `osapi-orchestrator` and `osapi-justfiles` itself, read the
  `fetch` recipe and record which modules it takes. Expect five for `osapi`,
  three each for the next four, and one for `osapi-justfiles`. Take the
  repository set from `gh repo list osapi-io --no-archived --visibility public`,
  not from the specification's list — `global/repositories` says a written list
  is right when written and wrong afterwards, and this task is where that
  applies to this feature.

- [x] T011 [US1] Run the SC-001 reading. Give somebody who has not opened the
  repository the specification alone and three questions: what are the five
  modules; which recipes does the `md` module supply; and what must a consumer
  set before importing `go`? A person is preferred; a fresh agent given only
  `spec.md` is the fallback. **Record what it proves and what it does not** —
  that the answers are in the text, not that a maintainer would enjoy finding
  them.

  **Three of three answered, and it found three defects doing it.** A fresh
  agent given only `spec.md` answered all three questions, but had to *infer*
  what each module is for from its recipe prefixes — the specification named the
  five modules in three places and said nowhere what any of them does. That is
  now FR-006a, and it was a section 3 requirement unmet: naming the parts is not
  stating what they are for.

  It caught FR-013's table printing defaults for three of `go`'s seven variables
  while FR-013a claimed all twenty have one. Both were true — the four unprinted
  ones are computed or empty rather than absent — but **an empty default and a
  missing default are indistinguishable in a table that prints neither, and they
  are opposite facts.** All twenty are now printed.

  And it reported the document reads as requirements plus self-referential
  narrative rather than as one coherent whole, with the consumer-facing facts
  outnumbered by commentary about writing the baseline. Recorded as FR-022a and
  handed to `system`, because the fix is structural rather than editorial: one
  document carrying both an inventory and a shape finding serves the first
  reader worse.

  **What it proves and what it does not.** That the answers are in the text, for
  all three. Not that a maintainer mid-task would find them — the reading said
  plainly they would have to read past several paragraphs of methodology to
  reach what they came for.

______________________________________________________________________

## Phase 4: User Story 2 — the shape is tested against a repository with no code (Priority: P1)

**Goal**: the programme learns whether the seven-section shape fits a repository
that is not a Go library, before four more baselines are written to it.

**Independent test**: SC-004 — each of the seven sections either filled, or
absent with a stated reason.

- [x] T012 [US2] Confirm nothing changed in the inventoried repository — SC-007:
  `git -C ~/git/osapi-io/osapi-justfiles status --porcelain` is empty. A
  baseline that edited what it was describing would have measured its own
  change.
- [x] T013 [US2] Walk the seven sections against the specification and confirm
  each is filled: what it is (FR-001, FR-002), where it sits (FR-003 to FR-005),
  architecture (FR-006 to FR-010), the contract (FR-011 to FR-015), measurements
  (FR-016), gaps (FR-017 to FR-020), exclusions (FR-021 to FR-022). **Zero
  omissions is the expected result**, and FR-022 states it — so this task
  confirms a claim rather than discovering one, and a section found empty means
  FR-022 is wrong.
- [x] T014 [US2] Confirm FR-020 says what the fragment did and did not give. It
  must name the one thing `global/baseline` does not say — what "contract" means
  for a repository exposing no code — and must leave to `system` whether the
  fragment should say it. **It must not amend the fragment**, which is a change
  to `.charter/` and belongs to `system`. The finding is this baseline's; the
  fix is not.

______________________________________________________________________

## Phase 5: User Story 3 — a change here is the widest change (Priority: P2)

**Goal**: somebody editing a module knows the reach before they edit.

- [x] T015 [US3] Confirm FR-005 and FR-017 together state reach and mechanism
  without asserting a violation: that every consumer fetches from
  `refs/heads/main`, that nothing records which version a build used, and that
  the strained rule is `global/tooling`'s "both provisioning paths resolve to
  the same version" — which here has no mechanism rather than a divergent one.
  The distinction matters: `.just/` is gitignored, so the committed-output
  clause does not apply, and a baseline asserting a violation it cannot support
  is the invented standard `global/correction` names.

______________________________________________________________________

## Phase 6: Gaps, and what happens to them

- [x] T016 [P] Confirm each of the four gaps names both sides and an owner —
  FR-017 through FR-020 — and that none is corrected here. Two are
  `osapi-justfiles`', one is `system`'s, and one is a question handed to
  `system` about its own fragment.

- [x] T017 Open the amendment `system`'s 002 needs for FR-019, or record that it
  is not opened. 002's FR-031 records this repository as having 0 documentation
  pages, which is true of pages and misleading as a statement about
  documentation: it has **no documentation pages and six documentation files**.
  That is 002's to amend in its own change. **This task is not "fix it"** — it
  is "do not let it be forgotten", and recording that it was left is an
  acceptable outcome as long as it is recorded.

  **Opened, and it grew.** The page-count correction went in as 002's FR-032.
  Two more went with it, because this baseline's verification had found them by
  then: FR-033, that `osapi-justfiles` has seven consumers rather than six —
  `specs` fetches `just` and `md`, and 002's own repository map said six while
  carrying the command that returns seven — and FR-034, that the programme
  covers six components while the organization has eight public repositories, so
  the difference between "the six" and "the repositories" is stated rather than
  left implicit. FR-034 exists because that implicit difference is what produced
  the wrong consumer count.

______________________________________________________________________

## Phase 7: Verification and archival

- [x] T018 Run `cd specs && mise exec -- just test` — SC-006.

- [x] T019 Run `speckit-archive-run specs/001-justfiles-baseline` once this
  branch has merged. It creates this project's `.specify/memory/spec.md` and
  `plan.md`, which do not exist yet — this is the project's first archival, so
  there is nothing to fold into and every requirement enters as a new entry
  under the feature's own IDs.

  **Archived 2026-09-30.** `.specify/memory/spec.md`, `plan.md` and
  `changelog.md` all created; 29 requirements, 3 stories, 4 entities, 4 edge
  cases, 7 outcomes and 5 assumptions as AS-001 to AS-005, each carrying an
  item-level source ref. Nothing folded and nothing superseded, because there
  was nothing there. No agent context file exists in this project, so that step
  was skipped rather than guessed at.

- [x] T020 Mark `system`'s 002 T016 done, which is what opened this unit. Do
  **not** mark T017 or any other unit: this is unit 6 of 12, and four baselines
  and two moves remain.

______________________________________________________________________

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1** has none.
- **Phase 2** blocks everything. Until the figures are reproduced, every later
  task is checking prose against prose.
- **Phases 3, 4 and 5** are independent of each other once Phase 2 passes.
- **Phase 6** depends on Phase 2 only for FR-019's figures.
- **Phase 7** is last, and T019 needs this branch merged.

### What is genuinely parallel

- T010 and T011 — one is a set of greps across six repositories, the other a
  reading.
- T013, T015 and T016 — three different readings of the same merged text.

### What only looks parallel

T004 and T005 both enumerate the 38 recipes, and T005's answer depends on T004's
list being right. Run them in order.

______________________________________________________________________

## Implementation Strategy

### MVP

Phases 1 and 2. If the re-measurement passes, the inventory is worth archiving
even if nothing else on this list runs — the counts are the part a later reader
cannot check cheaply.

### Then

Phase 4 before Phase 3, if only one can be done. The shape finding is what four
later baselines depend on; the consumer reading is what one repository's
maintainers depend on.

______________________________________________________________________

## Notes

- No Go code changes anywhere. No change of any kind in `osapi-justfiles`.
- The specification was amended once before this list existed, at specs#179,
  adding FR-011a and FR-013a. Both came out of writing the plan rather than out
  of implementing anything, which is the argument for a planning phase that
  re-reads its own claims.
- FR-024, FR-028 and FR-031 named in the specification are `system`'s 002's, not
  this feature's. Do not renumber them and do not treat them as tasks here.
