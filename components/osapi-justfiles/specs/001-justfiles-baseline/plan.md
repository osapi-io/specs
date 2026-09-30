# Implementation Plan: A baseline for osapi-justfiles

**Branch**: `001-justfiles-baseline` | **Date**: 2026-09-29 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi-justfiles/specs/001-justfiles-baseline/spec.md`

## Summary

State what `osapi-justfiles` is, so its memory stops holding only a constitution
composed from `.charter/`. Twenty-two requirements, every one of the form "the
corpus MUST state X".

**Partly retrospective, and it says which parts.** The inventory was produced by
reading the repository and then stated, so the measuring is behind us. What is
genuinely ahead is the verification — the commands in FR-016 have to reproduce
their figures against a fresh checkout, and that is what `tasks.md` carries.
[gohai's baseline plan](../../../gohai/specs/001-gohai-baseline/plan.md) made
the same admission about itself and had no task list at all; this one has one,
because a baseline whose counts are never re-run is a baseline nobody checked.

One thing in it is not retrospective and belongs in a plan rather than a
specification: **what to do when a required section's word does not fit the
repository.** Section 4 of the shape is "the contract", and the word reads as
though it presumes exported symbols. The decision, and the reasoning behind it,
is below under "The one interpretive decision".

**Nothing lands in the `osapi-justfiles` repository.** That is what
CONTRIBUTING's "Seeding a component" requires of a baseline: the deliverable is
the inventory, and it lives here.

## Technical Context

**Language/Version**: Markdown. No compiled artifact. The repository being
inventoried contains **no compiled language at all** — 0 Go files — which is the
condition that makes it the shape's test case.

**Primary Dependencies**: None. The corpus depends on nothing at runtime. The
repository being inventoried depends on no other repository in the organization,
which is the fact FR-003 states.

**Storage**: `components/osapi-justfiles/specs/` for the specification — a
directory this feature creates, since it is the project's first — and
`components/osapi-justfiles/.specify/memory/` for what archival consolidates
into. That memory holds only a constitution before this feature, which is the
condition the feature exists to end.

**Testing**: `just test` in the specs repository — `mdformat --check`,
`just-fmt-check`, and `scripts/validate-skills.py`. There is no code to unit
test. Separately, every count in the specification carries the command that
reproduces it, and re-running those commands against `osapi-justfiles` is what
checks the inventory. The formatting gate cannot tell a right count from a wrong
one.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the `osapi-justfiles` repository —
`git -C osapi-justfiles status` clean is SC-007. No count stated without the
command that produces it. Every gap recorded with both sides named and an owner,
none corrected here. No compatibility policy invented for a repository that has
none.

**Scale/Scope**: One repository inventoried. Five modules, 38 recipes and about
twenty variables stated as a contract; six consuming repositories named by their
edges rather than described.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Documentation** | The recipes are the statement of record and this states where they live and what they take, never what the shell inside them does — FR-021's first exclusion. A rule a tool enforces is not restated as prose.                             |
| **Verification**  | Every count carries its command, and the recipe count was taken **two ways that agree**. That second measurement is the principle's "running something that would fail if the claim were false" rather than reading a file and concluding. |
| **Tooling**       | Nothing provisioned. FR-017 records that nothing pins the modules, as the rule it strains rather than as a violation — the committed-output clause does not bite, because `.just/` is gitignored rather than committed.                    |
| **Correction**    | Four findings recorded as gaps with owners, including one against `system`'s own 002. FR-015 refuses to invent a compatibility policy the repository does not have, which is the standard-to-fill-a-template failure this principle names. |
| **Workflow**      | Stages 3 and 4 for `001`, in one branch, after stage 1 merged as specs#178.                                                                                                                                                                |
| **Baseline**      | This is the first baseline written under the fragment. FR-020 records that it was sufficient except for one question, which is evidence about the fragment rather than about this repository.                                              |
| **Repositories**  | The consumer set was taken from the command each time rather than from a list, and this baseline states only its own edges — the map is `system`'s.                                                                                        |
| **Tracking**      | Nothing here becomes an issue. The gaps are recorded where the next reader of this repository's memory will find them, and the two that imply work in `osapi-justfiles` name it as the owner.                                              |

**Result**: no violations.

## The one interpretive decision

The shape's section 4 is **"the contract"**, and 002 wrote it expecting a
repository that exposes code. This one exposes none. Three readings were
available:

1. **Omit the section**, using 002's FR-011 allowance, and state why. Rejected:
   the repository plainly *has* something consumers depend on, so an omission
   would record an absence that is not there — and it would have exercised
   FR-011 on the wrong case, teaching the programme that a non-Go repository has
   no contract.
2. **Read "contract" narrowly as exported symbols** and conclude the section is
   not applicable. Rejected for the same reason, with the additional cost that
   the fifth and sixth baselines would inherit the conclusion.
3. **Read "contract" as what a consumer may depend on**, whatever its form.
   Taken.

Under the third reading the contract is **38 recipe names and about twenty
variable names**, and it passes every test that makes a contract worth stating:
a consumer depends on it, renaming part of it breaks them at their next fetch,
and nothing in the repository declares it. That last part is what makes stating
it valuable rather than redundant.

**What this decision costs, stated rather than hidden**: it widens the word for
every baseline after it. A later reader could take "contract" to mean any
observable regularity, which would make the section unbounded. The bound that
keeps it useful is the one applied here — *something a consumer's build breaks
on* — and FR-020 hands the question of whether `global/baseline` should say so
to `system`, because a fragment is amended in its own change.

## The reading order, and why it was that order

The same order
[gohai's baseline](../../../gohai/specs/001-gohai-baseline/plan.md) used, for
the same reason: it is what keeps prose from becoming a source.

1. **The files first.** Each module's `.just` file for its recipes and
   variables, the root `justfile` for the self-consumption asymmetry, every
   consumer's `fetch` recipe for the edges.
2. **The counts by command**, never by reading a sentence claiming one. The
   recipe count was taken twice by different means and the results compared
   before either was written down.
3. **The prose last**, and only to find disagreements. Six READMEs and a
   112-line root README were available and none was transcribed.

Reading the READMEs first would have produced a plausible inventory of what the
modules are *for* and would not have found the unprefixed `run` recipe, the
pinned-inner-floating-outer version shape, or the self-consumption asymmetry —
none of which any README mentions.

## Project Structure

### Documentation (this feature)

```text
components/osapi-justfiles/specs/001-justfiles-baseline/
├── spec.md              # merged at specs#178, amended at #179; 24 requirements
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
components/osapi-justfiles/
├── specs/001-justfiles-baseline/spec.md   # the statement of record
└── .specify/memory/                        # where archival puts it
    ├── constitution.md                     # composed; eight fragments
    ├── spec.md                             # created by archival
    └── plan.md                             # created by archival
```

### What is being inventoried

```text
osapi-justfiles/                 # nothing here changes
├── justfile                     # its own test recipe, resolving two ways
├── docusaurus/docusaurus.just   # 10 recipes
├── go/go.just                   # 16 recipes, one of them unprefixed
├── just/just.just               # 2 recipes, no variables
├── md/md.just                   # 2 recipes, pinning mdformat and Python
└── react/react.just             # 8 recipes
```

**Structure Decision**: no corpus subject file beyond `spec.md`. The statement
is the specification, archived into memory like every other feature's. No skill
gains a reference: no skill in this repository builds or formats anything, so a
citation into these recipes would be a rule invented for a reader who does not
exist — the same reasoning
[007's FR-017](../../../osapi/specs/007-the-embedded-ui/spec.md) applied to the
`add-a-domain` skill.

## What the verification actually checks, and what it cannot

`tasks.md` re-runs every command in FR-016 against a fresh checkout. That checks
the **counts**. It does not check the two things most likely to be wrong, which
is stated here so a green task list is not mistaken for a verified inventory:

- **Whether a recipe does what its name suggests.** FR-021 excludes it
  deliberately.

- **Whether the contract is complete.** This was going to be the second entry on
  this list, worded as a limit: a variable a module reads without assigning a
  default would not appear in FR-013's table, because that table was built from
  assignment lines. **Writing it down was enough to notice it was testable.**
  Comparing each module's `{{ variable }}` references against its assignment
  lines took one command, the table turned out to be complete, and the two
  references it could not account for were recipe parameters — which is how
  FR-011a's two argument-taking recipes were found. Both results went into the
  specification by amendment at specs#179, before this plan merged.

  The entry stays here in its corrected form because the mistake is worth
  keeping: a limit that can be tested is not a limit, it is a check nobody ran.
  Stating it as a boundary of what the inventory could know read as rigour and
  was the opposite.

- **Whether the modules are what the consumers need.** That is a judgement about
  fitness, not a measurement.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
