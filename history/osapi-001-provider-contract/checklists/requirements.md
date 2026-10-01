# Specification Quality Checklist: Provider contract

**Purpose**: Validate specification completeness and quality before proceeding
to planning **Created**: 2026-09-17 **Feature**: [spec.md](../spec.md)

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

- Items marked incomplete require spec updates before `/speckit-clarify` or
  `/speckit-plan`

### Two items fail by design, and iterating would make the spec worse

**"No implementation details" and "No implementation details leak"**. Every
requirement cites the file, interface or advisory it was written from:
`internal/provider/errors.go:28`, `internal/provider/facts.go:64`,
GHSA-7fjw-v3g9-326g. The constitution's Verification principle requires a claim
about the codebase to be measured rather than asserted, and its Correction
principle requires a requirement to be written from evidence the repository
already carries. Removing the citations would satisfy the checklist and destroy
the spec's only means of being checked. The requirement text itself stays
behavioural — what a provider must do — and the paths appear as evidence, never
as instructions.

**"Written for non-technical stakeholders"**. The subject is how one layer of a
codebase behaves, and the readers are contributors and agents adding a provider.
There is no non-technical audience for it. What a domain does for an operator
stays in the published documentation, which is stated in Assumptions.

Both deviations are consequences of the checklist being written for
product-feature specs, applied here to a retrospective specification of existing
behaviour. Recorded rather than resolved; no iteration attempted, because each
available fix removes something the constitution requires.

### Deliberate wording choices

- **SC-003** names `add-a-domain`, a repository artifact rather than a
  technology. The spec exists partly so that skill can stop restating mechanics,
  so the outcome is only measurable by naming it.
- **FR-011** and **FR-013** state rules the code does not fully meet yet, with
  the open gaps named in Assumptions. A requirement the code fails is a gap in
  the code; writing the requirement to match current behaviour instead would be
  the inverse of the Correction principle.
