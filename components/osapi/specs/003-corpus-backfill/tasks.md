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
- [ ] T007 [US1] In the same branch, run `/speckit-plan` and `/speckit-tasks`
  for `004`, then `/speckit-analyze`, and fix what it reports. Stages 2 through
  4 are one unit of review.
- [ ] T008 [US1] Record, in `004`'s specification, every rule the code does not
  match as a gap rather than as a statement — FR-009. A rule moved from the site
  that the code has outgrown is the Edge Case the specification warns about.
- [ ] T009 [US1] Cite `002` rather than restating it wherever Subject A reaches
  signing, response verification or agent identity —
  [data-model.md](data-model.md), "The relationship to what memory already
  holds".
- [ ] T010 [US1] Open the pull request for `004` in `specs/` and merge it. This
  is the statement of record, and nothing in Phase 4 may start before it lands.

**Checkpoint**: the job system is stated in the corpus. The site still says it
too, identically, and nothing points at either — the window research Finding 3
describes.

## Phase 4: User Story 2 — an operator still finds what they need (Priority: P1)

**Goal**: the site keeps what an operator uses, every address resolves, and no
surviving page sends an operator to the corpus.

**Independent test**: SC-002 and SC-003 from [quickstart.md](quickstart.md).

- [ ] T011 [US2] Split
  `osapi/docs/docs/sidebar/architecture/job-architecture.md` per
  [data-model.md](data-model.md): the job states as observed, polling, the CLI
  reference and the metrics stay; the mechanics go. The result must read as a
  whole page, not a remainder — FR-003.
- [ ] T012 [US2] Split
  `osapi/docs/docs/sidebar/architecture/system-architecture.md`: health checks
  with their endpoints and CLI access, authentication, authorization, CORS and
  external dependencies stay; the component map, the layers and the request flow
  go to Subject B.
- [ ] T013 [US2] [P] Update the Deep Dives and Further Reading links in
  `osapi/docs/docs/sidebar/architecture/architecture.md`, which is otherwise
  unchanged. A link to a section that moved is the broken internal link the site
  build catches.
- [ ] T014 [US2] Replace
  `osapi/docs/docs/sidebar/development/adding-an-api-domain.md` with the short
  contributor page from research Decision 3: what adding a domain involves, a
  citation table into the corpus, and a pointer to the `add-a-domain` skill.
- [ ] T015 [US2] Add `@docusaurus/plugin-client-redirects` to
  `osapi/docs/package.json` and `osapi/docs/docusaurus.config.ts`, redirecting
  `architecture/api-guidelines` and `architecture/principles` to the page from
  T014, and delete both files.
- [ ] T016 [US2] Run the SC-003 address check from
  [quickstart.md](quickstart.md). Six lines, none `MISSING`.
- [ ] T017 [US2] Run
  `cd osapi && just docusaurus-fmt-check && just docusaurus-build`. The build is
  what catches a link left pointing at moved content.
- [ ] T018 [US2] Run the SC-002 grep. No surviving page may answer an operator
  with "see the specifications repository"; the contributor page from T014 is
  the only exclusion.
- [ ] T019 [US2] Open the pull request in `osapi/` for T011–T018 and merge it.
  The duplication from the Phase 3 checkpoint ends here — this task is what
  closes FR-010's window, and leaving it undone leaves the duplication
  permanent.

**Checkpoint**: the job system is stated once. Both readers are served, and
every address resolves.

## Phase 5: User Story 3 — a rule has one home (Priority: P2)

**Goal**: the skill cites rather than restates, and Subject B follows Subject
A's path.

**Independent test**: SC-004 and SC-005 from [quickstart.md](quickstart.md).

- [ ] T020 [US3] Replace every restatement of a job system rule in
  `specs/.claude/skills/add-a-domain/references/` with a citation table naming
  the `004` requirement, following `references/provider.md`'s existing example.
- [ ] T021 [US3] Run `cd specs && just test`. `skill-lint` resolving every
  citation is SC-004's gate.
- [ ] T022 [US3] Run the SC-005 check:
  `git diff --stat main -- .claude/skills/add-a-domain/` must be net negative on
  `references/`, with `SKILL.md` unchanged in shape.
- [ ] T023 [US3] Run `/speckit-specify` for Subject B — building a domain —
  producing `specs/components/osapi/specs/005-building-a-domain/spec.md` from
  the sources in [data-model.md](data-model.md), citing `001` for every provider
  rule it already holds rather than restating it.
- [ ] T024 [US3] Fold in the principles that T002 found are *not* already stated
  in the charter or the constitution; cite the ones that are.
- [ ] T025 [US3] Carry Subject B through the same two-repository sequence: merge
  `005` in `specs/`, then the osapi pull request that empties
  `adding-an-api-domain.md` of what `005` now states and updates the citations.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Run the SC-006 check from [quickstart.md](quickstart.md): every
  behavioural requirement in `004` names the file it describes, and a sample of
  five is opened and confirmed against the code.
- [ ] T027 [P] Run the SC-001 reading with somebody who has not read the site
  pages, using the three fixed questions. An author cannot test their own corpus
  for completeness.
- [ ] T028 Run `/speckit-archive-run specs/003-corpus-backfill` once T019 and
  T025 have merged, consolidating this feature into
  `specs/components/osapi/.specify/memory/`. Archive after the implementation,
  not before: this feature's outcome is the classification and the pattern, and
  both are only true once the moves have landed.
- [ ] T029 Update `specs/components/osapi/specs/003-corpus-backfill/spec.md`'s
  Assumptions with the corrected line count for `job-architecture.md` — 630, not
  603 — in its own pull request. A merged specification that turns out wrong is
  amended before the work that depends on it, per the Correction principle.

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
