# Specification Quality Checklist: Per-agent public key store

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

### The same two items fail here as in 001, for the same reason

**"No implementation details" and "No implementation details leak"**.
Requirements cite the file, advisory or type they were written from:
`internal/controller/enrollment/accept.go`, `internal/agent/heartbeat.go`,
`internal/validation/target.go`, GHSA-3jh4, GHSA-j73r. The constitution's
Verification principle requires a claim about the codebase to be measured rather
than asserted, and its Correction principle requires requirements to come from
evidence the repository already carries. Removing the citations would satisfy
the checklist and leave the spec uncheckable. The requirement text itself stays
behavioural — what must be true — and the citations sit alongside as evidence.

**"Written for non-technical stakeholders"**. The subject is how one layer of a
codebase authenticates another. The readers are contributors and agents. What an
operator needs is covered by FR-012 and FR-013, which require the fleet view and
the documentation.

Recorded rather than resolved, as in `001-provider-contract`. No iteration
attempted: each available fix removes something the constitution requires.

### Deliberate choices

- **FR-009 was a question; clarify answered it.** Enforcement is opt-in per
  side, and once on, an agent with no stored key is refused there. Recorded
  under Clarifications, applied to FR-009, with SC-007 added for the staged
  rollout.
- **FR-006 constrains targeting, not just storage.** Deterministic resolution is
  what actually closes GHSA-j73r; a store nobody consults would satisfy the
  letter of the other requirements and leave the attack open.
- **Two advisories, one spec.** Response verification and registry
  authentication need the same store, so speccing them apart would have produced
  two designs for one mechanism.
