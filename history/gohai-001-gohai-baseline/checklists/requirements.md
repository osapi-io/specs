# Specification Quality Checklist: A baseline for gohai

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

Four items fail by design, and for a baselining feature the reason is sharper
than it was for osapi's five features: **the subject of this specification is
the implementation.** An inventory of how a repository behaves cannot avoid
naming the repository's files, and one that did would be unfalsifiable — a
reader could not check a single claim.

The constitution's Verification principle requires the evidence, and
CONTRIBUTING's "Seeding a component" goes further for a baseline: "State how
each requirement was checked, and give the command that checks it again, so a
reader re-measures rather than trusting the prose." Every requirement here
carries a file path, and every count carries a shell command. Removing them to
pass these boxes would remove the only thing that makes the inventory worth more
than gohai's README — which is precisely the document whose two wrong numbers
this feature found.

**Success criteria are technology-agnostic** fails for the same reason: SC-002
names four counts and the commands that reproduce them, and SC-005 asserts a
clean `git status`. Both are technology-specific and both are the point.

**Written for non-technical stakeholders** fails because the audience is a
consumer of a Go library or a contributor to it. There is no non-technical
reader of a document whose purpose is to state a five-method interface.

The four are left unchecked rather than removed. A checklist that passes because
its failing items were deleted records nothing.

## What the verification found

Two disagreements between gohai's prose and its code, recorded in FR-014 and
FR-015 rather than corrected:

| Claim                                                              | Code                       | Kind                                                                                                                                                                   |
| ------------------------------------------------------------------ | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "65 collectors" (`README.md:111`, and 65 rows in the catalogue)    | 62 packages                | A **definition**: the catalogue has an `Implemented` column, and three rows — `rackspace`, `softlayer`, `eucalyptus` — are marked `🪦`. 65 catalogued, 62 implemented. |
| "9 categories" (`README.md:111` and `docs/collectors/README.md:3`) | 10 declared, all 10 in use | An **error**. There is no reading on which nine is right.                                                                                                              |

The first is why a baseline states what a number counts rather than just the
number. The second is why CONTRIBUTING calls prose a lead rather than a source —
and it is the same failure shape the osapi backfill hit three times.

Correcting gohai's prose is not this feature's work: nothing lands in that
repository. It belongs to gohai in its own change.
