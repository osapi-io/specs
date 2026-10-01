# Implementation Plan: Building a domain

**Branch**: `005-building-a-domain` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi/specs/005-building-a-domain/spec.md`

## Summary

The specification states 26 requirements about what adding an API domain
consists of. This plan says what turning them into a landed change is, and it is
larger than Subject A: four pages are affected instead of one, two of them are
deleted outright, and 654 of the lines leaving the site come from a single page
that is the most-read contributor document osapi has.

The shape is the same as [004](../004-job-system/plan.md) — the corpus statement
merges first, the site reduction second, archival last — and the reason to keep
that order is stated below rather than assumed, because reversing it is the one
sequencing mistake that leaves the duplication live.

What is different from Subject A is the amount of *subtraction with no
replacement*. `job-architecture.md` kept an operator half. `api-guidelines.md`
and `principles.md` have no operator half at all: every line of both is
contributor knowledge, so both addresses become redirects and the pages cease to
exist. That is the first time this backfill deletes a page rather than splitting
one, and it is why the redirects matter more here than anywhere else in 003.

No Go code changes. Five gaps are recorded and none is scheduled — see **Out of
scope**.

## Technical Context

**Language/Version**: None. Markdown in two repositories.

**Primary Dependencies**: `@docusaurus/plugin-client-redirects`, added **by this
feature**. It is [003's T015](../003-corpus-backfill/tasks.md), which 005
carries out along with the rest of 003's Phase 4 — so it is this feature's own
work rather than a dependency to wait on. 005 is the only subject in the
backfill that deletes a page, and therefore the only one that needs a redirect.

**Storage**: N/A.

**Testing**: `just test` here — mdformat, just-fmt and
`scripts/validate-skills.py`, which resolves every citation and fails by name on
a wrong relative depth. `just docusaurus-fmt-check` and `just docusaurus-build`
in osapi; the build fails on a link left pointing at a deleted page, which is
the gate that catches the Further Reading list described in
[data-model.md](data-model.md).

**Target Platform**: The corpus and the published site.

**Project Type**: Documentation.

**Performance Goals**: N/A.

**Constraints**: `adding-an-api-domain.md` and `system-architecture.md` keep
their addresses and must read as whole pages afterwards rather than as
remainders. `api-guidelines.md` and `principles.md` lose their content entirely
and keep their addresses only as redirects. No corpus requirement may restate
what [001](../001-provider-contract/spec.md),
[002](../002-agent-key-store/spec.md) or [004](../004-job-system/spec.md) states
— FR-002 and FR-003.

**Scale/Scope**: Four pages. 654 lines removed and replaced by a short page, 61
and 46 lines deleted, and 189 lines removed from a 330-line page. One skill
reference rewritten. Two pull requests, one per repository.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | The corpus states the rules; the skill cites them; the site keeps only what an operator uses. Two pages had no operator content at all, which is the clearest case this principle has produced: a page nobody but a contributor reads, sitting in the operator's navigation.                                     |
| **Verification**  | Every requirement cites the file it describes, and four of them cite a line number. The four gaps were found by reading the code behind the page rather than the page — `validateHostname` is the example: the page names a call that does not compile. `just skill-lint` fails when a citation stops resolving. |
| **Tooling**       | Nothing new is provisioned. The redirects plugin arrives through 003's own task list.                                                                                                                                                                                                                            |
| **Correction**    | Four gaps are recorded with both sides named and none is silently fixed. Two of them are 003's own record being wrong about pages it measured correctly, which this plan states plainly rather than quietly reconciling.                                                                                         |
| **Workflow**      | This is stage 3 for `005`; tasks follow in the same branch, the implementation is its own pull request per repository, and archival comes after the implementation has merged.                                                                                                                                   |

**Result**: no violations.

## Project Structure

### Documentation (this feature)

```text
components/osapi/specs/005-building-a-domain/
├── plan.md              # This file
├── research.md          # Phase 0: what the sequencing and layout decisions are, and why
├── data-model.md        # Phase 1: every page, by line range, and what replaces it
├── contracts/
│   └── walkthrough.md   # Phase 1: what a walkthrough is, and how it differs from a requirement
├── quickstart.md        # Phase 1: how to verify the move
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
specs/                                        # this repository
├── components/osapi/specs/005-building-a-domain/
│   ├── spec.md                               # merged; the statement of record
│   └── data-model.md                         # holds the walkthrough FR-005 requires
└── .claude/skills/add-a-domain/
    ├── references/provider.md                # already cites 001; unchanged
    ├── references/sdk.md                     # the sdk-standards deferral is named, not repeated
    └── references/*.md                       # domain-building mechanics become citation rows

osapi/
└── docs/docs/sidebar/
    ├── development/adding-an-api-domain.md   # 654 lines → a short contributor page
    └── architecture/
        ├── api-guidelines.md                 # deleted; address redirects
        ├── principles.md                     # deleted; address redirects
        └── system-architecture.md            # contributor half removed, operator half stays
```

**Structure Decision**: two pull requests, and the corpus one goes first. See
[research.md](research.md) Decision 1 for why the reverse order is the failure
mode rather than merely slower.

## Documentation Surface

Subject A's plan introduced this section because a documentation feature's
surface *is* its deliverable, and leaving it implied is how a page gets split by
judgement at implementation time. Here it matters more, because two pages are
deleted and the split of a third is a line-range decision that a reviewer should
be able to check rather than trust.

| Page                                  | Today                        | After                                                                                 | Reader afterwards                                                          |
| ------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `development/adding-an-api-domain.md` | 654 lines, the whole subject | A short page: what adding a domain involves, a citation table, a pointer to the skill | A contributor, who is the one reader for whom a citation is the right form |
| `architecture/api-guidelines.md`      | 61 lines, six guidelines     | Deleted. Address redirects to the contributor page                                    | Nobody; it had no operator content                                         |
| `architecture/principles.md`          | 46 lines, eight principles   | Deleted. Address redirects to the contributor page                                    | Nobody; same                                                               |
| `architecture/system-architecture.md` | 330 lines                    | 141 lines: health checks, security, external dependencies                             | An operator configuring and calling osapi                                  |

The exact line ranges are in [data-model.md](data-model.md). The contributor
page's contents are specified there too, concretely enough that implementation
has nothing left to invent — which is the point of writing it here rather than
discovering it in a diff.

## Out of scope

Five gaps are recorded in the specification. None is scheduled by this plan, and
each has an owner:

| Gap                                                    | Owner           | Why not here                                                                                                          |
| ------------------------------------------------------ | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `validateHostname` unexported and triplicated (FR-012) | osapi           | A Go change. This feature touches no code.                                                                            |
| The absent `sdk-standards` capability (FR-019)         | this repository | Writing it is a feature of its own, and inventing it inside a backfill is how a rule gets written to fill a template. |
| Step 8's commands do not cover Step 7's files (FR-024) | osapi           | A justfile or page change in osapi.                                                                                   |
| 003 records five API guidelines; six exist (FR-014)    | 003             | Its record, not this feature's. Corrected when 003 is archived.                                                       |
| 003 records five principles; eight exist (FR-022)      | 003             | Same.                                                                                                                 |

Also out of scope: the 30 feature pages, any Go code change, the Docusaurus
theme beyond the two redirects, and Subject A's job system material, which is
archived.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
