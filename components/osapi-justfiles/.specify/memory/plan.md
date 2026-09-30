# Main Implementation Plan

> **Revision**: 2026-09-30 — Seeded from the justfiles baseline
> (`specs/001-justfiles-baseline`). A documentation feature: nothing in the
> `osapi-justfiles` repository changed, and nothing will from a baseline. What is
> recorded here is the shape the work had and the one decision it genuinely made
> — how to fill a required section whose word does not fit a repository with no
> code.

## Summary

State what `osapi-justfiles` is, so its memory stops holding only a constitution
composed from `.charter/`. Twenty-nine requirements, every one of the form "the
corpus MUST state X".

This was unit 6 of twelve in the baseline programme and taken deliberately out of
order: it is the smallest repository in the organization and the largest risk to
the *shape*, because it has no Go code, no `docs/` tree and no documentation
site. The cost of discovering the shape does not fit is paid once here or four
times later.
[Source: specs/001-justfiles-baseline/plan.md -> "Summary"]

## Technical Context

**Language/Version**: None. The repository contains **no compiled language at
all** — 0 Go files — and its only executable content is `just` recipes and the
shell they invoke.
[Source: specs/001-justfiles-baseline/plan.md -> "Language/Version"]

**Primary Dependencies**: None. The repository depends on no other repository in
the organization, and the corpus depends on nothing at runtime. Each module pins
the tools it invokes — `md` pins mdformat, mdformat-gfm and Python; `go` pins a
coverage target — while nothing pins the module itself.
[Source: specs/001-justfiles-baseline/plan.md -> "Primary Dependencies"]
[Source: specs/001-justfiles-baseline/spec.md -> FR-014]

**Storage**: `components/osapi-justfiles/specs/` for the specification and
`components/osapi-justfiles/.specify/memory/` for what archival consolidates
into. That memory held only a constitution before this feature.
[Source: specs/001-justfiles-baseline/plan.md -> "Storage"]

**Testing**: `just test` in the specs repository — `mdformat --check`,
`just-fmt-check`, and `scripts/validate-skills.py`. There is no code to unit
test. Separately, every count in the specification carries the command that
reproduces it, and re-running those commands is what checks the inventory: **the
formatting gate cannot tell a right count from a wrong one.**
[Source: specs/001-justfiles-baseline/plan.md -> "Testing"]

**Target Platform**: The corpus.
[Source: specs/001-justfiles-baseline/plan.md -> "Target Platform"]

**Project Type**: Documentation.
[Source: specs/001-justfiles-baseline/plan.md -> "Project Type"]

**Constraints**: No change to the `osapi-justfiles` repository. No count stated
without the command that produces it. Every gap recorded with both sides named
and an owner, none corrected in the baseline. **No compatibility policy invented
for a repository that has none.**
[Source: specs/001-justfiles-baseline/plan.md -> "Constraints"]

**Scale/Scope**: One repository inventoried. Five modules, 38 recipes and twenty
variables stated as a contract; seven consuming repositories named by their edges
rather than described.
[Source: specs/001-justfiles-baseline/plan.md -> "Scale/Scope"]
[Source: specs/001-justfiles-baseline/spec.md -> FR-004a]

## Project Structure

```text
osapi-justfiles/                 # nothing here changes
├── justfile                     # its own test recipe, resolving two ways
├── docusaurus/docusaurus.just   # 10 recipes
├── go/go.just                   # 16 recipes, one of them unprefixed
├── just/just.just               # 2 recipes, no variables
├── md/md.just                   # 2 recipes, pinning mdformat and Python
└── react/react.just             # 8 recipes

components/osapi-justfiles/
├── specs/001-justfiles-baseline/spec.md   # the statement of record
└── .specify/memory/                        # where archival puts it
```

**Structure Decision**: no corpus subject file beyond the specification, and no
skill gains a reference. No skill in the specs repository builds or formats
anything, so a citation into these recipes would be a rule invented for a reader
who does not exist.
[Source: specs/001-justfiles-baseline/plan.md -> "Structure Decision"]

## Filling a Required Section Whose Word Does Not Fit

The one decision this feature made rather than found, and the reason it is in the
plan rather than the specification.

The shape's section 4 is **"the contract"**, and `system`'s 002 wrote it
expecting a repository that exposes code. `osapi-justfiles` exposes none. Three
readings were available:

| Reading                                                       | Verdict                                                                                                                |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Omit the section under 002's FR-011 allowance                  | Rejected — records an absence that is not there, and teaches the programme that a non-Go repository has no contract     |
| Read "contract" narrowly as exported symbols, not applicable   | Rejected for the same reason, and the fifth and sixth baselines would inherit the conclusion                            |
| Read "contract" as **what a consumer may depend on**           | **Taken** — 38 recipe names and twenty variable names pass every test that matters                                     |

A consumer depends on it, renaming part of it breaks them at their next fetch,
and nothing in the repository declares it. That last part is what makes stating
it valuable rather than redundant.

**What the decision costs, stated rather than hidden**: it widens the word for
every baseline after this one, and a later reader could take "contract" to mean
any observable regularity, which would make the section unbounded. The bound that
keeps it useful is **something a consumer's build breaks on**. Whether
`global/baseline` should say so is `system`'s, because a fragment is amended in
its own change.
[Source: specs/001-justfiles-baseline/plan.md -> "The one interpretive decision"]

## The Reading Order That Keeps Prose From Becoming a Source

1. **The files first.** Each module's `.just` file for its recipes and variables,
   the root `justfile` for the self-consumption asymmetry, every consumer's
   `fetch` recipe for the edges.
2. **The counts by command**, never by reading a sentence claiming one. The recipe
   count was taken twice by different means and the results compared before
   either was written down.
3. **The prose last**, and only to find disagreements.

Reading the READMEs first would have produced a plausible inventory of what the
modules are *for* and would not have found the unprefixed `run` recipe, the
pinned-inner-floating-outer version shape, or the self-consumption asymmetry —
none of which any README mentions.
[Source: specs/001-justfiles-baseline/plan.md -> "The reading order, and why it was that order"]

## What Verification Checks, and What It Cannot

Re-running the commands checks the **counts**. It does not check the two things
most likely to be wrong, and saying so is what stops a green task list being
mistaken for a verified inventory:

- **Whether a recipe does what its name suggests.** Excluded deliberately.
- **Whether the modules are what the consumers need.** A judgement about fitness,
  not a measurement.

A third entry was going to sit here as a limit — that a variable read without an
assigned default would not appear in the variables table. **Writing it down was
enough to notice it was testable.** One command settled it: the table is
complete, and the two references it could not account for were recipe parameters,
which is how the two argument-taking recipes were found. The entry is kept in
corrected form because the mistake is the transferable part: **a limit that can
be tested is not a limit, it is a check nobody ran.** Stating it as a boundary of
what the inventory could know read as rigour and was the opposite.
[Source: specs/001-justfiles-baseline/plan.md -> "What the verification actually checks, and what it cannot"]

## Testing Strategy

`just test` in the specs repository is the gate for corpus work: mdformat over
the markdown, justfile formatting, and the skill validator. There is no code to
unit test and nothing lands in the inventoried repository, so the gate that
matters is not this one — it is whether each command beside a count still
produces the figure beside it.
[Source: specs/001-justfiles-baseline/tasks.md -> "Tests"]

The task list re-runs every one of them. That is deliberate: `gohai`'s baseline
archived with no task list and nothing was obviously lost, and this one has one
because a baseline whose counts are never re-run is a baseline nobody checked.
Three defects were found that way after the specification had merged, and none
was found by re-reading it.
[Source: specs/001-justfiles-baseline/tasks.md -> "Why this list exists at all"]

## Configuration

None. The repository has no configuration of its own; what a consumer configures
is the twenty override variables, which are the contract's second half rather
than this project's settings.
[Source: specs/001-justfiles-baseline/spec.md -> FR-013]
