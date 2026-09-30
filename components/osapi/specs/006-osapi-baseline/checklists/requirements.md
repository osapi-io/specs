# Specification Quality Checklist: A baseline for osapi

**Purpose**: Validate specification completeness and quality before proceeding
to planning

**Created**: 2026-09-29

**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

## Notes

Four items fail by design, the same four gohai's baseline failed and for the
same reason: a baseline's subject *is* the implementation. An inventory that
named no files would be unfalsifiable, and CONTRIBUTING's "Seeding a component"
goes further than the Verification principle here — it requires the command that
re-measures each count, so a reader re-measures rather than trusting the prose.
Removing those to pass these boxes would remove the only thing that makes the
inventory worth more than osapi's README.

## What the verification found

**Three contributor pages survived the corpus backfill**, and finding them is
the argument for baselining a repository that already has memory.

| Page                            | Lines | Corpus counterpart                              |
| ------------------------------- | ----- | ----------------------------------------------- |
| `architecture/ui.md`            | 264   | **none**                                        |
| `development/ui-development.md` | 200   | **none**                                        |
| `sdk/guidelines.md`             | 227   | partial — its rules are 005's FR-019 and FR-020 |

464 lines of contributor architecture sit on an operator's site with nowhere to
cite. They survived because 003 named six candidate pages and classified those;
these three were never candidates, so nothing examined them. An inventory that
only re-checked 003's six would have missed them exactly as 003 did.

`sdk/guidelines.md` is the interesting case and FR-015 separates it: its rules
are already stated in the corpus and the page cites them, then demonstrates them
with worked examples. **Showing a rule working is not stating it twice.** What
it holds beyond demonstration is the part with no counterpart.

## Two numbers that needed saying rather than stating

**219 against 221.** 219 are published site pages under `docs/docs/`; 221 adds
`docs/README.md` and `docs/SUPPORT.md`, which are the Docusaurus project's own
files. `system`'s 002 records osapi at 221 and this classification covers 219.
Both are right about different things, which is precisely the collision that
analyze pass caught in 002 — and it recurred here in a different form on the
first baseline written after it.

**The classification's arithmetic was wrong on the first attempt.** The table
summed to 217 against a measured 219, because `usage/configuration.md` and
`intro.md` sit outside the subdirectory counts. Corrected before this was
committed; the sum now reconciles against every directory count.

## What this feature does not do

It classifies; it moves nothing. 002's FR-026 puts the baseline before the move
and its FR-027 makes the move its own feature — which is the ordering osapi
itself got wrong the first time, when three features relocated documentation and
none of them wrote the document that says which pages are contributor-facing.
