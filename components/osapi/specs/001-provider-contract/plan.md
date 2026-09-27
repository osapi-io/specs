# Implementation Plan: Provider contract

**Branch**: `001-provider-contract` | **Date**: 2026-09-26 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/001-provider-contract/spec.md`

## Summary

**This plan is retrospective, and written to a gate.** The contract was stated
before it existed: `/speckit-archive-run` requires a `plan.md`, this feature had
none because it was specified and written rather than planned and implemented,
and the alternative was leaving the corpus unarchived. It guided no work. Read
it as a record of the shape the work had, not as a plan anybody followed — the
specification itself says the same about its own retrospective nature.

State the provider contract in the corpus, so a reader learns what a provider
must do from the corpus rather than from whichever sibling provider they opened
first. Sixteen requirements, every one of the form "the corpus MUST state X".

No Go source changes. The fourteen providers under `internal/provider/node/` and
the categorized ones beside them already conform; this documents existing
practice rather than proposing a change, which is why the work is writing and
citing rather than refactoring.

## Technical Context

**Language/Version**: Markdown. No compiled artifact.

**Primary Dependencies**: None. The corpus depends on nothing at runtime.

**Storage**: The corpus itself — `components/osapi/specs/` for the
specification, `.specify/memory/` for what archival consolidates into, and
`.claude/skills/add-a-domain/references/` for the skill that cites it.

**Testing**: `just test` in the specs repository: `mdformat --check` over the
markdown, `just-fmt-check`, and `scripts/validate-skills.py` for every
`SKILL.md` and the relative links in its references. There is no code to unit
test, so link resolution and formatting are the whole gate.

**Target Platform**: Not applicable. The readers are contributors and agents.

**Project Type**: Documentation. No dependencies, no modules, no configuration,
no routing — stated plainly because a plan that leaves those sections looking
unfilled reads as an oversight rather than a fact about the work.

**Performance Goals**: Not applicable.

**Constraints**: A rule lives in exactly one place. FR-016 exists to enforce
that: the skill cites the requirement rather than restating it, because two
copies drift and the copy an agent happened to load wins.

**Scale/Scope**: Sixteen requirements covering one layer of one repository.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                                                                         | Assessment                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** — a repository states in full the conventions binding it        | This feature is that principle applied to one layer. **Pass.**                                                                                                                                                                        |
| **Verification** — a claim is measured, not inspected                             | Each requirement cites the file and symbol it describes, so a reader checks the rule against the code rather than taking the corpus on trust. `just test` measures format and links. **Pass.**                                        |
| **Tooling** — a tool a repository invokes is declared where it declares its tools | No new tool. mdformat and the skill validator are already declared. **Pass.**                                                                                                                                                         |
| **Correction** — when applying a rule shows the rule is wrong, fix the rule first | Writing this spec found two errors in the skill it documents — a provider package that does not exist, and two helpers attributed to the wrong package — and both were corrected in the skill before the spec was finished. **Pass.** |
| **Workflow** — design output goes where the workflow reads it                     | The specification lives in the feature directory and consolidates into `.specify/memory/` on archive; the skill cites it from there. **Pass.**                                                                                        |

No violations. Complexity Tracking is therefore empty and omitted.

## Project Structure

### Documentation (this feature)

```text
specs/001-provider-contract/
├── plan.md              # This file
├── spec.md              # The sixteen requirements and their evidence
└── checklists/
    └── requirements.md  # From /speckit-specify
```

No `research.md`, `data-model.md` or `contracts/`. There was nothing to
research: the contract was read out of the code that already implements it.
There are no entities beyond the ones the spec names, and the corpus exposes no
interface to contract.

No `quickstart.md` either, and that is the honest answer rather than an
omission: a corpus statement is validated by a reader following it, not by a
command that can be run. What stands in for it is the gate — `just test` — plus
the requirement that every rule cite the code it describes, so the two can be
compared.

### Source Code (repository root)

```text
components/osapi/specs/001-provider-contract/spec.md    the contract
components/osapi/.specify/memory/spec.md                where archival puts it
.claude/skills/add-a-domain/references/provider.md      cites it, per FR-016
```

**Structure Decision**: The rule lives in the corpus and the skill points at it.
FR-016 makes that direction binding rather than conventional, so the skill
reference carries a table mapping each rule to its requirement number and holds
only what the specification does not: where a provider's files go, what they are
called, and the scaffolding to start from.
