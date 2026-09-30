______________________________________________________________________

## description: "Task list for the osapi baseline"

# Tasks: A baseline for osapi

**Input**: Design documents from `components/osapi/specs/006-osapi-baseline/`

**Prerequisites**: [spec.md](spec.md) merged (specs#169) and amended before
planning, [plan.md](plan.md)

**Tests**: none. There is no code. What stands in is seven commands that must
reproduce their figures, a classification that must sum to 219, and a reading.

## This list is written after the fact, and says so

The specification merged and no plan or task list followed, which left the
feature unarchivable — the archival gate requires a `plan.md`. Six other
features reached osapi's memory while this one sat at stage 1, including the
embedded UI, whose own specification depends on the classification this baseline
produced.

So the tasks below were written knowing their answers. That makes them weaker
than a task list written in advance, and it does not make them worthless: every
count here was **re-measured** while writing them rather than copied from the
specification, and the classification was re-summed. What a late list cannot do
is catch a mistake before it reaches the statement — which is exactly what
happened to the page classification, recorded in T006.

**Nothing lands in the osapi repository.** T012 verifies that.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Confirm the specification on `main` is the amended one:
  `grep -c 'FR-019' spec.md` must find the UI-divergence requirements, which
  were added before planning. A plan written against the unamended text would
  describe a feature that no longer exists.

  **Confirmed.** FR-019 through FR-021 are present; they record the 263-line
  second statement at `ui/docs/architecture.md`, which the page classification
  did not reach because it counted published pages.

______________________________________________________________________

## Phase 2: Foundational — the re-measurement

**This phase is the verification.** Every command comes from FR-012. A figure
that has moved is recorded as a new measurement with its date, not worked
around.

Run from `~/git/osapi-io/osapi`.

- [x] T002 The Go counts — FR-012:
  `find . -name '*.go' -not -path './.git/*' | wc -l` → `2739`, and the same
  with `-not -name '*_test.go'` → `1814`.

- [x] T003 The two page counts, which differ by a **definition** — FR-012 and
  FR-013: `find docs/docs -name '*.md' -not -path '*/node_modules/*' | wc -l` →
  `219`, and `find docs -name '*.md' -not -path '*/node_modules/*' | wc -l` →
  `221`. Both must be stated with what each counts. A reader given only one will
  conclude the other is broken.

- [x] T004 The structural counts — FR-012: provider categories `6`, API domains
  `24`, SDK methods `117`. The domain count needs its exclusions — `gen`,
  `mocks`, `common`, `apierr` — or it reads high.

- [x] T005 [P] Confirm the dependency edges from the source rather than from a
  list: `grep -oE "osapi-io/[a-z-]+" go.mod` for what osapi consumes, and the
  same in `osapi-orchestrator/go.mod` for what consumes it. FR-005 and FR-006.

  **Phase 2 result, 2026-09-30.** All seven figures reproduced exactly. Nothing
  had moved since the specification was written.

______________________________________________________________________

## Phase 3: User Story 1 — somebody learns what osapi is (Priority: P1)

**Goal**: memory answers what the repository is before it answers what was
decided about it.

- [x] T006 Confirm the classification of all 219 pages sums to 219 and lists
  every page exactly once — FR-018. **This is the check that already failed
  once**: the first attempt summed to 217, because `usage/configuration.md` and
  `intro.md` sit outside the subdirectory counts the table was built from. Two
  pages missing from a 219-page classification is invisible to every other check
  in this list.
- [x] T007 [US1] Confirm section 4 is **mostly citation** — FR-009 through
  FR-011. osapi's contract is stated across four archived features, and a
  baseline restating any of it creates the second statement the programme exists
  to end. Check that each part of the contract names where it lives rather than
  saying it again.
- [x] T008 [US1] Confirm sections 1 and 2 answer what the repository is and
  where it sits without requiring another baseline to be read first. osapi is
  the hub: five other components state their edges against its section 2, so a
  section 2 that assumes the reader has read them is circular.

______________________________________________________________________

## Phase 4: User Story 2 — the architecture survives a rename (Priority: P1)

- [x] T009 [US2] Confirm section 3 states what each part is **for** and what
  passes between parts, and contains no transcribed call graph and no exhaustive
  list of exported functions — 002's FR-004 through FR-006. The test is whether
  a rename would falsify a sentence.
- [x] T010 [US2] Confirm the four gaps name both sides and an owner — FR-014
  through FR-017 — and that none is corrected here. The three surviving
  contributor pages are the substantive one, and FR-016 states that the finding
  changes the programme's arithmetic from eleven units to twelve.

______________________________________________________________________

## Phase 5: User Story 3 — the pages that stayed are an operator's (Priority: P2)

- [x] T011 [US3] Confirm the classification's 216 "stays" are user-facing and
  its 3 "moves" are the contributor pages FR-014 names. A page classified
  wrongly either strands contributor knowledge on the site or moves an
  operator's reference into the corpus.
- [x] T012 Confirm nothing changed in the inventoried repository:
  `git -C ~/git/osapi-io/osapi status --porcelain` is empty of changes this
  feature made. A baseline that edited what it was describing would have
  measured its own change.

______________________________________________________________________

## Phase 6: Verification and archival

- [x] T013 Run `cd specs && mise exec -- just test` — SC-007.
- [x] T014 Run `speckit-archive-run specs/006-osapi-baseline` once this branch
  has merged. osapi's memory is **not** empty — it holds 1,840 lines from six
  archived features — so this run folds rather than seeds, and section 4's
  citations must not be expanded into statements while merging.
- [x] T015 Record in `system`'s 002 that this baseline is archived, and leave
  T023 open: it names three pages, `007` moved two, and the `sdk/guidelines.md`
  remainder has no feature yet.

______________________________________________________________________

## What this list does not check

Stated because a green list here is weaker evidence than a green list usually
is:

- **Whether the classification is right page by page.** It sums to 219 and each
  page appears once; whether each verdict is correct is a review.
- **Whether section 4's citations are complete.** A rule of osapi's contract
  that none of the four archived features states would not show up as a gap,
  because nothing points at its absence.
- **Whether the architecture survives a rename.** Only re-reading section 3
  after a refactor settles that, which is why US2's test is a reading rather
  than a command.

______________________________________________________________________

## Dependencies & Execution Order

- **Phase 2** blocks everything: until the figures are reproduced, every later
  task compares prose against prose.
- **T006 blocks Phase 5**, because a classification that does not sum cannot be
  checked for correctness.
- **Phase 6** needs this branch merged.

## Notes

- No Go code changes. No change of any kind in osapi.
- The specification was amended once before planning, adding FR-019 through
  FR-021 for the UI divergence. Those three are what `007` was opened against.
- This baseline found the three pages the corpus backfill never looked at, which
  is the finding that made the programme twelve units rather than eleven.
