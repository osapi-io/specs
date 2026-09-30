______________________________________________________________________

## description: "Task list for one shape for every component baseline"

# Tasks: One shape for every component baseline

**Input**: Design documents from `system/specs/002-baseline-shape/`

**Prerequisites**: [spec.md](spec.md) merged (specs#163, amended by #164 and
#165), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md),
[contracts/section-order.md](contracts/section-order.md),
[quickstart.md](quickstart.md)

**Tests**: none. There is no code. What stands in for a test is `just test`, the
composition check, and two readings that no command can perform.

## Read this before starting

**This feature writes four things and obliges ten others.** It is easy to read
the task list as "the baseline programme" and start writing baselines; FR-016
forbids that here, and the reason is that one wrong judgement would then
propagate into six documents before anybody reviewed it.

|                                         |                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------- |
| **Tasks this feature carries out**      | T001–T012 — the fragment, the manifest entry, the composition, the map |
| **Tasks that only open other features** | T013–T016 — they create a branch and invoke a skill, and stop          |
| **Not tasks at all**                    | The nine baselines and four moves. Each is its own feature's task list |

T013 to T016 are deliberately thin. A task here that produced another project's
baseline would be that project's work done in the wrong place.

______________________________________________________________________

## Phase 1: Setup

- [x] T001 Read [contracts/section-order.md](contracts/section-order.md) before
  writing anything, and confirm the seven sections it describes match FR-001's
  order in [spec.md](spec.md). The contract is what nine later features are
  written against; a disagreement between it and the requirement is cheap now
  and expensive after four baselines exist.

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: T002 through T005 are the whole of this feature's enforceable
output. A fragment that is written but not composed is a file, not a rule.

- [x] T002 Write `.charter/fragments/global/baseline.md` with the 14-line
  wording fixed in [research.md](research.md) Decision 1. Do not reword it: the
  wording was matched to the existing seven fragments' voice and length, and its
  middle paragraph names a real event — osapi's 1,840 lines of memory with no
  statement of purpose — because `global/correction` requires a requirement
  written from evidence the repository carries.

- [x] T003 Add `global/baseline` to `mandatory_fragments` in
  `.charter/manifest.yml`. **This is a separate step from T002 and skipping it
  is silent**: a fragment absent from the manifest is never composed, so it sits
  in the repository looking authoritative and binds nothing.

- [x] T004 Recompose the constitution for **all six** component projects by
  invoking `speckit-charter-compose` in each: `components/gohai`,
  `components/nats-client`, `components/nats-server`, `components/osapi`,
  `components/osapi-justfiles`, `components/osapi-orchestrator`. Six, not five.
  A project missed here is a repository bound by nothing, and nothing about its
  next baseline would reveal the omission.

  **Done, and it was wider than this task assumed.** All six component
  constitutions carried only **five** sections where the manifest declares
  eight: `global/repositories` (added by system's first feature) and
  `global/tracking` (added by specs#144) had never been composed into any of
  them. Only `system` had seven. So the fragment written in T002 could not have
  bound anything even once composed — the composition reads each project's
  `state.yml`, not the manifest, and every project's listed five.

  Both were fixed as part of this task, because T005 is unsatisfiable otherwise:
  each `state.yml` now lists all eight in manifest order, and every constitution
  carries eight marked sections at version 1.2.0.

  **No hand edits were lost.** `snapshot-detect-modified.sh` reported four
  sections modified in gohai, which was a false positive: comparing each section
  against its snapshot with heading levels and blank lines normalised showed the
  content identical, and the one remaining difference was a structural `---`
  before the metadata footer. The extension's own
  `constitution-validate-sections.sh` returns `VALID=true` for all six.

- [x] T005 Run the SC-005 check from [quickstart.md](quickstart.md):
  `grep -rl "^# Baseline" components/*/.specify/memory/constitution.md | wc -l`
  returns **6**. This is the task that distinguishes a composed rule from a
  written one.

  **Passes.**
  `grep -rl "^## Baseline" components/*/.specify/memory/constitution.md | wc -l`
  returns **6**. The three fragments that were missing are each now in 6 of 6.
  **Checkpoint**: the shape binds. Every baseline written after this point is
  written under a rule rather than under advice, which is the condition
  [research.md](research.md) Decision 5 exists to create.

______________________________________________________________________

## Phase 3: User Story 1 — the set reads as one thing (Priority: P1) 🎯 MVP

**Goal**: the map exists, so a reader can see the whole graph without reading
six documents first.

**Independent test**: the map's own commands reproduce its edges, and it agrees
with every baseline that exists.

- [x] T006 [US1] Add `## The Repository Map` to `system/.specify/memory/plan.md`
  with the table from [data-model.md](data-model.md) — six repositories, what
  each depends on, what depends on it, and one line on what it is. Not to
  `spec.md`: [research.md](research.md) Decision 2 gives the reason, which is
  that a dependency graph is current state and `plan.md` is where current state
  lives.

- [x] T007 [US1] Add the commands that produce the map beside it —
  `grep -oE "osapi-io/[a-z-]+" */go.mod` for the Go edges and
  `grep -n justfiles */justfile` for the build edge. **FR-007 applies to this
  feature's own artifacts**, not only to the baselines it governs, and a map
  without its commands is the cached list `global/repositories` forbids.

- [x] T008 [US1] State in the map section that the build edge — every repository
  fetching `osapi-justfiles` — appears in no `go.mod`, which is why it is listed
  separately rather than derived from the Go graph. A reader who ran only the
  first command would conclude `osapi-justfiles` has no dependents.

  Stated: every repository fetches `osapi-justfiles` through a justfile recipe
  rather than importing it, so it appears in no `go.mod`. A reader running only
  the Go command would conclude it has no dependents.

- [x] T009 [US1] Record in the map section that `osapi-justfiles` is fetched
  from `refs/heads/main` rather than a pinned ref, and that `global/tooling`
  requires a tool whose output is committed to be pinned. Owner: those
  repositories. Recorded, not fixed — this feature changes no repository.

  Recorded, not fixed: the fetch takes `refs/heads/main` rather than a pinned
  ref, against the Tooling principle. Owner named as `osapi-justfiles` and each
  consumer. **Checkpoint**: the graph is readable in one place and re-derivable
  from two commands.

______________________________________________________________________

## Phase 4: User Story 2 — a baseline survives ordinary change (Priority: P1)

**Goal**: the rules that keep a baseline evergreen are binding rather than
habitual.

**Independent test**: the fragment states the counts-with-commands rule, and
`contracts/section-order.md` gives a reviewer the question that distinguishes
architecture from a transcribed call graph.

- [x] T010 [US2] Confirm the fragment's third paragraph carries the
  counts-with-commands rule. It is the one mechanically checkable part of the
  shape, and [research.md](research.md) Decision 1 records it as deliberately a
  second rule rather than more context — a fragment omitting it would leave the
  most enforceable part as advice.

- [x] T011 [US2] Confirm `contracts/section-order.md` states, under section 3,
  the question a reviewer asks: *if a function were renamed tomorrow, would this
  section become wrong, or merely cite a stale path?* Nothing automatable checks
  the difference between architecture and a call graph, and a contract that did
  not give the reviewer a question would leave FR-004 unenforceable.

- [x] T012 [US2] Run `cd specs && mise exec -- just test` — SC-009.

  Green, and `constitution-validate-sections.sh` returns `VALID=true` for all
  six projects. **Checkpoint**: this feature's own output is complete.
  Everything below opens other work.

______________________________________________________________________

## Phase 5: User Story 3 — opening the remaining units (Priority: P2)

**Goal**: the ten obliged units are started in the order the plan fixes, and the
hardest-fitting repository is not left to last.

**Independent test**: each task below creates a branch and invokes a skill
against the right project, and stops there.

**These four tasks open features. They do not write them.**

- [x] T013 [US3] Open `osapi`'s baseline: branch, then `speckit-specify` against
  `components/osapi` for a seven-section baseline. **It must not restate the
  1,840 lines already in that memory** from five archived features — its section
  4 is mostly citation, because osapi's contract is already stated and restating
  it is the second statement this whole programme forbids. First by FR-029,
  because it is the dependency hub and every other baseline's edges are stated
  against its section 2.

  **Merged as specs#169**, and it changed the programme's arithmetic. The
  baseline found three contributor pages the corpus backfill never looked at —
  `architecture/ui.md` at 264 lines, `development/ui-development.md` at 200, and
  `sdk/guidelines.md` at 227 — of which the first two have no corpus counterpart
  at all. So osapi needs a move after all: **twelve units, not eleven**,
  recorded as FR-030, and a new task T023 below.

  It also corrected osapi's page count from 221 to **219**: the 221 counted the
  Docusaurus project's own `README.md` and `SUPPORT.md` rather than published
  pages. The programme's classification total is 440.

  It did **not** restate the 1,840 lines already in osapi's memory. Its section
  4 is mostly citation and says why, which is what FR-010 of that baseline
  requires.

- [ ] T014 [US3] **After T013's baseline merges**, and not before, run T004's
  composition if it has not already run — see [research.md](research.md)
  Decision 5. The fragment lands between the first baseline and the remaining
  four: earlier binds six repositories to an untested shape, later leaves five
  baselines written against a specification rather than a rule.

- [ ] T015 [US3] Open `gohai`'s baseline **amendment** — not a new feature. It
  adds section 2, section 3, and the classification of its 68 documentation
  pages. Section 3 is the one to note: gohai's FR-016 excluded architecture
  *deliberately*, so the amendment reverses a judgement rather than filling a
  blank. SC-006 is satisfied by that amendment, not by this task: opening a
  feature is not carrying it out, and the check belongs to the amendment's own
  task list.

- [ ] T016 [US3] Open `osapi-justfiles`' baseline early rather than last, even
  though it is the smallest. It has no Go and no documentation pages, so it is
  the one repository that tests FR-011 and FR-013 — whether a section may be
  omitted and whether a contract can be stated for something that exposes no
  code. **If the shape cannot be filled there, the shape is wrong**, and finding
  that out after four conforming baselines is the expensive order.

**Checkpoint**: the programme is running under a fixed shape, with its riskiest
case tested early.

______________________________________________________________________

## Phase 6: The programme's exit criteria

**None of these six is a task this feature completes.** Every one needs
baselines that do not exist yet, so none can run until the other ten units have
merged. They are recorded here because a programme without a stated finish line
is one that gets abandoned rather than finished — and because four of them were
briefly filed as though this feature could run them, which would have meant
reporting a pass against zero baselines.

- [ ] T017 The SC-001 reading, from [quickstart.md](quickstart.md): a reader who
  has seen none of the baselines reads all six and answers what each repository
  is for, which depends on which and what would break, and where to look for how
  one is built. Question 2 is the one that fails if the baselines are six
  conforming documents that share a template rather than a set — each
  individually correct, the graph still untraceable, because section 2 was
  filled in as a formality.

- [ ] T018 [P] SC-002: every count in every baseline is paired with the command
  that reproduces it, and running the commands reproduces the counts or shows
  precisely which have drifted. A count whose command no longer reproduces it
  has **dated**, not failed; a count with no command beside it has failed.

- [ ] T019 [P] SC-003: no baseline contains a transcribed call graph, an
  exhaustive list of exported functions, or a file-by-file walkthrough. The
  check is the question in
  [contracts/section-order.md](contracts/section-order.md) under section 3,
  applied by a reviewer, because nothing automatable separates architecture from
  transcription.

- [ ] T020 [P] SC-004: every baseline's section 7 is non-empty. FR-004's
  evergreen bound guarantees every baseline excludes something, so a zero means
  the omission was not stated rather than that nothing was omitted.

- [ ] T021 [P] SC-007: every documentation page in every repository was
  classified by that repository's baseline before any move touched it — 442
  pages across the five that have any.

- [ ] T023 Open `osapi`'s **move** — the twelfth unit, which FR-027's table
  originally said was unnecessary. It relocates `architecture/ui.md` and
  `development/ui-development.md` into the corpus, and the part of
  `sdk/guidelines.md` that is not a demonstration of rules the corpus already
  states. Driven by the classification in specs#169, which is the ordering
  FR-026 requires and the one osapi got wrong the first time.

- [ ] T022 The SC-008 search: every documentation page still present in a
  repository is one its own baseline classified **user-facing**. Anything
  classified contributor-facing and still there is a rule stated twice, which is
  the state the programme exists to end and the only check that distinguishes a
  finished one from six inventories written beside the documentation they were
  meant to replace.

______________________________________________________________________

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1** has none.
- **Phase 2** blocks everything: T003 makes T002 binding, and T005 is what
  proves it.
- **Phase 3** (US1) and **Phase 4** (US2) are independent of each other and both
  depend on Phase 2.
- **Phase 5** (US3) depends on Phase 2, and T014 depends on T013 having merged.
- **Phase 6** depends on all ten obliged units, which are outside this feature.

### What is genuinely parallel

- T006 through T009 are one section of one file and are sequential in practice.
- T010 and T011 are reads of two different files.
- T013, T015 and T016 open three different projects and can run in any order or
  at once; only T014 is ordered, and only relative to T013.

### What only looks parallel

T002 and T003 touch different files and **must not be split across pull
requests**. A fragment merged without its manifest entry is a rule that binds
nothing, and it reads as authoritative for exactly as long as nobody checks.

______________________________________________________________________

## Implementation Strategy

### MVP

Phases 1, 2, 3 and 4 — one pull request. The fragment, the manifest entry, the
six recomposed constitutions, and the map. That is the whole of this feature's
own output and it is coherent alone: the shape binds and the graph is readable.

### Then

Phase 5 opens the remaining work in the fixed order, with `osapi` first because
it anchors everyone's edges and `osapi-justfiles` early because it is the case
most likely to prove the shape wrong.

______________________________________________________________________

## Notes

- No code changes in any repository. No documentation moves in this feature
  either — FR-016 and FR-027 put every move in its own feature.
- Eleven units in total, enumerated in [plan.md](plan.md). One is this feature,
  nine are new features, one is an amendment to gohai's merged baseline.
- **442** documentation pages will be classified by the baselines, none of them
  here. Not 221 — that is `osapi`'s own count, and coincidentally also the total
  for the four repositories still needing a move. The two are different
  quantities that share a figure.
