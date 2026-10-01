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

  **Archived 2026-09-30, and last of the seven rather than first.** It had no
  `plan.md` for a day — stage 1 merged and stages 3 and 4 were skipped — and the
  archival gate requires one, so six features reached osapi's memory before the
  one that says what the repository is, including the embedded UI whose
  specification depends on this baseline's classification. Plan and tasks at
  specs#186, archival at specs#187. FR-113 through FR-133 sit **first** in that
  memory's requirements, before FR-001, because `global/baseline` requires it.

- [x] T014 [US3] **After T013's baseline merges**, and not before, run T004's
  composition if it has not already run — see [research.md](research.md)
  Decision 5. The fragment lands between the first baseline and the remaining
  four: earlier binds six repositories to an untested shape, later leaves five
  baselines written against a specification rather than a rule.

  **Already satisfied, and in the right order.** T004 composed the fragment into
  all six constitutions and T005 confirmed it. osapi's baseline merged at
  specs#169 before that, so the ordering Decision 5 requires held without a
  second composition being needed. Verify with
  `grep -c '^## Baseline' components/*/.specify/memory/constitution.md` — six
  files, one each.

- [x] T015 [US3] Open `gohai`'s baseline **amendment** — not a new feature. It
  adds section 2, section 3, and the classification of its 68 documentation
  pages. **Done.** The classification merged at specs#205 and sections 2 and 3
  at #209. Splitting it that way was not the plan and is worth recording: the
  classification was self-contained and the two missing sections are not, so
  holding the smaller half back would have delayed a finding for nothing.
  gohai's memory already carries both subjects, written during the memory tree
  work, so what the amendment owes is the baseline's own statement of them
  rather than the knowledge. Section 3 is the one to note: gohai's FR-016
  excluded architecture *deliberately*, so the amendment reverses a judgement
  rather than filling a blank. SC-006 is satisfied by that amendment, not by
  this task: opening a feature is not carrying it out, and the check belongs to
  the amendment's own task list.

- [x] T016 [US3] Open `osapi-justfiles`' baseline early rather than last, even
  though it is the smallest. It has no Go and no documentation pages, so it is
  the one repository that tests FR-011 and FR-013 — whether a section may be
  omitted and whether a contract can be stated for something that exposes no
  code. **If the shape cannot be filled there, the shape is wrong**, and finding
  that out after four conforming baselines is the expensive order.

  **Done, and the shape held.** Specified at specs#178, planned and tasked at
  #180, archived 2026-09-30. **No section was omitted**, so FR-011's allowance
  was never exercised — and that is the answer this unit existed for. FR-013 was
  the one that needed work: "the contract" reads as though it presumes exported
  symbols, and the baseline had to decide that 38 recipe names and twenty
  variable names are one. They are, by every test that matters, and the bound
  stated so the word does not become unbounded for the four baselines after it
  is *something a consumer's build breaks on*.

  It also produced three amendments to this feature — FR-032, FR-033 and FR-034
  at specs#184 — and one finding it handed back rather than fixing: whether
  `global/baseline` should say what a contract means for a repository exposing
  no code, and whether a baseline should carry the shape finding at all, since
  the SC-001 reading judged that the two deliverables in one document serve a
  consumer worse. Both are this feature's to decide.

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

- [x] T017 The SC-001 reading, from [quickstart.md](quickstart.md): a reader who
  has seen none of the baselines reads all six and answers what each repository
  is for, which depends on which and what would break, and where to look for how
  one is built. Question 2 is the one that fails if the baselines are six
  conforming documents that share a template rather than a set — each
  individually correct, the graph still untraceable, because section 2 was
  filled in as a formality.

  **Done 2026-09-30. Question 1 passes, question 2 passes, question 3 is
  partial.** The reading answered the graph from the text, with every Go edge
  stated from both ends and every build edge in `osapi-justfiles`' FR-004, and
  it reconstructed what breaks on each edge including the delayed shape that
  pinning by pseudo-version produces. Question 3 is partial by design: the
  recipe contract, the variables, the fetch mechanism and the pinning situation
  are all stated precisely, while CI workflows, recipe internals, binary
  production and toolchain versions are excluded. The reader's own summary of
  that: "I can tell you what `just test` resolves to and not what it runs."

  Its verdict on the set: **one set, converged onto rather than born as one.**
  The evidence it gave was not the shared template, which it dismissed, but that
  the documents report on their own propagation. `osapi-justfiles` records three
  headings drifting and corrects them, `nats-client` says it kept them right by
  copying the corrected file rather than re-deriving, and `nats-server` and
  `osapi-orchestrator` count the hops. Four of the six also declare their own
  reading order in their preambles, and all six file findings against each other
  and against this feature with owners rather than fixing them in place.

  **Nine defects, all fixed at specs#212.** Ordered by what each cost a reader:

  | Defect                                                      | Where                    |
  | ----------------------------------------------------------- | ------------------------ |
  | A citation to `FR-115`, which does not exist, twice         | `nats-client`            |
  | Two documents disagreeing about which repository is the hub | `osapi-justfiles` FR-003 |
  | Five requirements filed inside Success Criteria             | `gohai`, from specs#205  |
  | A move size stale against an amendment one day older        | `gohai` FR-020           |
  | Nine counts whose command needs the row above it            | three baselines          |
  | A fourth gap invisible to anyone reading section 6          | `nats-server`, from #207 |
  | "five exclusions" where six are listed                      | `osapi` SC-004           |
  | "three gaps" where four are stated                          | `osapi-justfiles` SC-005 |
  | "three exported types" beside a table saying four           | `nats-server` FR-012     |

  The first is the one worth keeping. Four documents claim their edges are
  "verified from both ends", and at the single place where one of them links to
  the other end, it links to a requirement that has never existed. Nobody
  followed the link, including the reviews that merged it. A claim about
  verification that is itself unverified is the exact failure this programme
  exists to catch, and it took a reader restricted to the text to find it.

  Two of the nine were introduced by amendments **this programme** made in the
  last two days, which is the honest cost of correcting merged documents: a
  block appended before the wrong heading, and a gap filed in the section whose
  count it corrects rather than the section that lists gaps.

  **What the reading could not get, and it is not a defect list.** Nothing in
  the six says what the product is *for*. Six documents and roughly 3,400 lines
  describe the machine, and osapi's FR-017 excludes what any domain or provider
  does, so a reader finishes knowing the shape of osapi and not its purpose. The
  reader's words: "I can describe the machine and not the job." Also absent: a
  definition of "the corpus", which is the subject of nearly every requirement
  in all six; and the programme's other units, since four of the six carry a
  unit number while units 1 to 5 and 10 to 12 are named nowhere.
  `osapi-justfiles`' FR-022a recorded that complaint about itself and assigned
  it here. Owner: this feature, and it is the strongest argument yet that a
  reader who needs an entry point should be given memory rather than the
  baselines.

- [x] T018 [P] SC-002: every count in every baseline is paired with the command
  that reproduces it, and running the commands reproduces the counts or shows
  precisely which have drifted. A count whose command no longer reproduces it
  has **dated**, not failed; a count with no command beside it has failed.

  **Done 2026-09-30.** 35 commands extracted from the six baselines and run in
  the repository each describes. Every one reproduces its count except one,
  which had failed rather than dated. **The pass also missed a second class
  entirely**, which T017's reading found: nine rows across three baselines gave
  their command as "the same, plus ..." or "the same, with ...", inheriting the
  row above. The extractor skipped those rather than reporting them, so "every
  command reproduces" was true of the commands it ran and silent about nine it
  did not. `just memory-check` has treated that form as a defect since it was
  written, on the ground that a count whose command needs the row above it
  cannot be checked alone, and the baselines were held to a weaker standard than
  memory for no reason anybody had stated. All nine are now self-contained and
  all nine reproduce, taking the baselines from 35 runnable commands to 44.

  The one that had failed outright: `osapi`'s SDK method count gave
  `grep -cE ... pkg/sdk/client/*.go` followed by the word "summed" outside the
  backticks. `grep -c` over many files prints a count per file, so the command
  as written produces no number at all. The count itself, 117, is right. Fixed
  to `grep -hE ... | wc -l`.

  The same pass found the count **hedged** in osapi's memory, as "roughly 110
  exported methods" where the figure is exact and reproducible. That is the
  defect `osapi-justfiles`' FR-013b recorded in its own variable count,
  appearing a second time, which is the argument for a check rather than a
  convention.

  **The standing guarantee is memory's, not the baselines'.** A baseline records
  what was true at a commit, so drift in it is expected and gating it would be
  wrong. Memory is the current description, so `just memory-check` runs every
  count in it on every test run. That check had two holes this task exposed:

  | Hole                                          | Counts covered |
  | --------------------------------------------- | -------------: |
  | before                                        |             53 |
  | it only read measurement **tables**           |             55 |
  | its glob stopped at `memory/*.md`, not deeper |             62 |

  The second was the serious one. Every subject document lives in
  `memory/architecture/`, one directory below the pattern, so the check had
  never looked at a single one of them while reporting a total that read as
  complete.

- [x] T019 [P] SC-003: no baseline contains a transcribed call graph, an
  exhaustive list of exported functions, or a file-by-file walkthrough. The
  check is the question in
  [contracts/section-order.md](contracts/section-order.md) under section 3,
  applied by a reviewer, because nothing automatable separates architecture from
  transcription.

  **Passes, 2026-09-30, with one thing worth naming.** No baseline transcribes a
  call graph or walks files. The largest surfaces are stated as rules rather
  than as lists: `osapi`'s 117 SDK methods become five naming rules derived from
  them, and `osapi-orchestrator`'s 101 operations become one sentence plus a
  page each.

  What comes closest to a list is an **enumerated vocabulary**: gohai's eight
  registry functions, the orchestrator's eight guards and ten predicates. Each
  is the complete set a consumer has to know, short enough to read, and closed
  by constants in the code. The test that separates it from transcription is
  whether a reader needs the whole set to use the thing. For a vocabulary they
  do, and for 117 methods they do not.

- [x] T020 [P] SC-004: every baseline's section 7 is non-empty. FR-004's
  evergreen bound guarantees every baseline excludes something, so a zero means
  the omission was not stated rather than that nothing was omitted.

  **Passes, 2026-09-30.** All six, at 6, 9, 16, 19, 23 and 65 non-blank lines
  for gohai, osapi-orchestrator, osapi, nats-client, nats-server and
  osapi-justfiles. The order is worth a glance: `osapi-justfiles` has no Go at
  all and excludes the most, because a repository whose contract is 38 recipe
  names has to say what a recipe does *not* promise. Size predicted nothing here
  either.

  **Unit 8 done, 2026-09-30.** `nats-server` baselined at specs#191, amended at
  #192, archived at #193. Its findings came from reading `Start()` in order
  rather than from counting — a statement order, two literal arguments, and an
  absent statement — and its SC-001 reading passed three of three, the first
  clean reading in the programme. It also drew a **different** coherence verdict
  from the two before it: one argument rather than a checklist with footnotes.

  **Unit 7 done, 2026-09-30.** `nats-client` baselined at specs#188, amended at
  #189 and archived at #190. Its reading found something a command could not: an
  acceptance scenario promising a behaviour the specification never stated. Two
  counts were also wrong, both missing an exclusion. Remaining: `nats-server`,
  `osapi-orchestrator`, gohai's amendment, and the moves.

- [x] T021 [P] SC-007: every documentation page in every repository was
  classified by that repository's baseline before any move touched it — 440
  pages across the five that have any. **Done.** osapi at specs#169, gohai at
  #205, osapi-orchestrator at #206, and both nats repositories at #207. Three of
  those four were amendments to baselines that predated FR-025, which is the
  cost of fixing the shape after four baselines had merged. The results
  contradict FR-027's prediction for three of six repositories and are recorded
  as FR-035.

- [~] T023 Open `osapi`'s **move** — the twelfth unit, which FR-027's table
  originally said was unnecessary. It relocates `architecture/ui.md` and
  `development/ui-development.md` into the corpus, and the part of
  `sdk/guidelines.md` that is not a demonstration of rules the corpus already
  states. Driven by the classification in specs#169, which is the ordering
  FR-026 requires and the one osapi got wrong the first time.

  **Two of three pages done, and the box stays open until the third is.**
  `007-the-embedded-ui` moved the two UI pages: specified at specs#172, planned
  at specs#173, implemented at osapi#549, corrected at specs#175 and osapi#550.
  It did **not** touch `sdk/guidelines.md`, which 006's FR-015 classifies as
  *partly* moving — its rules are 005's FR-019 and FR-020 and the page rightly
  demonstrates them, but the package structure and the response pattern have no
  counterpart anywhere. That remainder is a feature of its own and it is not
  open yet. Ticking this on the UI move alone would have recorded a third of a
  page family as a whole one.

  **Partly done, 2026-09-30.** The UI half is carried out: three statements of
  264, 200 and 263 lines are now 82, 52 and 9, the last a pointer whose own text
  says it is a pointer. What remains is `sdk/guidelines.md`'s non-demonstration
  part, roughly 100 lines of package structure and response pattern, which has
  no corpus counterpart and no feature open. Owner: `osapi`.

- [ ] T022 The SC-008 search: every documentation page still present in a
  repository is one its own baseline classified **user-facing**. Anything
  classified contributor-facing and still there is a rule stated twice, which is
  the state the programme exists to end and the only check that distinguishes a
  finished one from six inventories written beside the documentation they were
  meant to replace.

  **Blocked, and the residue is measured, 2026-09-30.** The search runs; it
  cannot pass, because two moves have not happened. What is still in a
  repository after its own baseline classified it contributor-facing:

  | Page                               | Lines | State                              |
  | ---------------------------------- | ----: | ---------------------------------- |
  | `gohai/docs/methodology.md`        |   382 | untouched                          |
  | `gohai/docs/adding-a-collector.md` |   280 | untouched                          |
  | `gohai/docs/ocsf-validation.md`    |   107 | untouched                          |
  | `osapi`'s `sdk/guidelines.md`      |   227 | the non-demonstration part is owed |

  ```sh
  cd ~/git/osapi-io && wc -l gohai/docs/methodology.md \
    gohai/docs/adding-a-collector.md gohai/docs/ocsf-validation.md \
    osapi/docs/docs/sidebar/sdk/guidelines.md
  ```

  **osapi's UI move is done**, which this task list never recorded. Its three
  statements were 264, 200 and 263 lines and are now 82, 52 and 9: the site page
  reduced to the operator's half, the development page likewise, and
  `ui/docs/architecture.md` a nine-line pointer whose own text says it is a
  pointer and not a summary, and why. That is the shape FR-027 asks for, and it
  is the only one of the moves carried out so far.

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
- **440** documentation pages will be classified by the baselines, none of them
  here. Not 442, which used `osapi`'s pre-correction 221; see FR-031 and FR-038.
  And not 221 — that is `osapi`'s own count, which the four other repositories
  also totalled before the correction. The collision is what made the stale
  figure findable, and correcting `osapi` to 219 is what broke it.
