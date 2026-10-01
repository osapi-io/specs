# Implementation Plan: A baseline for osapi-orchestrator

**Branch**: `001-orchestrator-baseline` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

## Summary

State what `osapi-orchestrator` is. Twenty requirements, and the last of the six
components to get a baseline.

It is the first baseline written after memory stopped being a requirements list.
`global/baseline` now says memory is documentation, so this feature's archival
writes prose under seven headings rather than labelled obligations, and the five
memories written before it were converted rather than left as the odd ones out.

**Nothing lands in the `osapi-orchestrator` repository.**

## Technical Context

**Language/Version**: Markdown here. The repository inventoried is Go, 81 files,
59 not tests, `go 1.26.0`.

**Primary Dependencies**: None for the corpus. The repository depends on osapi.

**Storage**: `components/osapi-orchestrator/specs/` for this feature, and
`.specify/memory/` for what archival consolidates into. That memory holds only a
constitution, so the archival seeds rather than folds.

**Testing**: `just test`, which now includes `memory-check` running every count
in every memory against its command. That gate did not exist when the first five
baselines were written.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the inventoried repository. Every command in a
measurement table must stand alone, because `memory-check` runs it in isolation
and cannot resolve "the same, plus X" against the row above.

**Scale/Scope**: The largest documentation set in the organization, 140 pages
against 81 Go files, and the only one whose coverage reconciles.

## Constitution Check

| Principle         | How this feature satisfies it                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | The 101 operation pages are cited rather than copied; the contract they share is stated once.                                          |
| **Verification**  | Fourteen counts with standalone commands, and the documentation mapping checked by iterating headings in both directions.              |
| **Tooling**       | Nothing provisioned.                                                                                                                   |
| **Correction**    | Three gaps with owners, none corrected. FR-018 records that the best documentation coverage in the organization has no gate behind it. |
| **Workflow**      | Stages 1 to 4 in one branch.                                                                                                           |
| **Baseline**      | The first written under the fragment's documentation rule rather than converted into it afterwards.                                    |
| **Repositories**  | The single edge verified from both ends.                                                                                               |
| **Tracking**      | Nothing becomes an issue.                                                                                                              |

**Result**: no violations.

## The measurement that needed care

`grep -cE '^func \(o \*Orchestrator\) [A-Z].*\) \*Step \{$'` returns **2**, not
101, because most signatures in `ops.go` span three lines and the return type
sits on its own. A count taken that way and written down would have been wrong
by two orders of magnitude and would have read as precise.

`grep -cE '^func \(o \*Orchestrator\) [A-Z]' pkg/orchestrator/ops.go` returns
101 and is what the specification carries. `grep -c ') \*Step {'` also returns
101, which is the second measurement that makes the first trustworthy.

## What the reconciliation actually checked

125 pages under `docs/operations/` and 101 operation methods. Those numbers do
not match, and the 24 directory indexes are the difference.

Comparing 101 against 101 would prove nothing about whether they are the same
101, so the check iterates: for every page, take its `H1` and grep `ops.go` for
a method of that name; then for every method, grep the pages for an `H1`
matching it. Zero orphans in either direction.

This is the first documentation set in the programme to reconcile. Three
baselines before it found prose disagreeing with code.

## What the verification cannot check

- **Whether the 101 operations are the right 101.** A judgement.
- **Whether the guard vocabulary is right.** Eight guards and ten predicates
  exist; whether they are the right eight and ten is a judgement.
- **Whether the mapping stays one to one.** It holds today and nothing enforces
  it. FR-018 records that as a gap rather than as reassurance.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
