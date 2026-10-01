# Implementation Plan: A baseline for gohai

**Branch**: `001-gohai-baseline` | **Date**: 2026-09-29 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/gohai/specs/001-gohai-baseline/spec.md`

## Summary

**This plan is retrospective, and written to a gate.** The inventory was
produced by reading gohai and then stated; `speckit-archive-run` requires a
`plan.md`, this feature had none because a baseline is looked-up rather than
planned, and the alternative was leaving the inventory unarchived. It guided no
work. Read it as a record of the shape the work had — the same admission
[001-provider-contract's plan](../../../osapi/specs/001-provider-contract/plan.md)
makes about itself, and consistent with the specification's own statement that
its subject is a description rather than a change.

State how gohai behaves today, so its memory stops being empty. Sixteen
requirements, every one of the form "the corpus MUST state X".

**Nothing lands in the gohai repository.** That is not a scoping preference but
what CONTRIBUTING's "Seeding a component" requires of a baseline: the
deliverable is the inventory, and it lives here.

## Technical Context

**Language/Version**: Markdown. No compiled artifact. The repository being
inventoried is Go — 314 files, 205 of them not tests — but nothing in it
changes.

**Primary Dependencies**: None. The corpus depends on nothing at runtime.

**Storage**: `components/gohai/specs/` for the specification and
`components/gohai/.specify/memory/` for what archival consolidates into. That
memory is empty before this feature, which is the condition the feature exists
to end.

**Testing**: `just test` in the specs repository — `mdformat --check`,
`just-fmt-check`, and `scripts/validate-skills.py`. There is no code to unit
test here. Separately, every count in the specification carries the shell
command that reproduces it, and re-running those four commands against gohai is
what checks the inventory rather than the formatting.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the gohai repository — `git -C gohai status` clean
is SC-005. No count stated without the command that produces it. A disagreement
between gohai's prose and its code recorded as a gap with both sides named,
never silently corrected.

**Scale/Scope**: One repository inventoried. 62 collectors stated by their
shared contract rather than individually, which is the decision FR-004 records.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | The inventory goes where a skill reads it first, and cites gohai's own catalogue rather than duplicating 62 entries. gohai's `docs/` keeps its job; this states the contract.                                                                                                                                    |
| **Verification**  | Every requirement names the file it describes and every count carries its command, which is what CONTRIBUTING requires of a baseline specifically: "so a reader re-measures rather than trusting the prose". Two disagreements were found that way.                                                              |
| **Tooling**       | Nothing new is provisioned. The Time Machine extension CONTRIBUTING selects was **not** installed: its installer needs an interactive confirmation this session cannot give and warns that it bypasses the trusted catalogues. Reading the repository is the slow path CONTRIBUTING names, not a prohibited one. |
| **Correction**    | The two gaps are recorded with both sides named. Neither was fixed here, because nothing lands in gohai; both were then corrected by gohai in its own change, `gohai#201`, which also turned up a third defect — a legend defining `✅` twice.                                                                   |
| **Workflow**      | Specify, then this plan, then archive. No `tasks.md`: there is no ordered work to break down, which is the same shape 001-provider-contract had.                                                                                                                                                                 |

**Result**: no violations.

## Project Structure

### Documentation (this feature)

```text
components/gohai/specs/001-gohai-baseline/
├── spec.md              # The inventory — 16 requirements, the deliverable
├── plan.md              # This file
└── checklists/
    └── requirements.md  # From stage 1; four items fail by design
```

No `research.md`, `data-model.md` or `contracts/`: the research *is* the
specification, there is no data model to design, and gohai's contracts are what
the specification states rather than something this feature defines.

### Content

```text
specs/                                              # this repository
└── components/gohai/
    ├── specs/001-gohai-baseline/spec.md            # the inventory
    └── .specify/memory/                            # empty; this fills it

gohai/                                              # unchanged
├── internal/collector/{collector,registry}.go      # read, not modified
├── pkg/gohai/{gohai.go,collectors/,ocsf/}          # read
└── {README.md,docs/,CONTRIBUTING.md}               # read as leads, not sources
```

**Structure Decision**: one specification, no subdivision. gohai is one library
with one contract; splitting the inventory by category would create ten
documents that each restate the same five-method interface.

## What was read, and how

The order matters, because it is what kept prose from becoming a source.

1. **The code first.** `internal/collector/collector.go` for the interface and
   the category constants, `internal/collector/registry.go` for the surface and
   the dependency handling, `pkg/gohai/gohai.go` for registration.
2. **The counts by command**, never by reading a sentence that claimed one. Four
   are stated and all four are reproducible.
3. **The prose last**, and only to find disagreements. This is the reverse of
   the tempting order, and it is why the two gaps were found rather than
   inherited: reading the README first would have produced an inventory stating
   65 and 9, both wrong, with the code never consulted.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
