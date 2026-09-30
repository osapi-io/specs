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

  | Repository           | Doc pages | Baseline                       | Move                                |
  | -------------------- | --------- | ------------------------------ | ----------------------------------- |
  | `osapi`              | 221       | needed — it has none           | already done, across three features |
  | `osapi-orchestrator` | 140       | needed                         | needed, the largest remaining       |
  | `gohai`              | 68        | exists, needs sections 2 and 3 | needed                              |
  | `nats-client`        | 8         | needed                         | likely small                        |
  | `nats-server`        | 5         | needed                         | likely small                        |
  | `osapi-justfiles`    | 0         | needed                         | none — nothing to move              |

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
  is moved without its classification stating why. **442** pages across the five
  repositories that have any. **Corrected**: this read 221, which is `osapi`'s
  own page count and coincidentally also the total for the four repositories
  still needing a move — two different quantities sharing one figure, which is
  why the error read as consistent.
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
