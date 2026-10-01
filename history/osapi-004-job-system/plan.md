# Implementation Plan: The job system

**Branch**: `004-job-system` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi/specs/004-job-system/spec.md`

## Summary

The specification states 24 requirements about how work reaches an agent. This
plan says what turning them into a landed change consists of, and the answer is
mostly subtraction: roughly 430 lines leave
`docs/docs/sidebar/architecture/job-architecture.md`, the operator half stays,
and the `add-a-domain` skill's restatements of the mechanics become citation
rows.

Three of the requirements are corrections rather than statements, and they
change what the site says as well as what the corpus holds: the job key shape,
the consumer defaults and the bucket TTL. A site page left stating the old
numbers beside a corpus stating the new ones is worse than either alone.

No Go code changes. The riskiest part is not the writing — the specification is
merged — it is that this lands across two repositories and the second half is
what ends the duplication.

## Technical Context

**Language/Version**: None. Markdown in two repositories.

**Primary Dependencies**: None new. The redirects plugin that
[003's research](../003-corpus-backfill/research.md) identified belongs to the
pages `005` moves, not to this subject.

**Storage**: N/A.

**Testing**: `just test` here — mdformat, just-fmt and
`scripts/validate-skills.py`, which resolves every citation.
`just docusaurus-fmt-check` and `just docusaurus-build` in osapi, where the
build fails on a link left pointing at removed content.

**Target Platform**: The corpus and the published site.

**Project Type**: Documentation.

**Performance Goals**: N/A.

**Constraints**: `job-architecture.md` must keep its address and read as a whole
page afterwards, not as a remainder. No corpus requirement may restate what
[001](../001-provider-contract/spec.md) or [002](../002-agent-key-store/spec.md)
states. The three corrections must land in both places or neither.

**Scale/Scope**: One page split, roughly 430 lines moving and roughly 200
staying. One skill reference rewritten. Two pull requests, one per repository.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                                                                      |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | The corpus states the mechanics in full; the skill cites them; the site keeps what an operator needs and does not point them here. The three corrections exist because the same rule was stated twice and the copies disagreed — which is the failure this principle describes, caught in the act. |
| **Verification**  | Every requirement cites the file it describes, and the three gaps were found by reading those files rather than by trusting the page. `just skill-lint` is what fails when a citation stops resolving; the quickstart's checks are commands rather than instructions to look.                      |
| **Tooling**       | Nothing new is provisioned.                                                                                                                                                                                                                                                                        |
| **Correction**    | The three gaps are recorded as corrections with both sides named. FR-024 carries the obligation that the site change lands, rather than leaving the corpus and the page disagreeing — the state the correction principle calls out.                                                                |
| **Workflow**      | This is stage 3 for `004`; tasks follow in the same branch, and the implementation is its own pull request per repository.                                                                                                                                                                         |

**Result**: no violations.

## Project Structure

### Documentation (this feature)

```text
components/osapi/specs/004-job-system/
├── plan.md              # This file
├── research.md          # Phase 0: what to verify before writing, and what was found
├── data-model.md        # Phase 1: the corpus sections, and what each replaces
├── quickstart.md        # Phase 1: how to verify the move
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
specs/                                        # this repository
├── components/osapi/specs/004-job-system/
│   └── spec.md                               # merged; the statement of record
└── .claude/skills/add-a-domain/
    └── references/agent.md                   # delivery mechanics become citations

osapi/
└── docs/docs/sidebar/architecture/
    └── job-architecture.md                   # contributor half removed, operator half stays
```

**Structure Decision**: the corpus half is merged already. What remains is the
osapi half, in one pull request: the page split, the three corrected numbers,
and the citation rows. `internal/` is untouched.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
