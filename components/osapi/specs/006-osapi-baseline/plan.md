# Implementation Plan: A baseline for osapi

**Branch**: `006-osapi-baseline` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi/specs/006-osapi-baseline/spec.md`

## Summary

State what osapi is, so its memory stops holding 1,840 lines about decisions and
nothing about the repository they were decided for. Twenty-one requirements,
every one of the form "the corpus MUST state X", plus a classification of all
219 site pages.

**This plan is retrospective, and it is late.** The specification merged as
specs#169 and no plan followed, which left the feature stalled at stage 1: the
archival gate requires a `plan.md`, so osapi's baseline could not be archived
and its memory could not receive the frame the specification wrote. Five
features were archived into that memory before this one and a sixth — the
embedded UI — was archived *ahead* of it, out of the ascending order archival
expects, because this file did not exist.

That is worth recording rather than quietly fixing. The specification is the one
artifact that says what osapi is, and it sat unarchivable for a day because the
stage that produces this file was skipped. `gohai`'s baseline made the same
admission about being written to a gate; this one adds that a baseline with no
plan is not merely undocumented, it is **unarchivable**, and nothing in the
workflow says so out loud.

**Nothing lands in the osapi repository.** That is what CONTRIBUTING's "Seeding
a component" requires of a baseline: the deliverable is the inventory, and it
lives here. The moves the inventory *found* are separate features — `007` did
two of the three pages and the third is still open.

## Technical Context

**Language/Version**: Markdown. The repository being inventoried is Go — 2,739
files, 1,814 of them not tests — with a TypeScript single-page application under
`ui/`. Nothing in either changes.

**Primary Dependencies**: None. The corpus depends on nothing at runtime.

**Storage**: `components/osapi/specs/` for the specification and
`components/osapi/.specify/memory/` for what archival consolidates into. That
memory is **not** empty — it holds 1,840 lines from five archived features,
which is the condition this feature exists to complete rather than to create.

**Testing**: `just test` in the specs repository — mdformat, just-fmt and
`scripts/validate-skills.py`. There is no code to unit test. Separately, every
count in the specification carries the command that reproduces it, and
re-running those seven commands against osapi is what checks the inventory. The
formatting gate cannot tell a right count from a wrong one.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the osapi repository. **Section 4 must be mostly
citation**: osapi's contract is already stated across four archived features,
and restating any of it would be the second statement the whole programme exists
to end. No count without its command. Every disagreement between osapi's prose
and its code recorded as a gap with both sides named and an owner.

**Scale/Scope**: One repository inventoried, the largest in the organization.
219 site pages classified individually; 24 API domains, 6 provider categories
and 117 SDK methods stated by their shared contract rather than enumerated.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | Section 4 cites the four archived features rather than restating them, and says so. The classification names which pages hold contributor knowledge, which is what makes the one-statement rule checkable for this repository.                  |
| **Verification**  | Seven counts, each with its command. Two differ by a **definition** rather than a measurement — 219 site pages against 221 files under `docs/` — and FR-013 states what each counts, because a reader given one will think the other is broken. |
| **Tooling**       | Nothing provisioned.                                                                                                                                                                                                                            |
| **Correction**    | Four gaps recorded with owners, none corrected here. FR-016 records that the finding changes the programme's arithmetic and says 002 is amended in its own change rather than this one.                                                         |
| **Workflow**      | Stages 3 and 4, written after stage 1 merged — late, and the Summary says how late and what it cost.                                                                                                                                            |
| **Baseline**      | This is the feature the fragment describes: memory that answers what was decided and never what the thing is. The fragment's own example is osapi's 1,840 lines.                                                                                |
| **Repositories**  | The dependency edges are stated from `go.mod` and the justfiles rather than from a list, and this baseline states only its own — the map is `system`'s.                                                                                         |
| **Tracking**      | Nothing here becomes an issue. The three surviving contributor pages became `007` and the `sdk/guidelines.md` remainder, which are features rather than issues.                                                                                 |

**Result**: no violations.

## What a baseline for the hub has to do differently

osapi is not the first baseline written but it is the first one *required* by
the others: every other component's section 2 states its edges against osapi's,
so this document is read while reading five others. Three consequences shaped
the specification and are recorded here rather than left to the next reader to
infer.

**Section 4 is mostly citation, and that is the point.** Four archived features
already state osapi's contract — the provider contract, the agent key store, the
job system, building a domain. A baseline restating any of it would create the
second statement the programme exists to end, so section 4 names where each part
of the contract lives and states only what none of them states. This is the
opposite of every other baseline, where section 4 is the substantive part.

**The counts differ by definition, not by error.** 219 and 221 are both right,
about different questions: 219 published pages under `docs/docs/`, and 221
adding the Docusaurus project's own `README.md` and `SUPPORT.md`. A baseline
that stated one number would leave a reader comparing it against the other and
concluding one of them was broken. `system`'s 002 had recorded 221 as the page
count, which is why FR-013 states both and 002 was amended.

**Classifying 219 pages is the work, not a by-product.** 002's FR-025 makes the
classification precede the move, and osapi is the repository where that ordering
was got wrong the first time: the corpus backfill moved documentation across
three features and none of them wrote the document saying which pages are
contributor-facing. The three pages that survived are what that omission cost.

## Project Structure

### Documentation (this feature)

```text
components/osapi/specs/006-osapi-baseline/
├── spec.md              # merged at specs#169; 21 requirements, 7 outcomes
├── plan.md              # This file, written 2026-09-30
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
components/osapi/
├── specs/006-osapi-baseline/spec.md   # the statement of record
└── .specify/memory/                    # 1,840 lines from six archived features
    ├── constitution.md                 # composed; eight fragments
    ├── spec.md                         # gains sections 1, 2, 3 and the classification
    ├── plan.md                         # gains the repository's own frame
    └── changelog.md
```

**Structure Decision**: no corpus subject file beyond `spec.md`, and no skill
gains a reference. A baseline is what a reader reads first, not a rule a skill
cites; the rules it points at are already cited by the features that state them.

## What the verification checks, and what it cannot

The seven commands check the **counts**. Three things they do not check, stated
so a green task list is not mistaken for a verified inventory:

- **Whether the classification of 219 pages is right page by page.** It was made
  by reading each page's subject; re-running it means reading them again, which
  is a review rather than a measurement. What *is* checkable is that the
  classification sums to 219 and that every page appears exactly once — and it
  did not, on the first attempt: the sum came to 217 because two pages sit
  outside the subdirectory counts.
- **Whether section 4's citations are complete.** A rule of osapi's contract
  that none of the four archived features states would not appear as a gap,
  because nothing would point at its absence.
- **Whether the architecture survives a rename**, which is what US2 asks. That
  is a judgement about the level of statement, and only re-reading it after a
  refactor settles it.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
