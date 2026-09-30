# Specification Quality Checklist: The embedded UI

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

Four items fail by design, as they have for every corpus feature here. The
subject is how a repository is built, so an inventory that named no files would
be unfalsifiable.

## What makes this move different from the backfill's four

**It reconciles three statements, not two.** The backfill compared a site page
against the code. Here two prose documents describe the same architecture and
have already diverged — 264 lines on the site last touched 2026-08-15, 263 lines
beside the code last touched 2026-09-02, each holding a section the other never
got.

**That is why the order matters more than usual.** Relocating only the site page
would leave the divergent copy as the sole statement by default, and that copy
is the one missing `Configuration` and `Embedding Mechanism`. Doing half of this
reaches a worse state than doing none.

## Three decisions worth reviewing

**FR-012 takes the union rather than choosing a winner.** All three unshared
sections survive: `Feature flags` from the copy beside the code, `Configuration`
and `Embedding Mechanism` from the site page. Picking the newer file would have
lost two sections; picking the site page would have lost one. None of the three
is a claim the other copy contradicted — each describes something that exists —
so no adjudication was needed, and FR-013 records that the shared sections'
differences are punctuation rather than disagreement, so a later reader does not
go looking for a decision nobody made.

**FR-016 keeps a file beside the code, as a pointer.** Every other document in
this programme either moves or stays. `ui/docs/architecture.md` becomes a
two-line pointer instead, because a contributor working in `ui/` looks there
first and an absent file sends them searching. Its location is its value; its
content is not.

**FR-017 adds nothing to the `add-a-domain` skill.** A domain's UI work is not
part of adding a domain today, and a citation invented for work nobody does is
the rule invented to fill a template that `global/correction` warns against.

## The split, and its precedent

`ui.md` is a split, not a move — about 60 lines of 264 stay. That is the shape
`system-architecture.md` took: what an operator configures and sees stays, how
it is built goes. `ui-development.md` moves entire, the shape
`adding-an-api-domain.md` took. Both precedents are in this project's own
memory, which is the argument for having written them down.
