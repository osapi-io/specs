# Feature Specification: A baseline for gohai

**Feature Branch**: `001-gohai-baseline`

**Created**: 2026-09-29

**Status**: Completed — amended 2026-09-30: FR-017 through FR-020 add the page
classification this baseline owed, which `system`'s 002 requires of every
baseline and which this one predates.

**Input**: gohai's `.specify/memory/` is empty. Its constitution is composed
from `.charter/` and so states what binds every repository and nothing about how
this one behaves, which means the memory a skill reads first says nothing about
the repository it describes. This is the first of the five unbaselined projects,
and CONTRIBUTING's "Seeding a component" names it as the one to try first
because gohai depends on nothing else in the organization.

## What this specification is, and what it is not

**Its subject is a description, not a change.** Nothing lands in the gohai
repository — no Go code changes, no collector is added or altered. What this
produces is an inventory of how gohai behaves today, which lives in this feature
directory and reaches memory through archival like any other feature.

That distinction is what makes a baselining feature honest. A specification
written as though this work had been planned in advance would be the failure the
constitution's Correction principle names: a record that claims to have decided
something it merely found. This one claims to have *looked*, and every
requirement below says where it looked.

**Prose was a lead, never a source.** gohai carries a 324-line README, a
596-line CONTRIBUTING, and a `docs/` tree with a 65-row collector catalogue,
`methodology.md`, `adding-a-collector.md` and `ocsf-validation.md`. None of it
was transcribed. Every count below came from a command, and the commands are
given so a reader re-measures rather than trusting this file. Two disagreements
between that prose and the code turned up while doing so, and both are recorded
below as Gaps rather than quietly corrected.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A consumer knows what gohai guarantees (Priority: P1)

Somebody importing `pkg/gohai` needs to know what they may depend on: the shape
a collector has, what selects one, what runs before what, and what comes out.
They read the corpus and know before they write code against it.

**Why this priority**: gohai is SDK-first — its README says so in its first
sentence — so its consumers are programs, and a program that depends on an
undocumented shape breaks silently when the shape changes.

**Independent Test**: given the corpus alone, a reader can state the collector
contract, what decides whether a collector runs, and how one collector reads
another's output.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a consumer asks what a collector is, **Then**
   the five-method interface is stated with the file that declares it.
2. **Given** the corpus, **When** a consumer asks why a collector they expected
   did not run, **Then** the default-enabled rule is stated, along with the
   kinds of collector that opt out of it and why.
3. **Given** the corpus, **When** a consumer asks how a collector uses another's
   facts, **Then** the dependency declaration, the prior-results map and the
   typed accessor are all stated.

______________________________________________________________________

### User Story 2 - A contributor adding a collector knows the obligations (Priority: P2)

Somebody adding the sixty-third collector needs to know what the registry
requires of it, which category it belongs to, and what else has to change.

**Why this priority**: it is the most common change gohai takes, and the
contract is uniform across all 62 existing collectors, so stating it once serves
every future one.

**Independent Test**: the obligations are stated as a contract rather than as 62
examples, and a reader can name what a new collector must implement without
opening a collector.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a contributor asks which categories exist,
   **Then** all ten are named, and the corpus states that the set is closed by
   the constants rather than open to a new string.

______________________________________________________________________

### User Story 3 - A number in the corpus is the number in the code (Priority: P2)

Somebody reading a count in gohai's memory — how many collectors, how many
categories — finds what the repository has, or an explicit statement that the
code and the prose disagree.

**Why this priority**: gohai's own README already disagrees with its code on
both counts. Copying either number into memory would give a wrong figure the
authority of a specification.

**Independent Test**: for each count stated, the given command reproduces it.

**Acceptance Scenarios**:

1. **Given** a count in the corpus, **When** its command is run, **Then** it
   produces that number.
2. **Given** a count gohai's prose states differently, **When** the corpus is
   read, **Then** both figures appear with the reason they differ.

### Edge Cases

- **A collector is added or removed.** Every count here dates immediately, which
  is why each is paired with the command that recomputes it rather than being
  stated alone.
- **A collector returns nil.** The interface's own comment says `Collect`
  returns a typed struct "or nil if not supported", so absence is a normal
  outcome on a platform rather than a failure.
- **A catalogued collector does not exist.** Three entries are catalogued and
  deliberately unimplemented. A reader counting rows gets a different number
  from a reader counting packages, and both are right about different things.
- **A category constant with no collector.** None exists today — all ten are in
  use — but the inventory states the constants as the closed set, so a future
  unused one would not silently become invisible.

## Requirements *(mandatory)*

Each requirement takes the form *the corpus MUST state X*. The verification
column is not decoration: it is what distinguishes this inventory from a copy of
gohai's README.

### What gohai is

- **FR-001**: The corpus MUST state that gohai is an SDK-first Go library for
  collecting system facts, importable at `pkg/gohai`, which also ships a CLI —
  and that SDK-first is the repository's own framing rather than an
  interpretation. Verified: `README.md` line 13 states "gohai is an SDK-first Go
  library"; the CLI entry point is `main.go` with commands under `cmd/`.
- **FR-002**: The corpus MUST state the repository's size as a measurement with
  its command, not as a number alone: 314 Go files, of which 205 are not tests.
  Verified: `find . -name '*.go' -not -path './.git/*' | wc -l` and the same
  with `-not -name '*_test.go'`.

### The collector contract

- **FR-003**: The corpus MUST state the `Collector` interface as **exactly five
  methods** — `Name`, `Category`, `DefaultEnabled`, `Dependencies`, `Collect` —
  and MUST state that this is the whole contract a collector implements.
  Verified: `internal/collector/collector.go`, and
  `awk '/^type Collector interface/,/^}/' internal/collector/collector.go | grep -cE '^\t[A-Z]'`
  returns 5.
- **FR-004**: The corpus MUST state the collectors **by the contract they all
  obey, not one requirement each**. Sixty-two requirements naming sixty-two
  collectors would be a copy of the directory listing: it would rot on every
  addition, it would state nothing a reader could not get from `ls`, and it
  would bury the four rules that actually bind. The enumeration already exists
  and is maintained — `docs/collectors/README.md` — so the corpus cites it
  rather than duplicating it.
- **FR-005**: The corpus MUST state that `DefaultEnabled` is what keeps heavy or
  privileged collectors off until a caller asks, and MUST name the cases the
  interface itself names: ssh host keys, full package inventory, full service
  list. Verified: the doc comment on `DefaultEnabled` in
  `internal/collector/collector.go`.
- **FR-006**: The corpus MUST state the ten categories as a **closed set fixed
  by constants** — system, hardware, network, cloud, virtualization, security,
  software, users, linux, misc — and MUST state that every one of the ten is in
  use by at least one collector. Verified:
  `grep -cE '^\tCategory[A-Za-z]+ +=' internal/collector/collector.go` returns
  10, and
  `grep -rhoE 'collector\.Category[A-Za-z]+' pkg/gohai/collectors/ | sort -u | wc -l`
  also returns 10.
- **FR-007**: The corpus MUST state how one collector reads another's output:
  `Dependencies` declares what must run first, `PriorResults` carries the typed
  outputs of what finished, and the generic `GetDep[T]` retrieves one with its
  type. It MUST also state the interface's own caveat — prior "always includes
  everything declared in Dependencies; may include additional upstream siblings"
  — because a collector that relies on a sibling it did not declare works by
  accident. Verified: `internal/collector/collector.go`.
- **FR-008**: The corpus MUST state that `Collect` may return nil for a platform
  that does not support it, and that this is a normal outcome rather than an
  error. Verified: the `Collect` doc comment.

### The registry

- **FR-009**: The corpus MUST state the registry's exported surface —
  `NewRegistry`, `Register`, `Get`, `Names`, `NamesInCategory`, `Selected`,
  `SelectedWith`, `Run` — as the whole of what a caller drives. Verified:
  `grep -nE '^func ' internal/collector/registry.go`.
- **FR-010**: The corpus MUST state that the registry expands declared
  dependencies and runs collectors in topological levels rather than in
  registration order, so ordering is derived from `Dependencies` rather than
  from how a caller listed them. Verified: `expandWithDeps` and `topoLevels` in
  `internal/collector/registry.go`.
- **FR-011**: The corpus MUST state that all 62 collector packages are
  registered in one place, `pkg/gohai/gohai.go`, so a collector that exists but
  is unregistered is unreachable. Verified:
  `grep -oE 'collectors/[a-z_]+' pkg/gohai/gohai.go | sort -u | wc -l` returns
  62, matching the 62 package directories.

### Output

- **FR-012**: The corpus MUST state that gohai emits an OCSF representation
  through `FromFacts` in `pkg/gohai/ocsf`, and that this is a conversion of
  collected facts rather than a second collection path. Verified:
  `grep -nE '^func [A-Z]' pkg/gohai/ocsf/*.go`.
- **FR-013**: The corpus MUST state that a JSON Schema for the fact output
  exists at `schemas/gohai.schema.json` and is generated rather than
  hand-written, and MUST name the generator directory `schemas/gen`. Verified:
  those paths exist.

### Counts, and where the prose disagrees

- **FR-014**: The corpus MUST state **62 implemented collectors**, with the
  command that produces it, and MUST record that gohai's own prose says 65.
  **Gap, and it is a definition rather than an error**:
  `docs/collectors/README.md` tabulates **65 rows** and carries an `Implemented`
  column; three of those rows — `rackspace`, `softlayer`, `eucalyptus` — are
  marked `🪦` with Default `❌` and have no package under `pkg/gohai/collectors/`.
  So 65 is the catalogue including deliberately unimplemented entries and 62 is
  what exists. The corpus states both numbers and what each counts, because a
  reader who compares `ls` with the README and is told only one of them will
  think one is broken. Verified: `ls -d pkg/gohai/collectors/*/ | wc -l` returns
  62; the catalogue's row count is 65.

  **Corrected in gohai by gohai#201**, after this gap was recorded. Both figures
  now appear there with what each counts, so the disagreement described above no
  longer exists in that repository. The requirement stays as written: it states
  what the corpus must hold, and the record of having *found* the disagreement
  is what explains why gohai's prose changed.

- **FR-015**: The corpus MUST state **ten** categories and MUST record that
  gohai's prose says nine in two places. **Gap, and this one is an error rather
  than a definition**: `README.md` line 111 says "65 collectors across 9
  categories" and `docs/collectors/README.md` line 3 says "across 9 categories".
  Ten constants are declared and all ten are returned by at least one collector,
  so there is no reading on which nine is right.

  **Corrected in gohai by gohai#201**, in its own change — which is where a
  correction to that repository belongs, since nothing lands there from this
  feature. That change also found a **third** defect this requirement had not:
  the catalogue's legend defined `✅` twice, once as "implemented and tested" and
  once as "planned", which made the Implemented column unreadable given that 62
  of its 65 rows are ticks. It surfaced only because reconciling 65 against 62
  meant reading the legend — which is the argument for pairing a count with the
  command that produces it rather than stating the count alone.

### What this inventory does not cover

- **FR-016**: The corpus MUST state what it deliberately leaves out, so a later
  reader can tell an omission from a decision: how any individual collector
  gathers its facts, the CLI's flag surface beyond the node_exporter-style
  `--collector.<name>` form the catalogue documents, the OCSF field mapping in
  `schemas/field-mapping.md`, and gohai's testing conventions, which are its own
  `CONTRIBUTING.md`'s and are cited rather than copied.

### Key Entities

- **Collector**: A unit that gathers one area of system facts. Implements
  exactly five methods, belongs to one of ten categories, declares its
  dependencies, and may return nil where a platform does not support it.
- **Category**: One of ten fixed labels grouping related collectors, used to
  enable sets of them at once. Closed by constants.
- **Registry**: What holds collectors, resolves their declared dependencies into
  topological levels, and runs a selected set.
- **Prior results**: The typed outputs of collectors that have already run,
  reachable by name through a generic accessor.
- **Catalogued collector**: An entry in the collector catalogue, which may be
  implemented or deliberately not. 65 catalogued, 62 implemented.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has not seen gohai's README or `docs/` answers three
  questions from the corpus alone: *what does a collector have to implement?*;
  *why might a collector not run, and how do I make it run?*; *how does one
  collector use another's facts, and what may it assume about ordering?* Each
  would break a consumer if unanswered — a collector that does not satisfy the
  interface, a caller who cannot explain an absent fact, and a collector reading
  an undeclared sibling.
- **SC-002**: Every count in the corpus is paired with a command, and running
  the command reproduces the count. Four counts are stated: 314, 205, 62, 10.
- **SC-003**: Both disagreements between gohai's prose and its code appear in
  the corpus with both figures and the reason they differ, rather than as a
  single corrected number.
- **SC-004**: `just test` passes in the specs repository.
- **SC-005**: Nothing in the gohai repository changes. `git -C gohai status` is
  clean at the end of this feature.
- **SC-006**: gohai's `.specify/memory/spec.md` is non-empty once this feature
  is archived, and every entry in it carries a source reference to this feature.

### The classification this baseline owed

- **FR-017**: The corpus MUST classify every one of gohai's 68 documentation
  pages as user-facing or contributor-facing, **by who reads it** rather than by
  where it sits. This baseline was written before `system`'s
  [002](../../../../system/specs/002-baseline-shape/spec.md) fixed the shape and
  carried no classification, which 002's FR-025 requires and its T021 records as
  owed.

  | Pages                        |   # | Reader      | Disposition                 |
  | ---------------------------- | --: | ----------- | --------------------------- |
  | `docs/collectors/*.md`       |  64 | consumer    | **stays**, per 002's FR-028 |
  | `docs/README.md`             |   1 | consumer    | **stays**, it is the index  |
  | `docs/adding-a-collector.md` |   1 | contributor | **moves**                   |
  | `docs/methodology.md`        |   1 | contributor | **moves**                   |
  | `docs/ocsf-validation.md`    |   1 | contributor | **moves**                   |
  | **Total**                    |  68 |             | **65 stay, 3 move**         |

  The 64 collector pages stay for the reason 002's FR-028 gives: each documents
  what one collector returns, and its reader is somebody consuming the library
  rather than changing it. Separating a collector's interface from its
  description serves nobody.

- **FR-018**: The corpus MUST state what the three contributor pages hold and
  that **none has a corpus counterpart**, so this is 769 lines of contributor
  knowledge on a consumer's documentation tree with nowhere to cite.

  | Page                    | Lines | Holds                                                                                        |
  | ----------------------- | ----: | -------------------------------------------------------------------------------------------- |
  | `methodology.md`        |   382 | How gohai decides what a collector reads, which library it wraps, what its fields are called |
  | `adding-a-collector.md` |   280 | The step-by-step walkthrough for building one                                                |
  | `ocsf-validation.md`    |   107 | How to validate the OCSF output and vendor extension against the upstream schema             |

  `methodology.md` is the substantive one, and it is **architecture rather than
  a walkthrough**: what decides a collector's field names and which upstream
  library it wraps is the design of the collection layer. gohai's memory
  currently excludes "how any individual collector gathers its facts", which was
  the right exclusion for 62 instances and the wrong one for the rule they
  share.

- **FR-019**: The corpus MUST record which of the three pages anything cites,
  and it is not all of them.

  | Page                    | Cited by `CONTRIBUTING.md`      | Cited by `docs/README.md` |
  | ----------------------- | ------------------------------- | ------------------------- |
  | `adding-a-collector.md` | lines 436 and 489               | yes                       |
  | `methodology.md`        | line 8, as "reference material" | yes                       |
  | `ocsf-validation.md`    | **nowhere**                     | yes                       |

  ```sh
  grep -nE 'methodology\.md|adding-a-collector\.md|ocsf-validation\.md' CONTRIBUTING.md
  ```

  Two of the three are load-bearing for a contributor, so a move relocates their
  content and must leave those citations resolving. That is the obligation 003's
  FR-006 placed on osapi's move.

  `ocsf-validation.md` is reachable only from the index, which is a fourth
  disposition the classification did not have a column for: not stranded, since
  the index links it, but cited by nothing that tells a contributor when to read
  it. It is a runbook nobody is sent to.

- **FR-019a**: The corpus MUST record that `docs/README.md` **stays and is
  edited**. It is the index and it links all four of its siblings, so three rows
  leave it when the three pages move. A classification that calls the index
  "stays" and stops there hides an edit inside a move, which is the shape of
  defect osapi's 007 found four times.

- **FR-020**: The corpus MUST record that the move is **a separate feature**,
  per 002's FR-026 and FR-027: the baseline classifies and relocates nothing.
  That feature is not open. Owner: this project.

  It is also larger than osapi's was. osapi's move reconciled 464 lines across
  two UI pages; this one is 769 across three, and one of them is architecture
  the baseline explicitly excluded.

## Assumptions

- The audience is a consumer of `pkg/gohai` or a contributor to it, not an
  operator running the CLI. What the CLI prints for an operator is gohai's own
  documentation's job.
- The contract is what is worth stating; the collectors are what is worth
  counting and citing. That is the judgement FR-004 records, and it is the
  reason this inventory is short enough to read.
- gohai's own `CONTRIBUTING.md` and `docs/` continue to exist and stay where
  they are. This inventory cites them; it does not replace them, and this
  feature changes nothing in that repository.
- Counts were measured on `3132c9d`, the `main` commit at the time of writing.
  They will date; the commands are what survives.
- The Time Machine extension, which CONTRIBUTING selects for producing an
  inventory from existing code, was **not** used. Its installer requires an
  interactive confirmation that this session cannot give, and it warns that it
  bypasses the trusted extension catalogues. This inventory was written by
  reading the repository, which CONTRIBUTING calls the slow path and does not
  forbid. Whether to trial the extension remains open for the other four
  unbaselined projects.
