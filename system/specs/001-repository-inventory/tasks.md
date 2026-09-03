______________________________________________________________________

## description: "Task list for repository inventory"

# Tasks: Repository inventory

**Input**: Design documents from `system/specs/001-repository-inventory/`

**Prerequisites**: plan.md, spec.md

**Tests**: No automated test tasks. The feature adds no code.

**Organization**: Grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 or US2

______________________________________________________________________

## Phase 1: Setup

- [ ] T001 Confirm `gh repo list osapi-io --no-archived --visibility public`
  returns the eight repositories, so the rule names a command that works

______________________________________________________________________

## Phase 2: User Story 1 - Cross-repository work knows where to get the list (Priority: P1) 🎯 MVP

**Goal**: The constitution names the command.

**Independent Test**:
`grep -i -A6 "^## Repositories" system/.specify/memory/constitution.md` shows
the rule in the generated file.

- [ ] T002 [US1] Write `.charter/fragments/global/repositories.md` stating that
  the osapi-io repositories are what the command returns and that no document
  may hold a copy. Match the length and voice of
  `.charter/fragments/global/tooling.md` — three short paragraphs, no headings
  beyond the title _(satisfies FR-001)_
- [ ] T003 [P] [US1] Add `global/repositories` to `mandatory_fragments` in
  `.charter/manifest.yml` _(satisfies FR-002)_
- [ ] T004 [P] [US1] Add `global/repositories` to `fragments` in
  `system/.specify/charter/state.yml` _(satisfies FR-002)_
- [ ] T005 [US1] Regenerate by running `/speckit-charter-compose` then
  `/speckit-constitution` from `system/`. Do not hand-edit `constitution.md`
  _(satisfies FR-002)_
- [ ] T006 [US1] Confirm `system/.specify/memory/constitution.md` contains a
  `<!-- [F] global/repositories SECTION -->` block and that its `**Version**`
  line bumped from `1.1.0` with `Last Amended` updated _(satisfies FR-002,
  SC-001)_

**Checkpoint**: The rule is in the generated constitution and loads every
session. US1 ships on its own.

______________________________________________________________________

## Phase 3: User Story 2 - The written lists are removed (Priority: P2)

**Goal**: The one document that hardcodes repository names stops.

**Independent Test**:
`grep -rn "nats-client" ~/git/osapi-io/specs --include="*.md"` returns no
hand-maintained list.

- [ ] T007 [US2] Rewrite the reproduction script in
  `system/.specify/memory/dependencies.md` so its `for d in ...` loop takes
  repositories from `gh repo list osapi-io --no-archived --visibility public`
  instead of naming them inline _(satisfies FR-003)_
- [ ] T008 [US2] Confirm no hand-maintained repository list remains anywhere in
  the specs repository _(satisfies SC-002)_

______________________________________________________________________

## Phase 4: Verification

- [ ] T009 Confirm adding a repository needs no edit: the command's output is
  the list, and nothing stores it _(satisfies SC-003)_
- [ ] T010 Run `mise exec -- just test` and confirm `md-fmt-check` and
  `just-fmt-check` are clean

______________________________________________________________________

## Dependencies & Execution Order

- Setup (T001) first
- US1 (T002–T006) next. T003 and T004 touch different files and can be done
  together; T005 needs both
- US2 (T007–T008) can follow US1 or run alongside it — it touches a different
  file
- Verification (T009–T010) last

## Implementation Strategy

US1 alone delivers the rule. US2 removes the existing violation, without which
the constitution contradicts the repository on the day it is written.
