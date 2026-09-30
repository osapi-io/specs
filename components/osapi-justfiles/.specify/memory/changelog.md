# Changelog

## Merged Features Log

### A baseline for osapi-justfiles — archived 2026-09-30

**Branch:** `001-justfiles-baseline`

**Spec:** [specs/001-justfiles-baseline/spec.md](../../specs/001-justfiles-baseline/spec.md)

**What was added:**

- The project's first memory. Before this it held only a constitution composed
  from `.charter/`, which states what binds every repository and nothing about
  this one.
- What the repository is: a library of shared `just` recipes, **zero Go files**,
  five independent modules, existing so that a convention binding several
  repositories is written once.
- Where it sits: the only node in the dependency graph with **no outgoing edge**
  and seven incoming, which makes a change here the widest change available in
  the organization.
- The contract, in two halves because a consumer depends on both: 38 recipes by
  name, and twenty override variables with every default stated. Two recipes take
  arguments and 37 of 38 carry their module's prefix.
- Four gaps with owners: nothing pins the modules, the repository consumes its
  own `md` module asymmetrically, 002's page count answers half its question, and
  `global/baseline` does not say what a contract means for a repository exposing
  no code.
- FR-001 to FR-022 with FR-004a, FR-006a, FR-011a, FR-013a, FR-013b, FR-021a and
  FR-022a; three user stories; four entities; four edge cases; SC-001 to SC-007;
  AS-001 to AS-005.

**The shape finding, which mattered more than the inventory:**

- This unit existed to answer whether `system`'s seven-section shape fits a
  repository that is not a Go library. **It does, and no section was omitted** —
  002's FR-011 allowance for omitting one was never needed.
- Section 4 was the only one requiring interpretation. "The contract" reads as
  though it presumes exported symbols; here it is 38 recipe names and twenty
  variable names, which is an interface by every test that matters. The bound that
  keeps the word useful is *something a consumer's build breaks on*.
- FR-021a records that three of the seven section **headings** had drifted from
  002's names — each an improvement in isolation, all three now verbatim. This was
  the first baseline written to the shape, and four more will be written by
  copying it rather than by re-reading 002.

**New Components:**

- None. No file in the `osapi-justfiles` repository changed, and a baseline never
  changes one.

**Three amendments taken from its own verification, after the specification
merged:**

- A consistency pass found the variable count hedged as "about twenty" in five
  places while the table beside it enumerated exactly 20, and found no row for
  them in the measurements at all. FR-013b.
- The task that takes the repository set from `gh repo list` rather than from a
  written list found a **seventh** consumer — `specs`, the design record. The
  specification had said six, because the frame was the six components rather
  than the repositories the command returns. FR-004a.
- The SC-001 reading found the five modules named in three places and explained in
  none, and found the variables table printing defaults for three of `go`'s seven
  while another requirement asserted all twenty have one. FR-006a, and FR-013's
  full table.

**None of the three was found by re-reading the specification.** That is the
transferable part, and it is why this baseline has a task list where `gohai`'s
did not.

**Success criteria, recorded as they actually landed:**

- SC-001's reading answered all three of its questions, and found three defects
  doing it. It also judged the document to read as requirements plus
  self-referential narrative, with the consumer-facing facts outnumbered by
  commentary about writing the baseline. That judgement is **unresolved** and its
  owner is `system`'s 002 — FR-022a.
- Everything else reproduced exactly at `e765614`.

**What went to `system` rather than being fixed here:** the page-count
correction, the seventh consumer, and the difference between "the six components"
and "the eight repositories" — amended into 002 as FR-032, FR-033 and FR-034.

**Tasks Completed:** 20/20 tasks
