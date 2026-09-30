# Feature Specification: One shape for every component baseline

**Feature Branch**: `002-baseline-shape`

**Created**: 2026-09-29

**Status**: Draft

**Input**: Six repositories need a baseline and one has been written. The goal
is that somebody reads one component's memory, then the next, and understands
how the organization fits together. gohai's baseline cannot serve that goal,
because its FR-016 deliberately excludes architecture. Five more in the same
shape would make the inconsistency permanent.

## Why this is a system feature

Nothing currently governs what a baseline contains. The charter has seven
fragments and the nearest, `global/workflow`, states only *where* design output
goes — "a feature under the project's `specs/`, consolidated into
`.specify/memory/` when it merges" — not what a baseline holds. So the shape was
undefined, and the first one came out shaped by whoever wrote it.

A required shape is not one repository's behaviour. It is an agreement every
component project honours, which is the test CONTRIBUTING sets under "Where a
change belongs", so it is a `system` feature. It produces a charter fragment as
its enforceable residue — FR-014.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The set reads as one thing (Priority: P1)

Somebody new reads each component's memory in turn. By the end they can say what
every repository is for, what depends on what, and where a change to one would
be felt in another. They get that from the baselines alone, without opening six
repositories.

**Why this priority**: it is the goal. Six inventories that each answer a
different question are six documents; six that answer the same questions in the
same order are a map.

**Independent Test**: a reader who has read none of them reads all of them and
states each repository's purpose and the dependency edges between them.

**Acceptance Scenarios**:

1. **Given** the six baselines, **When** a reader asks what a repository is for,
   **Then** the answer is in the same section of each one.
2. **Given** the six baselines, **When** a reader asks what would break if a
   repository changed, **Then** each baseline names what depends on it and what
   it depends on, so the reader can trace the edge from either end.
3. **Given** a baseline that omits a section, **When** a reader notices,
   **Then** the baseline says which section it omitted and why, so an omission
   is never indistinguishable from an oversight.

______________________________________________________________________

### User Story 2 - A baseline survives ordinary change (Priority: P1)

Somebody reads a baseline six months after it was written and finds it still
true, or finds the one command that proves it is not.

**Why this priority**: evergreen is the whole point. A baseline that transcribes
a call graph is wrong within a month, and a wrong baseline is worse than none
because it carries the authority of a specification.

**Independent Test**: every count in a baseline is paired with a command, and
running the commands reproduces the counts or shows exactly which drifted.

**Acceptance Scenarios**:

1. **Given** a count in a baseline, **When** its command is run, **Then** it
   produces that number or the difference is visible immediately.
2. **Given** an architectural statement in a baseline, **When** a function is
   renamed or a file moved, **Then** the statement is still true, because it
   states what the parts are *for* rather than transcribing their names.

______________________________________________________________________

### User Story 3 - A repository that is not a Go library still fits (Priority: P2)

Somebody baselines `osapi-justfiles`, which has no Go code at all, and the shape
accommodates it without pretending it has interfaces.

**Why this priority**: one of the six is not a Go library. A shape that only
fits five is not a shape.

**Independent Test**: the shape's required sections can be filled for a
repository of shared build recipes, and any section that genuinely does not
apply is omitted with a stated reason.

**Acceptance Scenarios**:

1. **Given** a repository with no exported code surface, **When** its baseline
   is written, **Then** the contract section states what consumers actually
   depend on — recipe names and their behaviour — rather than being left blank
   or filled with nothing.

### Edge Cases

- **A repository nothing depends on and which depends on nothing.** `gohai` is
  one today. Its dependency section says so explicitly rather than being
  omitted: "no edges" is information, and an absent section reads as unfinished.
- **A repository whose prose is better than its code coverage.**
  `osapi-orchestrator` has 140 doc pages against 81 Go files. The baseline cites
  rather than duplicates, and the risk there is copying, not omitting.
- **A repository with almost no prose.** `nats-server` has 12 Go files and 5 doc
  pages. Its baseline is close to the only statement that exists, which makes
  the verification discipline matter more rather than less.
- **The shape changes after some baselines are written.** It already has:
  gohai's predates this. A shape revision does not silently invalidate what
  exists; it obliges an amendment per FR-015.
- **A section that is required but whose content is genuinely empty.**
  Distinguished from "not applicable": an empty required section states that it
  is empty and what that means, and only a section the repository's nature makes
  meaningless may be omitted.

## Requirements *(mandatory)*

### The required sections

- **FR-001**: A component baseline MUST carry these seven sections, in this
  order. The order is part of the agreement: a reader moving between baselines
  finds the same answer in the same place.

  | #   | Section                          | Answers                                                                   |
  | --- | -------------------------------- | ------------------------------------------------------------------------- |
  | 1   | **What this repository is**      | Its purpose in one paragraph, and who consumes it                         |
  | 2   | **Where it sits**                | What it depends on, what depends on it, and what breaks in each direction |
  | 3   | **Architecture**                 | The parts, what each is for, and what flows between them                  |
  | 4   | **The contract**                 | What a consumer may depend on, and what is free to change                 |
  | 5   | **Measurements**                 | Counts, each with the command that reproduces it                          |
  | 6   | **Gaps**                         | Where the repository's own prose and its code disagree, with an owner     |
  | 7   | **What this inventory excludes** | Named omissions, so a gap is never mistaken for an oversight              |

- **FR-002**: Section 2, **Where it sits**, MUST name both directions — upstream
  and downstream — even when one is empty, and MUST state what a change would
  break in each. This is the section that turns six documents into a map, and it
  is the one gohai's baseline has no equivalent of.

- **FR-003**: Section 3, **Architecture**, MUST be present in every component
  baseline. gohai's FR-016 excluded architecture on the grounds that the
  contract was what mattered; that judgement was wrong for the goal and this
  requirement reverses it.

### How much architecture, so it stays evergreen

- **FR-004**: An architectural statement MUST be at the level of **what a part
  is for and what passes between parts**, not at the level of names that change.
  A baseline states that an agent receives work through a queue and returns a
  result through a store; it does not transcribe the call chain that implements
  it.
- **FR-005**: A baseline MUST NOT contain a transcribed call graph, a list of
  every exported function, or a file-by-file walkthrough. Each is wrong within a
  month, and each is already obtainable from the code faster than from prose.
- **FR-006**: Where an architectural statement names a symbol or a path, it MUST
  name it as **evidence for the statement** rather than as the statement itself,
  so a rename dates the citation without falsifying the claim.

### The verification discipline, as a rule rather than a habit

These four came out of gohai's baseline. Applied there they produced three real
defects in gohai's own documentation, so they bind rather than depending on
whoever writes the next one.

- **FR-007**: Every count in a baseline MUST be paired with the command that
  reproduces it. A bare number is a claim; a number with its command is a
  measurement.
- **FR-008**: A repository's own prose — its README, its `docs/`, its
  `CONTRIBUTING.md` — is a **lead, not a source**. A baseline states what the
  code does, and consults the prose to find disagreements.
- **FR-009**: The reading order MUST be **code first, counts by command, prose
  last**. This is the reverse of the tempting order and it is load-bearing:
  gohai's README said 65 collectors and 9 categories where the code had 62 and
  10, and reading the prose first would have produced an inventory stating both
  wrong numbers with the code never consulted.
- **FR-010**: A disagreement between a repository's prose and its code MUST be
  recorded as a **gap naming both sides and an owner**, never silently
  corrected. The baseline describes; correcting the repository is that
  repository's own change.

### Fitting every repository, including the one that is not a library

- **FR-011**: The seven sections are **required by default and omissible only
  where the repository's nature makes a section meaningless** — not where it is
  merely hard, and not where the writer ran out of time.
- **FR-012**: A baseline that omits a section MUST say so in section 7 and state
  why. An unstated omission is indistinguishable from an oversight, which is the
  failure section 7 exists to prevent.
- **FR-013**: For a repository with no exported code surface, the **contract**
  section MUST state what consumers actually depend on in that repository's own
  terms. `osapi-justfiles` has no Go files; what six repositories depend on is
  its recipe names and their behaviour, so that is its contract.

### What this produces, and what it obliges

- **FR-014**: This design MUST produce a charter fragment, because the shape
  binds every component from now on and a design alone binds nothing. The
  fragment's rule is one line: *a component's baseline states what the
  repository is, where it sits among the others, its architecture, its contract,
  its measurements with the commands that reproduce them, its gaps, and its
  omissions.* The reasoning stays here; the fragment is the enforceable residue.
- **FR-015**: gohai's baseline MUST be amended to match this shape, in **its own
  change**, because it is merged and archived and a correction to a merged
  statement is never folded into the change that discovered it. It is missing
  sections 2 and 3 — where it sits, and architecture.

### Voice

- **FR-017**: A baseline MUST be written in **ordinary prose**. It MUST NOT use
  Given/When/Then acceptance-scenario form, checklist scaffolding, or any other
  testing formalism as its body. Those belong to a feature specification, which
  is read once by a reviewer; a baseline is read repeatedly by somebody trying
  to understand a repository, and a formalism that helps a reviewer check a
  change actively obstructs a reader trying to learn a system.

  This specification itself uses Given/When/Then, because the spec template
  requires it of a feature. That is not a licence for the document it describes:
  the two are different kinds of writing with different readers, and conflating
  them is how memory comes to read like a test plan.

- **FR-018**: A baseline MUST read as continuous explanation rather than as a
  table of fields. Tables are for what is genuinely tabular — a dependency list,
  a set of counts with their commands — and prose is for everything else. A
  baseline that is entirely tables states facts without saying how they relate,
  which is the one thing a reader cannot get from the code.

- **FR-017a**: FR-017 and FR-018 bind **what archival writes into
  `.specify/memory/`**, not only the feature specification that produces it.
  Five archivals read them as the latter and the result is that memory holds the
  formalism FR-017 forbids.

  **What went wrong, precisely.** A baseline's feature specification
  legitimately carries user stories with priorities, acceptance scenarios and
  success criteria — that is how a change gets reviewed, and nothing here
  objects to it. Archival then copied those sections into memory unchanged, so
  `components/nats-client/.specify/memory/spec.md` opens with
  `## User Scenarios & Testing`, holds `User Story 2 … (Priority: P1)`, and
  states `SC-006: just test passes in the specs repository` — a sentence with no
  meaning in a document about what `nats-client` is. The seven sections a reader
  wants sit two levels below, under `### Functional Requirements`, each phrased
  "the corpus MUST state that…".

  A reader who wants to know what the repository is must mentally delete "the
  corpus MUST state that" from every sentence and skip past the process
  furniture to reach it. That is the obstruction FR-017 describes, and it is in
  the file FR-017 exists to protect.

- **FR-017b**: Archived memory MUST take this shape, because "prose" alone was
  not specific enough to prevent FR-017a:

  | File             | Holds                                                                                 |
  | ---------------- | ------------------------------------------------------------------------------------- |
  | `memory/spec.md` | The **seven sections at top level**, as declarative prose. What the repository *is*.  |
  | `memory/plan.md` | How it was established, what was decided, and what remains unverified. How we *know*. |

  Three rules follow, and each names something a completed archival did wrong:

  1. **Declarative, not normative.** "`nats-server` runs a NATS server inside
     its consumer's process" — not "the corpus MUST state that it runs…". The
     `MUST` belongs to the feature specification, where it obliges somebody to
     write something. In memory the writing has happened, so the obligation is
     spent and only the fact remains.

  2. **No feature-process furniture.** User stories, priorities, acceptance
     scenarios and success criteria do not reach memory. They record how a
     change was reviewed; the changelog already records that the change
     happened. Neither do **requirement identifiers in the body**. `FR-` labels
     were kept on the first attempt, justified by site pages and skills citing
     the corpus by requirement ID — and checking that showed the citations point
     at *feature specifications*, 22 of them across the skills, and that
     **nothing anywhere cites a memory requirement number**. The justification
     was a guess about where a verified fact applied.

  3. **Traceability is one line at the end, not a footer on every paragraph.**
     Memory names the feature it came from once. A reader who wants to know
     which requirement obliged a sentence reads that feature.

  4. **The voice is the architecture documentation this programme has been
     moving.** `global/baseline` carries it in full. In short: a heading names
     the thing, with its path where a path helps; a statement is present tense
     and made once; a design decision carries its reason beside the thing it
     explains; and commentary about the document never appears — not how a fact
     was found, not that a fact is important, not what an earlier version said.
     Show a configuration block, a directory tree or a command where showing it
     is shorter than describing it.

     The calibration is osapi's `system-architecture.md`, which explains that
     the liveness probe is deliberately trivial because dependency checks there
     would make orchestrators restart the process during a transient NATS outage
     — a restart storm on top of the original problem — and then tells the
     reader to use readiness for load balancing instead. One sentence of reason
     about the system, and guidance that can be acted on.

  A reader arriving at `memory/spec.md` should be able to read straight down and
  learn the system. **Seven headings in the right order is not sufficient to
  pass that test**: the first attempt produced exactly that, filled with
  labelled requirement bullets and citation footers, and it read as a
  specification with better navigation.

### What stitches the set together

- **FR-019**: `system`'s own memory MUST hold the **cross-repository map**:
  every repository, one line on what it is for, and every dependency edge. Each
  component baseline states its own edges (FR-002), and that is what keeps them
  true; the map is what lets a reader see the whole graph without reading six
  documents first.

  Both are required and neither replaces the other. The map alone goes stale
  because nothing forces it to match; the edges alone never compose into a
  picture. Together, each baseline is checkable against the map and the map is
  derivable from the baselines.

- **FR-020**: One baseline serves as the **worked example**, and it MUST be
  named in the map so a reader knows where to start. `gohai` is the one, for the
  reason it was chosen to go first: it depends on nothing and nothing depends on
  it, so it can be read without holding any other repository in mind. A reader
  learns the shape there and then reads the rest knowing what to expect in each
  section.

### Every repository, and what `system` is instead

- **FR-021**: Every repository MUST have a baseline, **`osapi` included**. Its
  five archived features are not one: they record what changed, not what the
  repository is. A reader arriving at `osapi`'s memory today finds requirements
  about job delivery and provider contracts, and no statement of what `osapi` is
  for or what it depends on — exactly the gap this shape exists to close.

  The two coexist. A baseline states what the repository is; archived features
  state what was decided about it. Neither replaces the other, and `osapi`'s
  baseline will be the largest of the six because it is the largest repository.

- **FR-022**: `system` MUST NOT have a baseline, because it is not a repository.
  It maps to no codebase, and its subject is what the repositories agree on
  rather than how any one of them behaves. What it holds instead is the
  cross-repository map (FR-019) and the agreements no single repository owns —
  this specification being one of them.

  Stating this matters because "every project gets a baseline" would otherwise
  read as including `system`, and a baseline of a project with no code would
  have to invent its own subject.

### Consistency beyond the corpus

- **FR-023**: The corpus MUST record where the repositories' **own documentation
  tooling** is consistent and where it is not, because a reader comparing two
  baselines will ask why one repository's documentation is checked more
  thoroughly than another's. Measured 2026-09-29:

  | Repository           | Doc pages | Built  | Link-checked |
  | -------------------- | --------- | ------ | ------------ |
  | `osapi`              | 221       | yes    | yes          |
  | `osapi-orchestrator` | 140       | **no** | **no**       |
  | `gohai`              | 68        | **no** | **no**       |
  | `nats-client`        | 8         | no     | no           |
  | `nats-server`        | 5         | no     | no           |
  | `osapi-justfiles`    | 0         | n/a    | n/a          |

  The rest of the build tooling is uniform, and the corpus MUST say so rather
  than implying drift: the four Go repositories fetch the same `go`, `just` and
  `md` justfile modules and run the same nine workflows. `osapi-justfiles`
  differs only by having no Go, and `osapi` only by having a published site.
  Both differences track a real difference in the repository.

- **FR-024**: **Gap**: 208 documentation pages across `osapi-orchestrator` and
  `gohai` have no build and no link checking — markdown formatting alone is
  enforced, so a broken internal link is never caught, where `osapi`'s 221 pages
  are checked by its site build. Owner: those two repositories, each in its own
  change. Recorded here rather than fixed, because this feature states a
  document shape and changes no repository.

### Classifying a repository's own documentation

The osapi backfill and gohai's baseline were **two different operations**, and
under one shape they cannot both be right. osapi's contributor documentation
moved out of its site into the corpus and the pages were deleted or reduced;
gohai's was left where it was and cited. The first obeys the one-statement rule;
the second leaves the same knowledge in two places, which is the drift
`global/documentation` forbids and the backfill existed to end.

So the move is the right operation everywhere — and the ordering osapi used was
wrong.

- **FR-025**: A baseline MUST classify **every page** of its repository's own
  documentation as **user-facing** or **contributor-facing**, and the test is
  the one the osapi backfill used: *who reads this page* — somebody using the
  repository, or somebody changing it — not where the page currently sits.

  This classification belongs in the baseline rather than in a separate audit,
  because the baseline is the document that establishes what the repository is
  for and who consumes it. Deciding it page-by-page during a move is how a
  remainder page gets produced and how user-facing content gets taken away by
  accident.

- **FR-026**: The baseline MUST come **before** the move. osapi did the reverse
  — its contributor documentation was backfilled across three features and it
  still has no baseline, which is the gap FR-021 exists to close. The baseline
  is what tells a reader which pages are contributor-facing; running the move
  first means deciding that mid-change with nothing to check the decision
  against.

- **FR-027**: Moving a repository's contributor documentation into the corpus
  MUST be its **own feature**, separate from the baseline that classified it,
  and MUST leave every address resolving — a short index, a redirect, or a
  reduced page that reads as a whole rather than as a remainder. This is the
  sequence osapi's backfill proved: the corpus statement merges first, then the
  repository change that removes the duplicate.

  Two repositories therefore have two features each and one has only a baseline:

  | Repository           | Doc pages | Baseline                       | Move                          |
  | -------------------- | --------- | ------------------------------ | ----------------------------- |
  | `osapi`              | 219       | done — specs#169               | **needed** — see FR-030       |
  | `osapi-orchestrator` | 140       | needed                         | needed, the largest remaining |
  | `gohai`              | 68        | exists, needs sections 2 and 3 | needed                        |
  | `nats-client`        | 8         | needed                         | likely small                  |
  | `nats-server`        | 5         | needed                         | likely small                  |
  | `osapi-justfiles`    | 0         | needed                         | none — nothing to move        |

- **FR-028**: A page a repository's consumers read MUST stay in that repository.
  Not everything in a `docs/` tree is contributor knowledge:
  `gohai/docs/collectors/` is a 65-row catalogue for people *using* the library,
  and gohai's own baseline already cites it as the maintained enumeration its
  FR-004 depends on. Moving it would take a user's reference away and break the
  citation in the same stroke.

- **FR-029**: The order across the six repositories MUST start with **`osapi`**,
  because it is the hub of the dependency graph — `nats-client` and
  `nats-server` below it, `osapi-orchestrator` above — so its "where it sits" is
  what every other baseline's edges are stated against. A leaf baselined first
  has nothing to point at.

### Corrected: twelve units, not eleven

- **FR-030**: osapi needs a **move** after all, so the programme is **twelve**
  units rather than eleven. This corrects FR-027's table, which said osapi's
  move was "already done, across three features".

  That was true of the six pages the corpus backfill scoped and false of three
  it never looked at. osapi's own baseline found them — `architecture/ui.md` at
  264 lines, `development/ui-development.md` at 200, and `sdk/guidelines.md` at
  227\. The first two have **no corpus counterpart at all**: 464 lines of
  contributor architecture on an operator's site with nowhere to cite, which is
  the state the backfill existed to end.

  They survived because the backfill named six candidate pages and classified
  those. Nothing examined a page that was not a candidate, and an inventory
  re-checking only those six would have missed them the same way. **That is the
  argument for baselining a repository that already has memory**, and it is why
  FR-026 puts the baseline before the move rather than treating a completed move
  as evidence that nothing remains.

- **FR-032**: `osapi-justfiles` has **no documentation pages and six
  documentation files**, and FR-023's table recording 0 for it answers only the
  first half. There is no `docs/` tree, so 0 is exactly right about pages — and
  misleading as an answer to "what documentation does this repository have",
  because five module READMEs and a root README are its documentation. They stay
  where they are, for FR-028's reason: a module's README documents the interface
  of the file beside it, and moving it would separate an interface from its
  description.

  Found by `osapi-justfiles`' own baseline, specs#178, and recorded there as its
  FR-019 before being amended here.

- **FR-033**: `osapi-justfiles` is depended on by **seven** repositories, not
  six. FR-019's map and this specification both said six, meaning the six
  components; the seventh is **`specs`**, the design record, which fetches the
  `just` and `md` modules. Only `.github` has no justfile.

  **The map carried the command that would have produced the right answer.**
  `grep -n justfiles */justfile`, run from the directory holding the clones,
  returns `specs` among the rest. The figure beside it said six. So this is not
  the failure `global/repositories` describes — a written list correct when
  written and wrong afterwards — it is a list that was **wrong when written**,
  because the writer's frame was the six components rather than the repositories
  the command returns. Ageing was not the problem. Nobody running the command
  was.

  It changes which module matters most: `md` reaches all seven, `just` six, `go`
  five, and `react` and `docusaurus` one each. And it puts the design record's
  own formatting gate downstream of an unpinned fetch — `specs`' `just test`
  gates every corpus change in the organization, and a commit to
  `osapi-justfiles` changes it. That is FR-024's existing finding reaching
  further than FR-024 said.

- **FR-034**: The programme's scope is the **six components**, and the
  organization has **eight** non-archived public repositories. The two outside
  the programme are `specs`, which is where components are described rather than
  a component, and `.github`, which holds shared configuration and no justfile.
  Neither gets a baseline, and this is stated because FR-033 shows what happens
  when the difference between "the six" and "the repositories" is left implicit:
  it was the frame that produced the wrong consumer count.

- **FR-031**: `osapi`'s page count is **219 published pages**, not 221. FR-023's
  table records 221, which counts `docs/README.md` and `docs/SUPPORT.md` — the
  Docusaurus project's own files rather than published pages. Both figures are
  right about different questions, and the programme's classification total is
  therefore **440** rather than 442.

  This is the **second** number collision this feature has produced, after the
  221-against-442 one the analysis pass caught. Both had the same shape: a
  figure correct for one question, quietly reused for another. Worth recording
  as a pattern rather than as two incidents, because the next baseline will
  offer the same opportunity.

### Corrected: what the classifications found

All five repositories with documentation have now been classified, at specs#169,
#205, #206 and #207. FR-027's table predicted the result and was wrong about
half of it.

- **FR-035**: FR-027's table MUST be read with this correction. It is kept as
  written because what it got wrong is the finding.

  | Repository           | Pages | FR-027 predicted      | Classified                |
  | -------------------- | ----: | --------------------- | ------------------------- |
  | `osapi`              |   219 | needed, see FR-030    | **2 pages move**, 1 split |
  | `osapi-orchestrator` |   140 | the largest remaining | **nothing moves**         |
  | `gohai`              |    68 | needed                | **3 pages move**          |
  | `nats-client`        |     8 | likely small          | **nothing moves**         |
  | `nats-server`        |     5 | likely small          | **nothing moves**         |
  | `osapi-justfiles`    |     0 | none, nothing to move | nothing to move           |

  Three of the six rows are wrong, and the largest one is wrong by the largest
  margin: 140 pages predicted to be the biggest move produce no move at all.
  What actually moves in the whole programme is five pages, three from `gohai`
  and two from `osapi`, plus the part of `osapi`'s `sdk/guidelines.md` that is
  not a demonstration of rules the corpus already states.

- **FR-036**: The corpus MUST state what predicts a move, since a page count
  does not. What predicts it is **who the repository's documentation was written
  for**, and that is a property of the tree as a whole rather than of its size.
  Four of the five repositories wrote every page for the people importing the
  package, and produced no move between them. `osapi` publishes a site aimed at
  operators and put contributor architecture on it, which is why a tree a
  quarter the size of `osapi-orchestrator`'s produced the only substantial move
  in the programme.

  Stated because the wrong prediction was not a slip. It was a reasonable
  inference from the only figure available before anybody read the pages, and
  the lesson is that the figure does not carry the information.

- **FR-037**: The corpus MUST record the convention the classifications made
  visible, which no repository owns and nothing states. Four repositories carry
  the same `docs/README.md` shape: an index table pointing at one directory per
  package, opening with the same sentence about `examples/` and
  `CONTRIBUTING.md`, word for word.

  ```sh
  cd ~/git/osapi-io && for r in gohai osapi-orchestrator nats-client nats-server; do
    grep -c 'Runnable programs live in' $r/docs/README.md
  done   # 1 1 1 1
  ```

  `osapi`, the one with a published site, does not. So the organization has a
  documentation layout that four repositories follow by copying each other, and
  a fifth that diverges for a reason nothing records. This is a candidate for
  `.charter/fragments/`, since it is a rule a repository can be measured
  against, and it is left as a gap rather than written here: a fragment composed
  into six constitutions is not a thing to add as a footnote to another
  feature's correction. Owner: `system`, its own feature.

- **FR-038**: This feature's **own task list** MUST agree with FR-031. FR-031
  corrected the classification total from 442 to 440 and `tasks.md` still says
  442 in two places, in T021 and in its closing figures. Corrected with this
  amendment.

  The 442 came from `osapi`'s 221 plus the other four repositories' 221, a
  coincidence the task list called out as a coincidence. With `osapi` at 219 the
  coincidence is gone, which is the only reason the stale figure is visible at
  all. A number that was interesting for being equal stops being equal when it
  is corrected, and that is a better alarm than most.

- **FR-039**: The corpus MUST record that the seven sections ask what a
  repository **is** and never what it is **for**, which T017's reading found by
  being unable to answer it. Six baselines and roughly 3,400 lines describe the
  machine, and a reader finishes them able to say that osapi queues work to
  agents and unable to say why anybody wants that.

  The answer was never missing from the organization. `osapi`'s README and the
  first page of its site both say it, in the same sentence: the project
  "provides basic management capabilities to Linux systems, enabling them to be
  used as appliances". A classification that asks who reads a page has no
  question that would notice the corpus lacking a sentence the front door
  carries.

  Section 1 is the natural home and its name works against it. "What the
  repository is" invites an answer about shape, and every baseline gave one.
  Fixed in memory rather than in the baselines, at specs#213, because memory is
  what a reader is handed: `system`'s architecture document and `osapi`'s entry
  point now open with the purpose, and the repository table in `README.md`
  states it above the links.

  What is left is whether section 1 should require it, which would bind six
  constitutions through `.charter/fragments/global/baseline.md`. Owner: this
  feature, in its own change, for the reason FR-037 gives about fragments.

- **FR-040**: The corpus MUST record what a citation points at now that memory
  is prose, because this feature changed the answer and did not say so.

  `osapi`'s 005 FR-025 requires citations "named to a requirement rather than to
  a document", and 003's citation contract gives the reason: "See the job system
  specification" is a pointer, "FR-007" is a citation, and only the second tells
  a reader whether what they want is there. That was right when memory held
  numbered requirements. This feature made memory prose with no requirement
  identifiers in it, which leaves a citation with two possible targets and no
  rule choosing between them.

  The count, measured 2026-09-30:

  | Citing                                  | Links | Target                    |
  | --------------------------------------- | ----: | ------------------------- |
  | `osapi`'s published documentation pages |    31 | four of its feature specs |

  ```sh
  grep -rho 'specs/blob/main/components/osapi/specs/[0-9]*-[a-z-]*' \
    --include='*.md' --include='*.mdx' osapi | sort | uniq -c
  ```

  `development/adding-an-api-domain.md` holds 16 of them as a table of `FR-001`
  through `FR-024`, which is what 005's FR-026 deliberately reduced it to. It is
  the shape that feature wanted and it now sends a contributor to a merged
  feature specification when a current description of the same subject exists in
  `architecture/domains.md`.

  Both targets are defensible and they answer different questions. A feature
  spec says what was decided and when, keeps its numbers forever, and is the
  right target for provenance, which is why the skills cite it. Memory says what
  is true today and is the right target for somebody about to write code. What
  is missing is the sentence saying which one a published page cites.

  Not decided here. Deciding it changes 31 links in `osapi` and the contract two
  of its features depend on, so it is its own feature with its own review.
  Owner: this project. Until then the links are correct against 005 and stale
  against the shape this feature established, and that is worth knowing rather
  than quietly fixing.

### What this feature does not do

- **FR-016**: This specification MUST NOT write any of the five remaining
  baselines. It states the shape; each baseline is its own feature in its own
  project, which is what keeps a wrong shape from being discovered six times.

### Key Entities

- **Baseline**: A component project's first feature, whose deliverable is an
  inventory of how that repository behaves today. Seven sections, in order.
- **Section**: One of the seven required parts. Required by default, omissible
  only where the repository's nature makes it meaningless, and never omitted
  silently.
- **Measurement**: A count paired with the command that reproduces it. The
  pairing is what makes a baseline checkable rather than believable.
- **Gap**: A disagreement between a repository's prose and its code, recorded
  with both sides named and an owner. Never corrected by the baseline itself.
- **Edge**: A dependency between two repositories, named from both ends so a
  reader can trace it from either.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has read none of the baselines reads all of them and
  can state, without opening a repository: what each of the six is for, and
  every dependency edge between them. This is the outcome; "six baselines exist"
  is not.
- **SC-002**: Every count in every baseline is paired with a command, and
  running the commands reproduces the counts or shows precisely which have
  drifted.
- **SC-003**: No baseline contains a transcribed call graph, an exhaustive list
  of exported functions, or a file-by-file walkthrough.
- **SC-004**: Every baseline's section 7 is non-empty — every one has something
  it deliberately leaves out, and says so.
- **SC-005**: The charter fragment exists and is composed into all six component
  constitutions, so the shape binds rather than being advice.
- **SC-006**: gohai's baseline carries sections 2 and 3, added by its own
  amendment rather than by this feature.
- **SC-007**: Every documentation page in every repository is classified as
  user-facing or contributor-facing by that repository's baseline, and no page
  is moved without its classification stating why. **440** pages across the five
  repositories that have any — `osapi`'s 219 published pages, not the 221 that
  includes the Docusaurus project's own files. **Corrected**: this read 221,
  which is `osapi`'s own page count and coincidentally also the total for the
  four repositories still needing a move — two different quantities sharing one
  figure, which is why the error read as consistent.
- **SC-008**: After the moves, no contributor rule is stated in both a
  repository and the corpus. This is the one-statement rule applied across
  repositories rather than within one, and it is what the whole exercise is for.
- **SC-009**: `just test` passes in the specs repository.

## Assumptions

- The six repositories are those the repository list returns today: `gohai`,
  `nats-client`, `nats-server`, `osapi`, `osapi-justfiles`,
  `osapi-orchestrator`. The list itself comes from the command `system`'s own
  first feature made authoritative, not from this file.
- The dependency graph as measured on 2026-09-29: `osapi` depends on
  `nats-client` and `nats-server`; `osapi-orchestrator` depends on `osapi`;
  `gohai` has no osapi-io Go dependencies and no osapi-io dependents;
  `osapi-justfiles` is fetched by all six through a justfile recipe. It will
  change, which is why FR-002 requires each baseline to state its own edges
  rather than this file holding the graph.
- Every repository already defers to this one for design: their own `AGENTS.md`
  and `CONTRIBUTING.md` point here rather than restating a workflow. So the
  evergreen documents live **only** in this repository, in each project's
  `.specify/memory/`, and are never copied into the repository they describe. A
  copy there would be the second statement `global/documentation` forbids, and
  it would be the copy that goes stale, because nothing regenerates it.
- **`osapi` gets a baseline like every other repository.** Its memory holds five
  archived features, which is accumulated *feature* history rather than an
  inventory: it says what each change did and nowhere says what the repository
  is, where it sits, or what its architecture is. Under this shape it is the one
  memory that does not conform — see FR-021.
- The work is **two operations, not one**: a baseline states what a repository
  is, and a move relocates its contributor documentation into the corpus. gohai
  has the first and needs the second; osapi has the second and needs the first.
  That asymmetry is the thing being corrected, and it is why FR-026 fixes the
  order rather than leaving it to whoever goes next.
- The seven sections are the minimum that answers SC-001. A baseline may say
  more; it may not say less without stating the omission.
- One finding is recorded here and deliberately not acted on: `osapi-justfiles`
  is fetched from `refs/heads/main` rather than a pinned ref, which the Tooling
  principle's "a tool whose output is committed is pinned" speaks to directly.
  It is osapi-justfiles' and each consumer's own change, not this feature's.
