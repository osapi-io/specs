# Tasks: Corpus backfill from the published site

**Feature**: `003-corpus-backfill` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md) | **Plan**: [plan.md](plan.md)

**Input**: [research.md](research.md) for the classification, the subjects and
the addresses; [data-model.md](data-model.md) for the section-by-section
mapping; [contracts/citation.md](contracts/citation.md) for what a citation is;
[quickstart.md](quickstart.md) for how each criterion is verified.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — may run in parallel with other **[P]** tasks: different files, no
  dependency on an incomplete task.
- **[US1]**, **[US2]**, **[US3]** — the user story from the specification that
  the task serves.
- Every task names the file it touches.

## Path Conventions

Two repositories, written in full because CONTRIBUTING's "Closing a change"
assumes one:

- `specs/` — this repository. Corpus under `components/osapi/specs/`, skill
  under `.claude/skills/add-a-domain/`.
- `osapi/` — the site under `docs/docs/sidebar/`, its config at
  `docs/docusaurus.config.ts`.

A task in `osapi/` and a task in `specs/` are never in the same pull request.
The ordering that makes that safe is research Finding 3: the corpus statement
merges first, the site change follows, and both must land.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Read `osapi/docs/docs/sidebar/architecture/job-architecture.md` in
  full and confirm the section ranges in [data-model.md](data-model.md) against
  the file as it stands. It is 630 lines, not the 603 the specification records
  (research Finding 2), so the ranges shift by 27 near the end.
- [x] T002 [P] Check each of the five principles in
  `osapi/docs/docs/sidebar/architecture/principles.md` against
  `specs/.charter/fragments/global/` and
  `specs/components/osapi/.specify/memory/constitution.md`. Record, per
  principle, whether it is already stated there — research Finding 1. The answer
  decides whether it becomes a citation or a statement in Subject B.
- [x] T003 [P] Confirm `@docusaurus/plugin-client-redirects` is compatible with
  the site's Docusaurus version in `osapi/docs/package.json`. Two addresses
  depend on it; if it is not, the fallback is a stub page each, and research
  Decision 3 needs amending first.

## Phase 2: Foundational (Blocking Prerequisites)

These bind both subjects. Nothing in Phase 3 or later starts until they are
done.

- [x] T004 [US3] Write the citation convention into
  `specs/.claude/skills/add-a-domain/README.md`: the table shape from
  [contracts/citation.md](contracts/citation.md), that citations are relative
  and name a requirement rather than a document, and that `just skill-lint` is
  what fails when one does not resolve.
- [x] T005 [US3] Verify the gate does what the contract claims: add a
  deliberately broken citation to a scratch copy of a reference file, run
  `cd specs && just skill-lint`, confirm it fails, and remove it. FR-008 is only
  enforceable if this is true, and the Verification principle says measure
  rather than assume.

> Phases 1 through 3 are done, and Subject A has landed in both repositories:
> `004-job-system` is specified, planned, tasked, implemented and archived, its
> site page is 203 operator-facing lines, and the skill cites it. Phase 4's
> tasks were carried out as `004`'s own T003–T011 rather than from this list,
> which is what "Subject A is its own feature" means in practice.
>
> Phases 1 and 2 are done. T002 corrected research Finding 1 rather than
> confirming it: none of the five principles are already stated in the charter,
> and the two that looked like they were are near misses recorded in the
> finding. T001 confirmed the live section ranges, T003 confirmed the redirects
> plugin publishes at the site's exact version, and T005 measured the citation
> gate failing on a broken citation and passing once it was restored.

## Phase 3: User Story 1 — a contributor answers from the corpus alone (Priority: P1) 🎯 MVP

**Goal**: the job system is stated in the corpus, completely enough that the
three questions in [quickstart.md](quickstart.md) are answerable without opening
the site.

**Independent test**: SC-001's reading, with only
`components/osapi/specs/004-job-system/spec.md` open.

This is Subject A, and per FR-005 it goes first. It is its own feature: these
tasks carry it as far as a merged specification, because a corpus statement is
what the site change then cites.

- [x] T006 [US1] Run `/speckit-specify` in `components/osapi` for Subject A,
  naming the sections in [data-model.md](data-model.md) marked *Corpus*, and
  producing `specs/components/osapi/specs/004-job-system/spec.md`. Per FR-009
  each requirement is checked against the code before it is written, and per
  FR-011 it cites the file it describes.
- [x] T007 [US1] In the same branch, run `/speckit-plan` and `/speckit-tasks`
  for `004`, then `/speckit-analyze`, and fix what it reports. Stages 2 through
  4 are one unit of review.
- [x] T008 [US1] Record, in `004`'s specification, every rule the code does not
  match as a gap rather than as a statement — FR-009. A rule moved from the site
  that the code has outgrown is the Edge Case the specification warns about.
- [x] T009 [US1] Cite `002` rather than restating it wherever Subject A reaches
  signing, response verification or agent identity —
  [data-model.md](data-model.md), "The relationship to what memory already
  holds".
- [x] T010 [US1] Open the pull request for `004` in `specs/` and merge it. This
  is the statement of record, and nothing in Phase 4 may start before it lands.

**Checkpoint**: the job system is stated in the corpus. The site still says it
too, identically, and nothing points at either — the window research Finding 3
describes.

## Phase 4: User Story 2 — an operator still finds what they need (Priority: P1)

**Goal**: the site keeps what an operator uses, every address resolves, and no
surviving page sends an operator to the corpus.

**Independent test**: SC-002 and SC-003 from [quickstart.md](quickstart.md).

- [x] T011 [US2] Split
  `osapi/docs/docs/sidebar/architecture/job-architecture.md` per
  [data-model.md](data-model.md): the job states as observed, polling, the CLI
  reference and the metrics stay; the mechanics go. The result must read as a
  whole page, not a remainder — FR-003.
- [x] T012 [US2] Split
  `osapi/docs/docs/sidebar/architecture/system-architecture.md`: health checks
  with their endpoints and CLI access, authentication, authorization, CORS and
  external dependencies stay; the component map, the layers and the request flow
  go to Subject B.
- [x] T013 [US2] [P] Update the Deep Dives and Further Reading links in
  `osapi/docs/docs/sidebar/architecture/architecture.md`, which is otherwise
  unchanged. A link to a section that moved is the broken internal link the site
  build catches.
- [x] T014 [US2] Replace
  `osapi/docs/docs/sidebar/development/adding-an-api-domain.md` with the short
  contributor page from research Decision 3: what adding a domain involves, a
  citation table into the corpus, and a pointer to the `add-a-domain` skill.
- [x] T015 [US2] Add `@docusaurus/plugin-client-redirects` to
  `osapi/docs/package.json` and `osapi/docs/docusaurus.config.ts`, redirecting
  `architecture/api-guidelines` and `architecture/principles` to the page from
  T014, and delete both files.
- [x] T016 [US2] Run the SC-003 address check from
  [quickstart.md](quickstart.md). Six lines, none `MISSING`.
- [x] T017 [US2] Run
  `cd osapi && just docusaurus-fmt-check && just docusaurus-build`. The build is
  what catches a link left pointing at moved content.
- [x] T018 [US2] Run the SC-002 grep. No surviving page may answer an operator
  with "see the specifications repository"; the contributor page from T014 is
  the only exclusion.
- [x] T019 [US2] Open the pull request in `osapi/` for T011–T018 and merge it.
  The duplication from the Phase 3 checkpoint ends here — this task is what
  closes FR-010's window, and leaving it undone leaves the duplication
  permanent.

**Checkpoint**: the job system is stated once. Both readers are served, and
every address resolves.

## Phase 5: User Story 3 — a rule has one home (Priority: P2)

**Goal**: the skill cites rather than restates, and Subject B follows Subject
A's path.

**Independent test**: SC-004 and SC-005 from [quickstart.md](quickstart.md).

- [x] T020 [US3] Replace every restatement of a job system rule in
  `specs/.claude/skills/add-a-domain/references/` with a citation table naming
  the `004` requirement, following `references/provider.md`'s existing example.

- [x] T021 [US3] Run `cd specs && just test`. `skill-lint` resolving every
  citation is SC-004's gate.

- [x] T022 [US3] Run the SC-005 check:
  `git diff --stat main -- .claude/skills/add-a-domain/` must be net negative on
  `references/`, with `SKILL.md` unchanged in shape.

  **T022 passes, and the margin is worth recording.** Measured against
  `d370e37`, the commit that planned this feature:

  | Reference     | Then    | Now     |
  | ------------- | ------- | ------- |
  | `agent.md`    | 119     | 136     |
  | `api.md`      | 193     | 125     |
  | `cli.md`      | 83      | 83      |
  | `docs.md`     | 60      | 81      |
  | `provider.md` | 127     | 127     |
  | `sdk.md`      | 122     | 140     |
  | **Total**     | **704** | **692** |

  Net **-12** on `references/`, and `SKILL.md` unchanged at 140 lines, so the
  check is met. It is met narrowly, and the reason is honest rather than a
  shortfall: five rules turned out to have no home in the corpus — three CLI and
  validation rules in `005`'s T016 to T018, and the absent `sdk-standards`
  capability named twice — and each is now stated where it was with a note
  saying the corpus does not hold it. Deleting them to make this number look
  better would have lost five real rules.

  The measure that shows what the backfill actually achieved is the site, not
  the skill: **950 lines of contributor knowledge left `docs/`** across the two
  subjects — 427 from `job-architecture.md`, 578 from `adding-an-api-domain.md`,
  107 in two deleted pages, and 188 from `system-architecture.md`.

- [x] T023 [US3] Run `/speckit-specify` for Subject B — building a domain —
  producing `specs/components/osapi/specs/005-building-a-domain/spec.md` from
  the sources in [data-model.md](data-model.md), citing `001` for every provider
  rule it already holds rather than restating it.

- [x] T024 [US3] Fold in the principles that T002 found are *not* already stated
  in the charter or the constitution; cite the ones that are.

- [x] T025 [US3] Carry Subject B through the same two-repository sequence: merge
  `005` in `specs/`, then the osapi pull request that empties
  `adding-an-api-domain.md` of what `005` now states and updates the citations.

**Subject B completed 2026-09-28.** T012 through T019 and T023 through T025 were
carried out by [005-building-a-domain](../005-building-a-domain/tasks.md), which
ran the same two-repository sequence Subject A did: the corpus statement and the
skill citations merged in `specs/` as #152 and #154, then the site reduction
merged in `osapi/` as #545.

| This task                                    | Carried out by `005`                                              |
| -------------------------------------------- | ----------------------------------------------------------------- |
| T012 the `system-architecture.md` split      | T009, T010 — 330 lines to 142                                     |
| T013 `architecture.md` links                 | T012 — it also described `system-architecture.md` as what left it |
| T014 the contributor page                    | T005, T006 — 654 lines to 76                                      |
| T015 the redirects plugin and both deletions | T007, T008                                                        |
| T016 the address check                       | T014's build, verified in the generated HTML                      |
| T017 the osapi gate                          | T014                                                              |
| T018 the SC-002 grep                         | T013                                                              |
| T019 merge the osapi pull request            | T015 — osapi#545                                                  |
| T023 specify Subject B                       | specs#152                                                         |
| T024 fold in the principles                  | T003, which found all **eight** unstated, not five                |
| T025 the two-repository sequence             | the whole of `005`                                                |

Two of this feature's own records were wrong and `005` recorded both rather than
correcting them quietly: `api-guidelines.md` states six guidelines, not five,
and `principles.md` states eight principles, not five. The line counts here were
right, so neither page had drifted — the counts were taken from memory. They are
corrected when this feature is archived, which is T028.

Only T026 through T029 remain. Archiving `003` comes after both its subjects,
and both have now landed.

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T026 [P] Run the SC-006 check from [quickstart.md](quickstart.md): every
  behavioural requirement in `004` names the file it describes, and a sample of
  five is opened and confirmed against the code.

  **Passes.** 24 of `004`'s 25 requirements name the file they describe or cite
  another specification. The exception is its FR-024, which obliges the skill to
  cite rather than restate — a process rule with no code to name, so nothing is
  missing.

  Five opened and confirmed against the code, not against the specification:

  | Requirement | Claim                                   | Confirmed at                                                                |
  | ----------- | --------------------------------------- | --------------------------------------------------------------------------- |
  | FR-001      | a job is keyed `jobs.{job-id}`          | `internal/job/client/client.go:334` and `:489` — `kvKey := "jobs." + jobID` |
  | FR-014      | `MaxDeliver: 5`, `AckWait: 2m`          | `cmd/root.go:175` and `:176`                                                |
  | FR-017      | the backstop is `DefaultCommandTimeout` | `internal/exec/types.go:36` — `10 * time.Minute`                            |
  | FR-021      | the `job-queue` TTL is `1h`             | `configs/osapi.yaml:92`                                                     |
  | FR-019      | four per-host statuses                  | `pkg/sdk/client/status.go:46–51` — failed, skipped, timeout beside ok       |

- [x] T027 [P] Run the SC-001 reading with somebody who has not read the site
  pages, using the three fixed questions. An author cannot test their own corpus
  for completeness.

  **Already satisfied, and deliberately not re-run.** This task's reading is
  defined in [quickstart.md](quickstart.md) as the three fixed questions asked
  against `components/osapi/specs/004-job-system/spec.md` — which is exactly the
  reading `004` ran as its own T015, by a fresh agent given that one file and
  nothing else: no repository, no site, no other specification, no session
  context. All three came back ANSWERABLE.

  Re-running it would put the same questions to the same file, so what it would
  test is the reader rather than the corpus. Recorded here instead, with two
  things a later reader should know:

  - That reading also found two real gaps, and `004` was amended for both before
    this was written — the two clocks now give their durations, and the terminal
    case of exhausted redelivery is stated. The file satisfies these questions
    by a wider margin now than when the reading passed.
  - Subject B was read separately, against its own specification and its own
    four questions, as `005`'s T021. That reading found three further holes, all
    since amended. Both subjects have therefore been read by somebody who had
    not seen the site pages, which is what this task exists for.

- [x] T028 Run `/speckit-archive-run specs/003-corpus-backfill` once T019 and
  T025 have merged, consolidating this feature into
  `specs/components/osapi/.specify/memory/`. Archive after the implementation,
  not before: this feature's outcome is the classification and the pattern, and
  both are only true once the moves have landed.

  **Archived 2026-09-28. The backfill is complete.** Merged into
  `components/osapi/.specify/memory/`: 1 user story as US13, 12 requirements as
  FR-082–FR-093, 4 entities, 3 edge cases, 2 outcomes as SC-024 and SC-025, and
  4 assumptions as AS-019–AS-022. The citation contract and the two redirected
  addresses went to `memory/plan.md`.

  **Two stories and four outcomes folded rather than duplicated**, into entries
  this feature's own subjects had already put in memory: the operator story into
  US11, the one-home story into US12, and the outcomes about reading from the
  corpus, citing the code, one statement per rule, and addresses resolving into
  SC-013, SC-014, SC-016 and SC-019. Four of those folds widened the existing
  entry from one subject to the general case. Nothing was superseded.

  That folding is the honest shape for a method feature archived after its
  subjects. The alternative was twelve near-duplicates of rules already stated
  per-subject.

- [x] T029 Update `specs/components/osapi/specs/003-corpus-backfill/spec.md`'s
  Assumptions with the corrected line count for `job-architecture.md` — 630, not
  603 — in its own pull request. A merged specification that turns out wrong is
  amended before the work that depends on it, per the Correction principle.

  **Merged as specs#157, and it was three corrections rather than one.** The
  task named the line count; the work had found two more:

  | This feature recorded                     | It is |
  | ----------------------------------------- | ----- |
  | `job-architecture.md` is 603 lines        | 630   |
  | `api-guidelines.md` holds five guidelines | six   |
  | `principles.md` holds five principles     | eight |

  **Every line count was right.** What was wrong was the count of items inside
  two of the pages, taken from reading about them rather than from them — which
  is the failure FR-009 exists to catch, in this feature's own record. Corrected
  in its own pull request ahead of archival, because a specification archived
  with wrong inventories records the error as knowledge.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** (T001–T003) has no dependencies. T002 and T003 are parallel.
- **Phase 2** (T004–T005) depends on Phase 1 and blocks everything after it.
- **Phase 3** (T006–T010) depends on Phase 2. T010 is a merge gate.
- **Phase 4** (T011–T019) depends on **T010**. The site cannot cite a
  specification that is not merged.
- **Phase 5** (T020–T025) depends on T010 for the citations and on T019 for the
  precedent. T023–T025 repeat Phase 3 and Phase 4 for Subject B.
- **Phase 6** (T026–T029) depends on T019 and T025, except T029, which can
  happen at any time and should happen early.

### The dependency that is not a phase

T010 → T019 is the one that matters and the one nothing enforces. Between them
the job system is stated twice, identically. If T019 stalls, FR-010 is violated
permanently and quietly. Any pause between those two tasks is worth an issue in
osapi naming T019 as the remaining work — which is what `global/tracking` means
by an intent surviving being put down.

### Parallel Opportunities

- T002 and T003, both reading and neither writing.
- T013 alongside T011 and T012: a different file, and its links are checked by
  the same build.
- T026 and T027, once the moves have landed.

## Implementation Strategy

**MVP is Phase 3 plus Phase 4** — Subject A, stated in the corpus and removed
from the site. That alone satisfies FR-005, the first two user stories and
SC-001 through SC-003, and it proves the two-repository sequence works before
Subject B, which is four times the page count, depends on it.

Subject B follows as its own feature. It is deliberately not implemented out of
this one: the Workflow principle gives each specification its own lifecycle, and
Subject A's outcome is what tells Subject B whether the pattern holds.
