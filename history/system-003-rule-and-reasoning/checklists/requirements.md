# Specification Quality Checklist: A rule and the reason for it live in different places

**Purpose**: Validate specification completeness and quality before proceeding
to planning

**Created**: 2026-09-30

**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
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
- [x] No implementation details leak into specification

## Notes

**Two items pass differently than their wording suggests**, which is how every
feature in this repository passes them. The requirements name files, fragments
and advisory identifiers, because `global/verification` requires evidence a
reader can re-measure and this feature's subject is where statements live. The
stakeholder is a contributor to any of the six repositories.

**SC-003 is the criterion that matters and the weakest to write.** It asks a
reader given only the fragment to sort ten rules and say where each goes. That
tests whether the test in FR-007 is usable by somebody who was not present for
the argument, which is the whole point of writing it into a fragment rather than
a feature. It cannot be automated and it is the only check that would catch a
resolution that reads well and does not discriminate.

**FR-017 records a gap this feature cannot close.** Nothing will check that a
rule in memory is also stated in its repository, because deciding which
statements are rules is the judgement FR-007 exists to make. The honest position
is in the requirement: this one may not be automatable, and saying so beats
inventing a checker that passes by counting something else.

**One requirement is about a merged specification being wrong.** FR-013 says
osapi's 005 FR-026 required removing the only place a contributor could read
rules the corpus then held alone. The specification is not amended, because it
records what was decided; the repository gains the eight statements instead.
That distinction is deliberate and is the Correction principle rather than an
exception to it.
