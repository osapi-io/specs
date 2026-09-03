______________________________________________________________________

## description: "Task list for repository inventory"

# Tasks: Repository inventory

**Input**: Design documents from `system/specs/001-repository-inventory/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No automated test tasks. The feature adds no code;
`gh reposync --check` is the test and quickstart.md holds the verification
scenarios.

**Organization**: Grouped by user story. US1 is the manifest, US2 is the rule
that makes anything read it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 or US2

## Repositories touched

This feature spans repositories, so it is more than one pull request:

| Repository                                                                          | Change                                                                                                                   | PR                     |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| `osapi-io/.github`                                                                  | gains `repos.json`                                                                                                       | 1st — must merge first |
| `osapi-io/{gohai,nats-client,nats-server,osapi,osapi-orchestrator,osapi-justfiles}` | deletes `.github/repos.json`                                                                                             | 3rd — one per repo     |
| `osapi-io/specs`                                                                    | deletes its manifest, adds the charter fragment, recomposes the constitution, fixes `dependencies.md`, carries this spec | 2nd                    |

Order matters: the merged manifest must exist before any per-repository manifest
is deleted, so no repository is ever left ungoverned.

______________________________________________________________________

## Phase 1: Setup

**Purpose**: Confirm tooling and record the starting state so the result can be
compared against something.

- [ ] T001 Confirm prerequisites: `gh auth status` shows an authenticated
  account with `repo` scope, `gh ext list` includes `retr0h/gh-reposync`, and
  `jq --version` succeeds
- [ ] T002 Record the baseline by running the "Before" block in
  `system/specs/001-repository-inventory/quickstart.md` and saving its output:
  every manifest declares 1 repository, and `gh reposync --check` in
  `osapi-io/specs` reports `[specs] topics: DRIFT` with exit 1

**Checkpoint**: Tooling works and the starting state is captured.

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the merged manifest content before any repository is changed.

**⚠️ CRITICAL**: T007 must not begin until T004 has merged.

- [ ] T003 Re-confirm the shared blocks are still identical across all seven
  manifests with
  `for f in ~/git/osapi-io/{gohai,nats-client,nats-server,osapi,osapi-orchestrator,osapi-justfiles,specs}/.github/repos.json; do jq -S -c '{settings,security,branch_protection}' "$f"; done | sort -u | wc -l`
  returning `1`. If it returns more, stop: the merge assumption in `plan.md` no
  longer holds and the plan needs revising before continuing
- [ ] T004 Compose the merged manifest content: one `org`, one shared
  `settings`/`security`/`branch_protection` block taken from any existing
  manifest, and eight `repos[]` entries carrying only `name`, `description` and
  `topics`, per `system/specs/001-repository-inventory/data-model.md`. Take
  `specs` topics as `["osapi","spec-driven-development","spec-kit","specs"]` per
  research.md decision 7, and add `.github` with description
  `OSAPI organization profile and defaults.` and topics `["osapi"]`

**Checkpoint**: Manifest content ready; nothing changed yet.

______________________________________________________________________

## Phase 3: User Story 1 - One file says what repositories exist (Priority: P1) 🎯 MVP

**Goal**: A single manifest in `osapi-io/.github` lists every managed
repository, and no second manifest survives.

**Independent Test**: `jq -r '.repos[].name' repos.json` in `osapi-io/.github`
returns eight names, `ls ~/git/osapi-io/*/.github/repos.json` finds nothing, and
`gh reposync --check` passes.

### Implementation

- [ ] T005 [US1] Create `repos.json` at the root of the `osapi-io/.github`
  repository with the content composed in T004, and open the pull request

- [ ] T006 [US1] Verify before merging: run `gh reposync --check` from the
  `osapi-io/.github` checkout and confirm it reports on all eight repositories,
  with `[specs] topics: DRIFT` the only failure

- [ ] T007 [US1] Merge the `osapi-io/.github` pull request

- [ ] T008 [US1] Resolve the `specs` drift by running
  `gh reposync --apply --repo specs` from the `osapi-io/.github` checkout,
  replacing the live `openspec` topic with `spec-kit`

- [ ] T009 [US1] Confirm `gh reposync --check` now passes for all eight
  repositories with exit 0

- [ ] T010 [P] [US1] Delete `.github/repos.json` in `osapi-io/gohai` and open
  the pull request

- [ ] T011 [P] [US1] Delete `.github/repos.json` in `osapi-io/nats-client` and
  open the pull request

- [ ] T012 [P] [US1] Delete `.github/repos.json` in `osapi-io/nats-server` and
  open the pull request

- [ ] T013 [P] [US1] Delete `.github/repos.json` in `osapi-io/osapi` and open
  the pull request

- [ ] T014 [P] [US1] Delete `.github/repos.json` in
  `osapi-io/osapi-orchestrator` and open the pull request

- [ ] T015 [P] [US1] Delete `.github/repos.json` in `osapi-io/osapi-justfiles`
  and open the pull request

- [ ] T016 [US1] Delete `.github/repos.json` in `osapi-io/specs` as part of this
  feature's pull request

- [ ] T017 [US1] Confirm no per-repository manifest remains among the active
  repositories: `ls ~/git/osapi-io/*/.github/repos.json` finds only `osapi-ui`,
  which is archived and therefore read-only. Record that exception rather than
  attempting to unarchive it

- [ ] T017a [US1] Confirm the manifest lists the `.github` repository itself,
  per FR-005: `jq -r '.repos[].name' repos.json | grep -Fx '.github'`

- [ ] T017b [US1] Confirm no manifest entry names a repository that no longer
  exists, per FR-007. `gh reposync --check` fails on such an entry, so a clean
  exit 0 in T009 is the evidence

**Checkpoint**: One manifest, eight repositories, `--check` green. US1 delivers
the whole of what was asked for and can ship without US2.

______________________________________________________________________

## Phase 4: User Story 2 - Work that spans repositories is told to read it (Priority: P2)

**Goal**: The constitution names the manifest as the source of the repository
list and forbids writing another one, so a fresh session learns this without
being told.

**Independent Test**: `grep -i repositor system/.specify/memory/constitution.md`
finds the rule in the generated constitution, and `dependencies.md` no longer
names repositories inline.

### Implementation

- [ ] T018 [US2] Write the charter fragment at
  `.charter/fragments/global/repositories.md`, stating that the repository list
  comes from `osapi-io/.github/repos.json` and that no other document may
  contain one. Match the voice of the five existing fragments in
  `.charter/fragments/global/`
- [ ] T019 [US2] Register the fragment in `.charter/manifest.yml` alongside the
  existing five
- [ ] T020 [US2] Add `global/repositories` to the `fragments` list in
  `system/.specify/charter/state.yml`
- [ ] T021 [US2] Recompose by running `/speckit-charter-compose` from `system/`,
  then `/speckit-constitution` to write the file. Compose assembles the fragment
  sections; `/speckit-constitution` writes `constitution.md` including its
  version line. Do not hand-edit `constitution.md` — it is generated, and a
  direct edit is lost on the next compose
- [ ] T022 [US2] Confirm the written `system/.specify/memory/constitution.md`
  contains a `<!-- [F] global/repositories SECTION -->` block and that its
  `**Version**` line has been bumped from `1.1.0` with `Last Amended` updated.
  If the version did not change, re-run `/speckit-constitution` rather than
  editing the line by hand
- [ ] T023 [US2] Rewrite `system/.specify/memory/dependencies.md` so its
  reproduction script reads repository names from the manifest instead of naming
  them inline in the `for d in ...` loop

**Checkpoint**: The rule is in the generated constitution and loads every
session. The one existing violation is fixed.

______________________________________________________________________

## Phase 5: Polish & Verification

- [ ] T024 Run every scenario in
  `system/specs/001-repository-inventory/quickstart.md` and confirm each
  expected result
- [ ] T025 Run `mise exec -- just test` in `osapi-io/specs` and confirm
  `md-fmt-check` and `just-fmt-check` are clean
- [ ] T026 Confirm no hand-maintained repository list remains anywhere in the
  specs repository, per SC-003

______________________________________________________________________

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: needs Setup. T003 is a gate — if the shared blocks
  have diverged, stop and revise the plan
- **US1 (Phase 3)**: needs Foundational
- **US2 (Phase 4)**: independent of US1 in principle, but the rule points at a
  manifest that should exist first. Do US1 first
- **Polish (Phase 5)**: needs both

### Critical ordering within US1

```text
T005 create manifest → T007 merge → T008 apply drift → T009 verify
                                                          ↓
                              T010–T016 delete per-repo manifests
```

Deleting a per-repository manifest before the merged one has merged leaves that
repository with no manifest at all. T007 is the gate.

### Parallel Opportunities

- T010 through T015 are six independent pull requests in six repositories and
  can all be opened at once, once T007 has merged
- T016 rides in this feature's own pull request, so it is not parallel with the
  others
- T018 and T019 touch different files and can be done together

______________________________________________________________________

## Implementation Strategy

### MVP: User Story 1 only

Phases 1 → 2 → 3, then stop and check. That delivers one file that answers what
repositories exist, with `gh reposync --check` green. It is the whole of what
was asked for.

### Then User Story 2

Phase 4 adds the rule that makes anything read the manifest. Without it the
manifest works but relies on someone remembering it exists, which is how the two
hardcoded lists came about in the first place.

______________________________________________________________________

## Notes

- `[P]` tasks touch different repositories and have no ordering between them
- `osapi-ui` is archived and read-only; its stale manifest stays. Recorded in
  T017 rather than worked around
- Nothing here runs unattended. `gh reposync --check` is run by hand, per
  research.md decision 6
- `--apply` mutates repository settings and branch protection. T008 is the only
  task that applies, and it is scoped to one repository with `--repo specs`
