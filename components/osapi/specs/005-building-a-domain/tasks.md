______________________________________________________________________

## description: "Task list for building a domain"

# Tasks: Building a domain

**Input**: Design documents from `components/osapi/specs/005-building-a-domain/`

**Prerequisites**: [spec.md](spec.md) merged (PR #152), [plan.md](plan.md),
[research.md](research.md), [data-model.md](data-model.md),
[contracts/walkthrough.md](contracts/walkthrough.md),
[quickstart.md](quickstart.md)

**Tests**: none. There is no code in this feature. What stands in for a test is
`skill-lint` resolving every citation, `docusaurus-build` failing on a link to a
deleted page, and the SC-001 reading.

**Organization**: by the three user stories, in priority order. Subject A's
[tasks.md](../004-job-system/tasks.md) is the shape this follows.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel — different files, no dependency on an incomplete
  task
- **[Story]**: US1, US2 or US3 from [spec.md](spec.md)

## Two repositories, and the order they merge

[research.md](research.md) Decision 1 fixes this and the reason is worth keeping
in front of whoever runs the list: **the corpus pull request merges first.**
Site-first leaves a window where neither the corpus nor the site states these
rules, `skill-lint` fails in `specs/`, and a contributor at the old address gets
a redirect to a page whose citations resolve to nothing. Corpus-first leaves a
window where both state them, which is visible, bounded, and gives a correct
answer from either.

| Pull request | Repository | Tasks                             |
| ------------ | ---------- | --------------------------------- |
| 1            | `specs/`   | T001–T004, T016–T020              |
| 2            | `osapi/`   | T005–T015                         |
| —            | `specs/`   | T021–T024, after both have merged |

______________________________________________________________________

## Phase 1: Setup

**Purpose**: confirm the boundaries the plan states still match the files.

- [ ] T001 Confirm the line ranges in [data-model.md](data-model.md) against
  `osapi/docs/docs/sidebar/architecture/system-architecture.md` as it stands
  today: `12–174` covering Component Map, Entry Points and Layers, and `241–266`
  covering Request Flow. Confirm the four page line counts — 654, 61, 46, 330. A
  range that no longer matches means the page moved under the plan, which is how
  [004's Finding 2](../004-job-system/spec.md) was caught; record the new range
  rather than quietly working around it.

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: T002 blocks every citation task. A wrong depth fails the build
in a way that reads like a missing file.

- [ ] T002 Confirm the citation depth by writing one citation and running the
  gate: from a file under `specs/.claude/skills/add-a-domain/references/`, the
  path to a corpus requirement is **four** `../` levels —
  `../../../../components/osapi/specs/005-building-a-domain/spec.md`. Three
  lands in `.claude/` and `skill-lint` says so by name. The rule is recorded in
  [003's citation contract](../003-corpus-backfill/contracts/citation.md); this
  task is the cheap proof before twenty rows are written against it.
- [ ] T003 Check the three principles 003 never named — Reliability and
  Stability, CLI Parity with API, Least Privilege Mode — against
  `.charter/fragments/global/` and
  `components/osapi/.specify/memory/constitution.md`, reading the fragment text
  rather than its heading. FR-023 requires this and
  [003's Finding 1](../003-corpus-backfill/research.md) is the reason: its first
  version claimed two principles were already charter rules, from the headings.
  Record what was found, including "unstated", so the next reader sees a check
  rather than an assumption.

**Checkpoint**: the citation shape is proven and the charter check is recorded.

______________________________________________________________________

## Phase 3: User Story 1 — a contributor can add a domain from the corpus alone (Priority: P1) 🎯 MVP

**Goal**: the corpus holds the sequence as well as the rules.

**Independent test**: SC-001's reading, run in Phase 6 once the corpus half has
merged.

- [ ] T004 [US1] Write the walkthrough into [data-model.md](data-model.md) —
  already drafted under "The walkthrough" — and confirm it keeps FR-004's three
  forced orderings separate from the conventional sequence, applying the test in
  [contracts/walkthrough.md](contracts/walkthrough.md): would a reader call the
  corpus *wrong* or merely *dated* if the step moved? Only "wrong" belongs in a
  requirement.

**Checkpoint**: the corpus states both the rules and the order. The site still
states them too — the window [research.md](research.md) Decision 1 describes.

______________________________________________________________________

## Phase 4: User Story 2 — an operator is not sent to a contributor's document (Priority: P1)

**Goal**: the site keeps what an operator uses, every address resolves, and two
pages cease to exist.

**Independent test**: SC-002 and SC-003 from [quickstart.md](quickstart.md).

- [ ] T005 [US2] Replace
  `osapi/docs/docs/sidebar/development/adding-an-api-domain.md` with the
  three-part contributor page specified in [data-model.md](data-model.md) under
  "The contributor page that survives": under ten lines of prose on what adding
  a domain involves, the citation table, and the pointer to the `add-a-domain`
  skill. No step contents, no code block, no summary of a rule — a summary is
  the second statement this feature exists to end.

  The citation table MUST include FR-022, the eight design principles, and
  FR-024, the gate. Both are rules a contributor needs and neither has another
  home on the site once `principles.md` is deleted.

- [ ] T006 [US2] State in one sentence on that page that its corpus links are
  absolute GitHub URLs because the corpus is not part of the published site.
  Without it the reader takes the one departure from
  [the citation contract](../003-corpus-backfill/contracts/citation.md) for an
  oversight.

- [ ] T007 [US2] Delete `osapi/docs/docs/sidebar/architecture/api-guidelines.md`
  and `osapi/docs/docs/sidebar/architecture/principles.md`. Both are wholly
  contributor knowledge — FR-014, FR-015, FR-022 — so neither keeps an operator
  half. This is the first time the backfill deletes a page rather than splitting
  one.

- [ ] T008 [US2] Add `@docusaurus/plugin-client-redirects` to
  `osapi/docs/package.json` and `osapi/docs/docusaurus.config.ts`, redirecting
  both deleted addresses to the contributor page. **This feature adds the
  plugin** — it is [003's T015](../003-corpus-backfill/tasks.md), and T022 marks
  that task done, so there is no earlier task to wait for. 005 is the only
  feature in the backfill that needs a redirect, which is why the plugin arrives
  here rather than with Subject A.

- [ ] T009 [US2] Remove lines `12–174` and `241–266` from
  `osapi/docs/docs/sidebar/architecture/system-architecture.md` — Component Map,
  Entry Points, Layers, Request Flow. Keep `175–240`, `267–309` and the link
  definitions.

- [ ] T010 [US2] Edit that page's introduction by one sentence so it leads into
  Health Checks rather than into a removed Component Map. Removing `241–266`
  leaves Health Checks running directly into Security, which reads; removing
  `12–174` leaves a jump the introduction has to cover.

- [ ] T011 [US2] Remove the `api-guidelines.md` and `principles.md` entries from
  that page's Further Reading list and add one to the contributor page. **This
  is a build failure, not a tidy-up**: `docusaurus-build` fails on a link to a
  deleted page, and both links are there today.

- [ ] T012 [US2] [P] Search the whole site for any other link to either deleted
  page:
  `grep -rn "api-guidelines\|principles" docs/docs docs/docusaurus.config.ts`.
  Everything outside the redirect configuration is a link that will break.
  `osapi/docs/docs/sidebar/architecture/architecture.md` is named here rather
  than left to the grep, because it is 003's T013 and its Deep Dives and Further
  Reading lists are where a link to moved content is most likely to survive. The
  page is otherwise unchanged.

- [ ] T013 [US2] Confirm no surviving page sends an operator to the corpus —
  003's FR-012 and SC-003's grep. The contributor page is the one exception and
  its reader is a contributor.

- [ ] T014 [US2] Run
  `cd osapi && mise exec -- just docusaurus-fmt-check && mise exec -- just docusaurus-build`.

- [ ] T015 [US2] Open and merge the osapi pull request for T005–T014. **This is
  the task that ends the duplication.** Until it lands, the corpus and the site
  both state these rules.

______________________________________________________________________

## Phase 5: User Story 3 — the rule has one home (Priority: P2)

**Goal**: the skill's six references cite the requirements instead of restating
the mechanics.

**Independent test**: SC-004's `just test`, and SC-005's grep.

- [ ] T016 [US3] Replace the domain-building mechanics in
  `specs/.claude/skills/add-a-domain/references/api.md` with citation rows
  naming FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018 and
  FR-024 — written out rather than as a range, so a coverage check can see each
  one. This is the largest of the six at 193 lines.

  FR-012, FR-014 and FR-024 each contain a recorded **Gap**. A citation row
  names the *rule* and leaves the gap in the corpus: "how a path parameter is
  validated", not "the page was wrong about `node.validateHostname()`". A gap
  copied into a reference becomes guidance, which is the opposite of what
  recording it was for.

- [ ] T017 [US3] [P] Do the same for `references/cli.md` citing FR-021,
  `references/docs.md` citing FR-001, and `references/agent.md` citing FR-009
  and FR-010. `references/agent.md` already cites 004 from Subject A; add to it
  rather than rewriting it. `references/provider.md` is unchanged — it already
  cites 001 and is the pattern being copied.

- [ ] T018 [US3] In `references/sdk.md`, cite FR-019 and FR-020, and **name the
  `sdk-standards` deferral at line 6 as unwritten rather than repeating it**. It
  claims binding rules exist in this repository and they do not. Repeating the
  claim propagates a settled-looking rule nobody has written; naming it tells
  the reader what state it is actually in.

- [ ] T019 [US3] Run the SC-005 grep from [quickstart.md](quickstart.md) over
  `specs/.claude/skills/add-a-domain/`. Every hit must sit in a citation row
  naming a requirement, never in a paragraph explaining the mechanism. A
  reference that explains how validation tags work is a second statement
  whatever it links to.

- [ ] T020 [US3] Run `cd specs && mise exec -- just test`. `skill-lint`
  resolving every new citation at four levels is the gate, and it is what T002
  proved in advance.

______________________________________________________________________

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T021 [P] Run the SC-001 reading from [quickstart.md](quickstart.md) with
  somebody who has not read the site page, asking the four fixed questions. An
  author cannot test their own corpus for completeness. A person is preferred; a
  fresh agent given **only** `spec.md` — no repository, no site, no other
  specification, no session context — is the fallback that makes the check
  runnable, and it is what Subject A used. **Record what it proves and what it
  does not**: that the answers are in the text, not that a person would succeed.
  Subject A's reading found two real gaps its author had read past twice, which
  is the argument for running it.

- [ ] T022 [P] Run the SC-006 check from [quickstart.md](quickstart.md): the
  contributor page's last commit must postdate this specification's merge. If it
  does not, the corpus and the site both state these rules and this feature is
  unfinished whatever the corpus says.

- [ ] T023 Mark 003's **T012 through T019** and T023 through T025 done, and
  update 003's `tasks.md` to record that Subject B completed, so a reader of 003
  sees a task list matching what happened. **Not T011**: that task split
  `job-architecture.md` and belongs to Subject A, which completed it in
  osapi#544, and it is already ticked. 003's own T028 and T029 remain, because
  archiving 003 comes after both its subjects.

  The mapping, so a reader of 003 can check it rather than trust it:

  | 003's task                                      | Carried out by               |
  | ----------------------------------------------- | ---------------------------- |
  | T012 the `system-architecture.md` split         | T009, T010                   |
  | T013 `architecture.md` links                    | T012                         |
  | T014 the contributor page                       | T005, T006                   |
  | T015 the redirects plugin and the two deletions | T007, T008                   |
  | T016 the SC-003 address check                   | T014's build and T012's grep |
  | T017 the osapi gate                             | T014                         |
  | T018 the SC-002 grep                            | T013                         |
  | T019 merge the osapi pull request               | T015                         |
  | T023 specify Subject B                          | merged as specs#152          |
  | T024 fold in the principles                     | T003, and FR-022 with FR-023 |
  | T025 the two-repository sequence                | the whole list               |

- [ ] T024 Run `/speckit-archive-run specs/005-building-a-domain` once T015 and
  T020 have merged, consolidating Subject B into
  `components/osapi/.specify/memory/`. Archive after the implementation, never
  before: what merged here is the statement, and the outcome is only true once
  the site change lands. The walkthrough in [data-model.md](data-model.md) folds
  into `memory/plan.md`; the requirements fold into `memory/spec.md`.

______________________________________________________________________

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1** has none.
- **Phase 2** blocks everything: T002 proves the citation depth before twenty
  rows depend on it, and T003 closes FR-023 before FR-022 is cited.
- **Phase 3** (US1) is the corpus half and merges first.
- **Phase 4** (US2) is the site half and cannot merge before Phase 3 and Phase 5
  have — see the table at the top.
- **Phase 5** (US3) travels with Phase 3 in the corpus pull request, because
  `skill-lint` runs in `specs/`.
- **Phase 6** needs both pull requests merged. T024 needs T015 and T020.

### What is genuinely parallel

- T012 with T009–T011 — a different search, same page family.
- T017 across its three files, and alongside T016 and T018: six reference files,
  no shared lines.
- T021 with T022 — a reading and a `git log`.

### What only looks parallel

T007 and T011 touch different files and **must not** be split across pull
requests: deleting the pages without editing the Further Reading list fails
`docusaurus-build`, and editing the list first leaves it pointing at the
contributor page before that page exists. Same change, either way.

______________________________________________________________________

## Implementation Strategy

### MVP

Phases 1, 2, 3 and 5 are one pull request in `specs/`. That is the corpus
statement plus its citations, and it is coherent on its own: the rules are
stated, the skill cites them, `just test` is green. The site still duplicates
them, which is the visible bounded window rather than a broken state.

### Then

Phase 4 in `osapi/`, one pull request, which is the half that ends the
duplication. Then Phase 6.

______________________________________________________________________

## Notes

- No Go code changes anywhere in this feature.
- Five gaps are recorded in [spec.md](spec.md) and **none is scheduled here**.
  [plan.md](plan.md)'s "Out of scope" table names each owner: `validateHostname`
  and Step 8's command list are osapi's, the `sdk-standards` capability is this
  repository's own feature, and 003's two miscounts are corrected when 003 is
  archived.
- Commit per task or per logical group. Stop at a checkpoint to validate.
