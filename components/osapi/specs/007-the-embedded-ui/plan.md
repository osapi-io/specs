# Implementation Plan: The embedded UI

**Branch**: `007-the-embedded-ui` | **Date**: 2026-09-29 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi/specs/007-the-embedded-ui/spec.md`

## Summary

The specification states 17 requirements about the embedded UI. Turning them
into landed work is mostly subtraction across three files, and the plan's job is
to fix the boundaries so the split is reviewable rather than decided in a diff.

One correction to the specification's own estimate: it says "roughly 60 lines
stay of 264". Measured against the headings, **80 stay and 184 move**. The
estimate was made before the ranges were counted; the ranges are below and
reconcile to 264.

This is the same two-repository sequence the backfill established — corpus
first, then osapi — with one difference that makes the order matter more than
usual. Two prose documents state this architecture today and they have diverged.
Relocating only the site page would leave the other as the sole statement, and
it is the one missing two sections.

No Go code changes. `ui/` is touched only for the documentation file it carries.

## Technical Context

**Language/Version**: None. Markdown in two repositories.

**Primary Dependencies**: None new.

**Storage**: N/A.

**Testing**: `just test` here — mdformat, just-fmt,
`scripts/validate-skills.py`. `just docusaurus-fmt-check` and
`just docusaurus-build` in osapi, where the build fails on a link left pointing
at removed content. Neither checks whether the split left a coherent page; that
is review.

**Target Platform**: The corpus, the published site, and one file beside the
code.

**Project Type**: Documentation.

**Constraints**: `architecture/ui.md` keeps its address and must read as an
operator's page afterwards, not as a remainder. `ui/docs/architecture.md` keeps
its address as a pointer — FR-016, and the one file in the programme that
survives beside the code. No requirement may restate what
[001](../001-provider-contract/spec.md), [004](../004-job-system/spec.md) or
[005](../005-building-a-domain/spec.md) already states, and the UI's permission
model cites rather than repeats osapi's.

**Scale/Scope**: Three files. 184 lines move from one, 200 from another, 263 are
replaced by a pointer. One corpus statement. Two pull requests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | This is the principle the feature serves, in its sharpest form yet: the same architecture is stated in two prose documents that have diverged. One statement, and citations, is the whole deliverable.                                                                    |
| **Verification**  | Every requirement cites the file it describes. Two came from reading the code rather than either page — the client-side decode without verification, and `/ui/` sitting in `.coverignore` — and a reader who trusted the prose would have had neither.                    |
| **Tooling**       | Nothing provisioned. FR-009 deliberately does not transcribe commands, because a rule a tool enforces is not restated as prose.                                                                                                                                           |
| **Correction**    | The divergence is recorded with what each copy held and when each was touched, rather than merged away. FR-012 takes the union rather than choosing a winner, and FR-013 says the shared differences were punctuation so nobody looks for a decision that was never made. |
| **Workflow**      | Stage 3 for `007`; tasks follow in the same branch, then one pull request per repository.                                                                                                                                                                                 |

**Result**: no violations.

## Project Structure

### Documentation (this feature)

```text
components/osapi/specs/007-the-embedded-ui/
├── spec.md              # merged; 17 requirements
├── plan.md              # This file
├── research.md          # Phase 0: the four decisions the spec left open
├── data-model.md        # Phase 1: every line range, and what replaces it
├── quickstart.md        # Phase 1: how to verify the move
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
specs/                                        # this repository
└── components/osapi/specs/007-the-embedded-ui/
    └── spec.md                               # the statement of record

osapi/
├── docs/docs/sidebar/
│   ├── architecture/ui.md                    # 264 -> 80, operator's half
│   └── development/ui-development.md         # 200 -> a short index
└── ui/docs/architecture.md                   # 263 -> a pointer
```

**Structure Decision**: no new corpus subject file. The statement is `spec.md`,
archived into memory like every other feature's. The `add-a-domain` skill gains
nothing — FR-017, because a domain's UI work is not part of adding a domain
today.

## The split, by line range

`architecture/ui.md`, 264 lines, measured against its headings on `0cca62060`.
Ranges are given so a reviewer checks the boundary rather than reconstructing it
— the lesson from Subject A, whose split was correct and whose boundaries had to
be inferred.

| Lines   | Section                                      | Disposition                                                                 |
| ------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| 1–11    | Frontmatter, title, introduction             | **Stays**, with one sentence of editing so it introduces an operator's page |
| 12–53   | `## Embedding Mechanism`                     | Moves — FR-006                                                              |
| 54–68   | `## Configuration`                           | **Stays** — FR-002, the one rule here an operator acts on                   |
| 69–102  | `## Application Structure`                   | Moves — FR-004                                                              |
| 103–114 | `## Tech Stack`                              | Moves — FR-003                                                              |
| 115–153 | `## Component Architecture`                  | Moves — FR-004                                                              |
| 154–159 | `## Authentication & Authorization`, opening | **Stays** — names the shared JWT, which an operator needs                   |
| 160–175 | `### Auth flow`                              | Moves — FR-007                                                              |
| 176–190 | `### RBAC model`                             | **Stays** — three roles and their permissions, which an operator configures |
| 191–231 | `## SDK Generation`, `### Fetch mutator`     | Moves — FR-005                                                              |
| 232–264 | `## Pages` and its five subsections          | **Stays** — what each screen shows                                          |

**80 stay, 184 move**, and 80 + 184 = 264.

Removing 160–175 leaves the authentication opening running straight into the
RBAC model, which reads. Removing 191–231 leaves the RBAC model followed by
`## Pages`, which also reads. The only edit the surviving page needs beyond
deletion is its introduction, which currently introduces a contributor's
document.

`development/ui-development.md` moves entire, all 200 lines, leaving a short
index — the shape `adding-an-api-domain.md` took.

`ui/docs/architecture.md` is replaced by a pointer of under ten lines. Its 263
lines are not moved twice: everything it holds is either in the site page's
moving half or is `Feature flags`, which FR-012 carries forward from this copy
specifically.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
