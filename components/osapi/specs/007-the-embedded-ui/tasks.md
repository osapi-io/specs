______________________________________________________________________

## description: "Task list for the embedded UI"

# Tasks: The embedded UI

**Input**: Design documents from `components/osapi/specs/007-the-embedded-ui/`

**Prerequisites**: [spec.md](spec.md) merged (specs#172), [plan.md](plan.md),
[research.md](research.md), [data-model.md](data-model.md),
[quickstart.md](quickstart.md)

**Tests**: none. There is no code. What stands in is `docusaurus-build` failing
on a broken link, three greps, and a reading.

## Two repositories, and the order

The sequence the backfill established, and here the order matters more than
usual.

| Pull request | Repository | Tasks                       |
| ------------ | ---------- | --------------------------- |
| 1            | `specs/`   | T001–T004                   |
| 2            | `osapi/`   | T005–T013                   |
| —            | `specs/`   | T014–T016, after both merge |

**Why the order matters more here.** Two prose documents state this architecture
and they have diverged. If the osapi change landed first, the corpus would not
yet hold the statement and `ui/docs/architecture.md` would have been reduced to
a pointer aimed at nothing. Worse, if only *part* of the osapi change landed —
the site page but not the file beside the code — the divergent copy becomes the
sole statement, and it is the one missing `Configuration` and
`Embedding Mechanism`. **Doing half of the second pull request is worse than
doing none of it**, which is why T012 exists.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Confirm the line ranges in [plan.md](plan.md) against
  `osapi/docs/docs/sidebar/architecture/ui.md` as it stands: `12–53`, `54–68`,
  `69–102`, `103–114`, `115–153`, `154–159`, `160–175`, `176–190`, `191–231`,
  `232–264`. They must sum to 264 and each boundary must land on its heading. A
  range that no longer matches means the page moved under the plan — record the
  new range rather than working around it, which is how 004's Finding 2 was
  caught.

  **Confirmed against the live file.** All ten boundaries land on their heading
  — line 12 `## Embedding Mechanism`, 54 `## Configuration`, 69
  `## Application Structure`, 103 `## Tech Stack`, 115
  `## Component Architecture`, 154 `## Authentication & Authorization`, 160
  `### Auth flow`, 176 `### RBAC model`, 191 `## SDK Generation`, 232 `## Pages`
  — the ranges are contiguous, and they total 264. Nothing moved under the plan.

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 SC-005: confirm all three unshared sections are in the merged
  `spec.md` before any file is touched: `Feature flags` (from
  `ui/docs/architecture.md`), `Configuration` and `Embedding Mechanism` (from
  the site page). **This is the task that makes the union real.** If one is
  missing and the osapi change proceeds, that section exists nowhere afterwards
  — the corpus does not hold it and both copies are gone.

  **Passes.** All three are in the merged statement: `Feature flags`,
  `Configuration` and `Embedding Mechanism`. Nothing can be lost by the
  deletions in Phase 4 — the union is real before any file is touched, which is
  the whole point of running this first. **Checkpoint**: nothing can be lost by
  the deletions that follow.

______________________________________________________________________

## Phase 3: User Story 1 — the architecture is stated once (Priority: P1)

**Goal**: the corpus holds one statement, so the two copies have something to be
replaced by.

**Independent test**: SC-002's greps, run after Phase 4.

- [x] T003 [US1] Confirm the corpus statement cites rather than restates where
  it reaches osapi's permission model — `resource:verb` and the three roles are
  osapi's and already stated — and where it reaches the generated client, which
  shares [005](../005-building-a-domain/spec.md)'s combined specification.

  **Confirmed.** FR-008 states the permission model is osapi's — three roles and
  `resource:verb` — and says where it reaches what those permissions mean it
  cites rather than restates. FR-005 cites 005's combined specification for the
  generated client rather than describing generation again.

- [x] T004 [US1] Run `cd specs && mise exec -- just test`, then open and merge
  the specs pull request. **Nothing in osapi may be touched before this merges**
  — the corpus statement is what the pointers point at.

  **Already satisfied by specs#172.** For a corpus feature the statement is
  `spec.md`, which merged at stage 1 — there is no separate corpus pull request
  to open. See the correction note below Phase 5. **Checkpoint**: the corpus
  states it. Three documents still state it too, which is the bounded window the
  backfill's sequencing accepts.

______________________________________________________________________

## Phase 4: User Story 2 — an operator keeps what they use (Priority: P1)

**Goal**: the site keeps what an operator configures and sees, and the duplicate
statements go.

**Independent test**: SC-003 and SC-004 from [quickstart.md](quickstart.md).

- [ ] T005 [US2] Remove lines `12–53`, `69–153`, `160–175` and `191–231` from
  `osapi/docs/docs/sidebar/architecture/ui.md` — the embedding mechanism,
  application structure, stack, component architecture, auth flow, SDK
  generation and fetch mutator. 184 lines of 264. Carries FR-003 through
  FR-007's move, and FR-014's split.
- [ ] T006 [US2] Rewrite that page's introduction, one sentence, so it
  introduces an operator's page and says where the architecture went. **Deletion
  alone will not fix it**: the current introduction introduces a contributor's
  document, and a page whose first paragraph promises architecture and then
  shows three operator sections reads as damaged rather than as reduced.
- [ ] T007 [US2] Confirm the surviving page's headings are exactly
  `## Configuration`, `## Authentication & Authorization`, `## Pages` — SC-003's
  grep — and that the authentication opening now runs into the RBAC model, and
  the RBAC model into `## Pages`, without a bridging paragraph. Both joins were
  checked in [plan.md](plan.md) and read.
- [ ] T008 [US2] Replace `osapi/docs/docs/sidebar/development/ui-development.md`
  with the three-part contributor index from [data-model.md](data-model.md):
  under ten lines of prose, a citation table by absolute GitHub address, and a
  pointer to the justfile rather than the commands — FR-015, with FR-009 for why
  the commands stay in the justfile. One sentence must say why the links are
  absolute — the corpus is a separate repository and is not published as part of
  the site.
- [ ] T009 [US2] Replace `osapi/ui/docs/architecture.md` with the pointer from
  [data-model.md](data-model.md), under ten lines. It **must** include the
  sentence saying it is a pointer rather than a summary: a pointer is a file
  somebody can edit back into a document, and that sentence is the only thing
  guarding against it — [research.md](research.md) Decision 2. FR-016.
- [ ] T010 [US2] [P] Search the site for any link into a removed section:
  `grep -rn "ui.md#" docs/docs` and
  `grep -rn "ui-development" docs/docs docusaurus.config.ts`. A link to a moved
  anchor survives deletion and fails the build.
- [ ] T011 [US2] Run
  `cd osapi && mise exec -- just docusaurus-fmt-check && mise exec -- just docusaurus-build`
  — SC-006 — and confirm the diff is markdown only, which is SC-007.
- [ ] T012 [US2] Confirm **all three** files are in the same commit before
  opening the pull request: the split page, the contributor index, and the
  pointer. Splitting them across changes leaves the divergent copy as the sole
  statement for as long as the gap lasts, and that copy is the one missing
  `Configuration` and `Embedding Mechanism`.
- [ ] T013 [US2] Open and merge the osapi pull request. **This is the task that
  ends the divergence.** Until it lands, three documents state the same
  architecture and two of them disagree.

______________________________________________________________________

## Phase 5: Verification and archival

- [x] T014 [P] Run SC-002's greps from [quickstart.md](quickstart.md): the stack
  terms and the three moved headings must appear in the corpus and nowhere under
  `osapi/docs/docs` or `osapi/ui/docs`. The stack is the sharpest probe — it is
  the section both former copies held and neither needed.

  **Failed on the first run, and the failure is the finding.** The stack grep
  returned a hit in `features/management-dashboard.md` — a **fourth** copy of
  the architecture, holding React 19, Vite and `//go:embed`. The feature
  classified three documents and there were four. It sat eight lines above a
  sentence this feature had just edited, so being in the file was not enough;
  only the grep was. Recorded as FR-014a at specs#175 and removed at osapi#550.
  SC-004 failed at the same time — the pointer was ten lines against a criterion
  of under ten, because the bare corpus address takes a line of its own once
  mdformat wraps at 80. Tightened to nine rather than relaxing the criterion.

  **Passes now.** The stack terms, the three moved headings and `go:embed`
  return nothing under `osapi/docs/docs` or `osapi/ui/docs`; the three site
  headings are exactly `Configuration`, `Authentication & Authorization` and
  `Pages`; the pointer is 9 lines.

- [x] T015 [P] Run the SC-001 reading with somebody who has seen neither UI
  page, asking the three fixed questions from [quickstart.md](quickstart.md).
  The third is the one to watch: a reader who learned only that the client
  "decodes" the token, and not that it does not verify it, has been misled in a
  security-shaped way. A person is preferred; a fresh agent given only `spec.md`
  is the fallback. **Record what it proves and what it does not** — that the
  answers are in the text, not that a contributor would find them pleasant.

  **Two of three, and the third is a real defect.** A fresh agent given only
  `spec.md` — no repository, no site, no session context — answered question 1
  from FR-001 and FR-006, and question 3 from FR-007, both plainly. It could not
  answer question 2: **FR-004 required the corpus to state what separates the
  four kinds of component and then did not state it.** It named the four and
  gave the directories, so a reader learned there are four buckets and where
  they sit on disk, not how to decide which bucket a new file belongs in — a
  requirement about a requirement. Fixed in this branch, measured from the code
  rather than reasoned: a primitive imports no generated client (0 of 34), a
  domain component imports the client or a hook (38 of 43), and every hook is
  `.ts` rather than `.tsx` so none can hold markup.

  It also reported that the correction block reads as an appendix and is easy to
  stop short of, so a reader can finish holding the wrong document count. A
  pointer to it now sits under the summary.

  **What this proves and what it does not.** That the answers are in the text,
  for two of three. Not that a contributor mid-task would find them — an agent
  is more patient than a person — and not that the prose is good. It found in
  one pass what re-reading the file did not, which is the argument for the
  reading being done by somebody who has seen nothing else.

- [ ] T016 Run `/speckit-archive-run specs/007-the-embedded-ui` once T004 and
  T013 have merged, and mark `system`'s 002 T023 done. Archive after the
  implementation: what merged in `specs/` is the statement, and the outcome is
  only true once the three documents have changed.

______________________________________________________________________

**A correction to Phase 3, found by the analysis pass.** T004 says to "open and
merge the specs pull request", as though the corpus statement were written
during implementation. It was not: for a corpus feature the statement **is**
`spec.md`, which merged at stage 1 as specs#172. Phase 3 therefore holds no
writing — it is verification that the merged statement says what the move
depends on, and T002 is the load-bearing one. The same was true of `004` and
`005`, and neither plan said so.

______________________________________________________________________

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1** has none.
- **Phase 2** blocks Phase 4 absolutely. T002 is what guarantees the deletions
  lose nothing.
- **Phase 3** must merge before Phase 4 starts — T004 says so explicitly.
- **Phase 4** is one commit and one pull request. T012 enforces that.
- **Phase 5** needs both merged.

### What is genuinely parallel

- T010 alongside T005 through T009 — a different search over the same page
  family.
- T014 and T015 — a grep and a reading.

### What only looks parallel

T005, T008 and T009 touch three different files and **must not** be split across
pull requests. T012 exists because the failure mode is not a broken build but a
silently worse state: one statement surviving, and the wrong one.

______________________________________________________________________

## Implementation Strategy

### MVP

Phases 1 to 3 — one pull request in `specs/`. The corpus states the UI's
architecture once. Three documents still state it, which is the bounded window
rather than a broken state.

### Then

Phase 4 in `osapi/`, one commit, one pull request, all three files. Then Phase
5\.

______________________________________________________________________

## Notes

- No Go code changes. `ui/` is touched only for the documentation file it
  carries.
- The `add-a-domain` skill gains nothing — FR-017. A domain's UI work is not
  part of adding a domain today, and a citation for work nobody does is the rule
  invented to fill a template.
- 80 lines stay on the site page of 264; the specification's "roughly 60" was
  estimated before the ranges were counted. [plan.md](plan.md) has the measured
  split.
