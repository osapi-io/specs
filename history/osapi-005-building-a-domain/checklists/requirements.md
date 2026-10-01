# Specification Quality Checklist: Building a domain

**Purpose**: Validate specification completeness and quality before proceeding
to planning

**Created**: 2026-09-28

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
- [x] Success criteria are technology-agnostic (no implementation details)
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

Three items fail by design, the same three that failed for
[001](../../001-provider-contract/checklists/requirements.md) and
[004](../../004-job-system/checklists/requirements.md). The reason is the same
and it is worth restating rather than cross-referencing, because a reader who
finds three unchecked boxes should not have to open another feature to learn
whether this one is unfinished.

**No implementation details** and **no implementation details leak** both fail
because this specification's subject *is* the implementation. A requirement
saying "the corpus MUST state that the `JobClient` interface has four generic
methods" cannot avoid naming the interface: the thing being specified is a
statement about code, and a statement about code that names no code cannot be
checked. The constitution's Verification principle requires the evidence, and
every requirement here carries a file and usually a line number so a reader
re-measures rather than trusting the prose. Removing the citations to pass this
box would remove the only thing that makes the requirements falsifiable.

**Written for non-technical stakeholders** fails because the audience is a
contributor adding a domain to osapi, or an agent doing the same. There is no
non-technical reader of a document whose purpose is to tell somebody which file
to create third. The operator-facing half of this material stays on the site,
which is where the non-technical reader is served — that is FR-026, and the
split between the two audiences is the feature.

These three are left unchecked rather than removed. A checklist that passes
because its failing items were deleted records nothing.

## What the verification actually found

Four gaps, recorded in the requirements rather than corrected:

| Gap                                                         | Requirement | Both sides                                                                                                                 |
| ----------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------- |
| `node.validateHostname()` does not exist as a shared helper | FR-012      | The page names that call; the function is unexported and duplicated in three packages. `validation.Var` is what is shared. |
| The `sdk-standards` capability is not in this repository    | FR-019      | The page and `references/sdk.md:6` both defer to it as binding; nothing has written it.                                    |
| 003 records five API guidelines                             | FR-014      | The page states six. The sixth is path-versus-query parameters.                                                            |
| 003 records five design principles                          | FR-022      | The page states eight. The three unnamed are Reliability and Stability, CLI Parity with API, Least Privilege Mode.         |

The first two are osapi's or this repository's to fix and each is its own
change. The last two are 003's own record being wrong about a page it measured
correctly — 46 lines, eight principles — which is the same shape as 004's
Finding 2 and the reason 003's FR-009 requires checking rather than
transcribing.
