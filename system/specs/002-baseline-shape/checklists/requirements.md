# Specification Quality Checklist: One shape for every component baseline

**Purpose**: Validate specification completeness and quality before proceeding
to planning

**Created**: 2026-09-29

**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
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
- [ ] No implementation details leak into specification

## Notes

Only two items fail here, against four in every other feature in this
repository, and the difference is worth noting: this specification's subject is
a **document shape** rather than a codebase, so it is genuinely readable by a
non-technical stakeholder and its success criteria are genuinely
technology-agnostic. Those two items pass honestly.

The two that fail are the implementation-detail pair. This specification names
file paths — `global/workflow`, `.specify/memory/`, `osapi-justfiles` — and
repository counts, because the Verification principle requires the evidence and
because a shape defined without naming what it must fit would be untestable.
FR-011 through FR-013 exist precisely because one of the six repositories has no
Go code, and that requirement cannot be stated without naming it.

## The correction this feature carries

**gohai's baseline excluded architecture on purpose, and that was wrong.** Its
FR-016 stated the exclusion plainly, which is the only reason this was findable
rather than having to be inferred from a thin document. FR-003 reverses it and
FR-015 obliges the amendment, in gohai's own change rather than in this one.

Two further decisions came from the goal rather than from the first attempt:

- **FR-002 and FR-019 together** are what make six documents a map. Each
  baseline states its own edges, and `system`'s memory holds the whole graph.
  Neither alone works: a central map goes stale because nothing forces it to
  match, and distributed edges never compose into a picture.
- **FR-017 and FR-018** require ordinary prose and forbid Given/When/Then in a
  baseline. A feature specification is read once by a reviewer checking a
  change; a baseline is read repeatedly by somebody learning a system. The
  formalism that helps the first actively obstructs the second, and memory
  written in it reads as a test plan rather than an explanation.

This specification uses Given/When/Then itself, because the template requires it
of a feature. FR-017 says why that is not a contradiction: the two documents
have different readers.

## Settled after the first review

Two questions this specification left open are now decided, and one new finding
is recorded:

- **`osapi` gets a baseline** (FR-021). Its five archived features record what
  changed, never what the repository is, so it is the one memory that does not
  conform to the shape. Six repositories, six baselines.
- **`system` does not** (FR-022), because it is not a repository. It holds the
  map and the agreements instead. Without stating this, "every project gets a
  baseline" reads as including it, and a baseline of a project with no code
  would have to invent its subject.
- **208 doc pages have no link checking** (FR-023, FR-024). `osapi-orchestrator`
  and `gohai` enforce markdown formatting only, where `osapi` builds and
  link-checks its 221. The rest of the build tooling is uniform, which the
  requirement states explicitly rather than leaving a reader to infer drift.
  Recorded with an owner, not fixed.
