# Tasks: The job system

**Feature**: `004-job-system` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md) | **Plan**: [plan.md](plan.md)

**Input**: [research.md](research.md) for the three decisions;
[data-model.md](data-model.md) for what each requirement replaces and what the
page keeps; [quickstart.md](quickstart.md) for how each criterion is verified.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallel-safe: different files, no dependency on an incomplete task.
- **[US1]**, **[US2]**, **[US3]** — the user story served.
- Every task names the file it touches.

## Path Conventions

- `specs/` — this repository: the corpus under
  `components/osapi/specs/004-job-system/`, the skill under
  `.claude/skills/add-a-domain/`.
- `osapi/` — the site under `docs/docs/sidebar/architecture/`.

The corpus half is merged. Everything below is one osapi pull request plus one
change here, and the osapi one is what ends the duplication.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Confirm the line ranges in [data-model.md](data-model.md) against
  `osapi/docs/docs/sidebar/architecture/job-architecture.md` as it stands. 003's
  T001 confirmed them at 630 lines; anything merged into that page since moves
  them again, and the split is done by section boundary rather than by line
  number for that reason.

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 [US3] Re-run the SC-002 citation checks from
  [quickstart.md](quickstart.md). Every cited file must still print. A citation
  that stopped resolving between the specification merging and this change is a
  requirement describing code that moved, and it is corrected here rather than
  carried.

## Phase 3: User Story 1 — a contributor knows what they are handed (Priority: P1) 🎯 MVP

**Goal**: the mechanics are stated only in the corpus, and the page no longer
holds a second copy.

**Independent test**: SC-004's greps return nothing from the page, and SC-001's
three questions are answerable from the specification alone.

- [x] T003 [US1] Remove from
  `osapi/docs/docs/sidebar/architecture/job-architecture.md` the sections
  [data-model.md](data-model.md) marks as replaced: Overview, Architecture
  Principles, Job Flow, NATS Configuration, Subject Hierarchy and Semantic
  Routing Rules, the routing *rules* from Target Types, Agent Implementation,
  Facts Collection, Package Architecture, Performance Optimizations, Security
  Considerations, and Error Handling.
- [x] T004 [US1] Delete the three wrong statements with the sections that hold
  them — the `{status}.{uuid}` key format, `MaxDeliver: 3` and `AckWait: 30s`,
  and the 24-hour TTL. Research Decision 1: none of the three is corrected in
  place, because correcting a number in two places is how it drifted the first
  time.
- [x] T005 [US1] Run the SC-004 grep. No output. A match is a second statement,
  and for the first three a second statement that is wrong.

## Phase 4: User Story 2 — the page still serves an operator (Priority: P1)

**Goal**: what remains is a page rather than a remainder, and its address is
unchanged.

**Independent test**: 003's SC-002 and SC-003 checks, plus the site build.

- [x] T006 [US2] Rewrite the page's opening so it introduces what the page now
  is — running and watching jobs — rather than opening on an overview of a
  system it no longer describes. FR-003 of 003: the operator's half must read as
  a coherent page, not as what was left.
- [x] T007 [US2] Keep, and check for orphaned cross-references: the submission
  CLI examples, the job states as observed, polling, the target syntax an
  operator types, the CLI command reference, and the metrics worth watching.
  [data-model.md](data-model.md) lists them with their line ranges.
- [x] T008 [US2] [P] Update any page that linked into a removed section.
  `architecture.md`'s Deep Dives and `system-architecture.md`'s Further Reading
  both point here; a link to a heading that no longer exists is what the site
  build catches.
- [x] T009 [US2] Confirm the page states nothing that sends an operator to the
  corpus — 003's FR-012. A contributor arriving here is served by the skill, not
  by a pointer on an operator page.
- [x] T010 [US2] Run
  `cd osapi && just docusaurus-fmt-check && just docusaurus-build`.
- [x] T011 [US2] Open and merge the osapi pull request for T003–T010. **This is
  the task that ends the duplication.** Until it lands, the corpus and the page
  both state these rules and three of the page's numbers are wrong — see
  [research.md](research.md), "The risk this feature carries".

## Phase 5: User Story 3 — the rule has one home (Priority: P2)

**Goal**: the skill cites the requirements instead of restating the mechanics.

**Independent test**: SC-004's `just test`, and SC-005's grep.

- [x] T012 [US3] Replace the delivery-semantics section of
  `specs/.claude/skills/add-a-domain/references/agent.md` with a citation table
  naming FR-009, FR-010, FR-011, FR-012, FR-013, FR-014 and FR-015 — written out
  rather than as a range, so a coverage check can see each one — in the shape
  [003's citation contract](../003-corpus-backfill/contracts/citation.md)
  defines. Leave the processor, registration and platform-selection material
  alone — research Decision 2.
- [x] T013 [US3] Run `cd specs && just test`. `skill-lint` resolving the new
  citations is the gate.
- [x] T014 [US3] Run the SC-005 grep and read the Security Considerations
  requirements: they must cite [002](../002-agent-key-store/spec.md) rather than
  explain signing again.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T015 [P] Run the SC-001 reading with somebody who has not read the site
  page, using the three fixed questions. An author cannot test their own corpus
  for completeness.
- [x] T016 [P] Run the "check that matters most" from
  [quickstart.md](quickstart.md): the page's last commit must postdate the
  specification's merge. If it does not, this feature is unfinished whatever the
  corpus says.
- [x] T017 Mark 003's T010 and T011 done, and update 003's `tasks.md` to record
  that Subject A completed — including which of its phases this feature carried
  out, so the next subject reads a task list that matches what happened.
- [x] T018 Run `/speckit-archive-run specs/004-job-system` once T011 and T013
  have merged, consolidating this subject into
  `specs/components/osapi/.specify/memory/`. Archive after the implementation,
  never before: what merged here is the statement, and the outcome is only true
  once the page no longer disagrees with it.

## What the consistency check found

`speckit-analyze` over the specification, this plan and this list, before the
first task ran:

| Finding                                           | Severity | What was done                                                                                                                                                 |
| ------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-010 and FR-011 had no task naming them         | MEDIUM   | They sat inside "FR-009 through FR-015" in T012. The range is written out now: a requirement a coverage check cannot see is one that can be dropped silently. |
| FR-024 had no task naming it                      | MEDIUM   | T011 names it. FR-024 is the obligation that the site change lands, so the task that merges it is the one that discharges it.                                 |
| No ambiguity, duplication or placeholder findings | —        | No vague adjectives, no TODO markers, no two requirements stating the same rule.                                                                              |
| No constitution conflicts                         | —        | Documentation, Verification and Correction are each satisfied by a named mechanism; the plan's Constitution Check records how.                                |

21 of 24 requirements were covered before those fixes; all 24 are now.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** (T001) first: the ranges decide what T003 removes.
- **Phase 2** (T002) blocks Phase 3. A citation that stopped resolving is
  corrected before anything is deleted, because the page is the only other copy.
- **Phase 3** (T003–T005) and **Phase 4** (T006–T010) are one pull request and
  are separated here by intent rather than by sequence: removal and rewriting
  touch the same file, so they happen together and T011 merges both.
- **Phase 5** (T012–T014) depends on the specification being merged, which it
  is. It may land before or after T011; the citations point at the corpus either
  way.
- **Phase 6** (T015–T018) depends on T011 and T013, except T016, which is the
  check that T011 happened at all.

### The dependency nothing enforces

T011. The corpus states these rules as of the specification's merge, so the
window 003's research Finding 3 describes is open now — and it is the bad
version of that window, because three of the page's numbers are not merely
duplicated but wrong. If this work pauses, T011 is what an issue in osapi must
name.

### Parallel Opportunities

- T008 alongside T003 through T007: different files, same build checking them.
- T015 and T016, once the pull request has landed.

## Implementation Strategy

One osapi pull request: remove, rewrite, check the links, build. Then the skill
citation here, which can go either side of it.

There is no smaller first step worth taking. Half a page is a page that
contradicts itself, and the three corrections are the reason not to leave it
half done: a reader who finds the page today gets `MaxDeliver: 3` for a consumer
that has used 5 for some time.
