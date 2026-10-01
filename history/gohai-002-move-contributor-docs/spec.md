# Feature Specification: Move gohai's contributor documentation into the corpus

**Feature Branch**: `docs/gohai-the-move`

**Created**: 2026-09-30

**Status**: Implemented 2026-09-30. The design rules are in
`components/gohai/.specify/memory/architecture/collectors.md`. The three
one-line rules stay in `docs/methodology.md` where a contributor with one
checkout meets them, which is what `system`'s 003 arrived at and what unblocked
the plan. FR-009 is answered: the field naming counts are 107, 91 and 752,
measured from the Tier column of `schemas/field-mapping.md`, and the page's
roughly 108, 74 and 768 summed correctly while every figure was wrong.

**Input**: Move the three pages gohai's baseline classified contributor-facing.
This is the move `system`'s 002 FR-027 requires as its own feature, authorized
by the classification merged at specs#205.

## What this specification is, and what it is not

It decides **what of 769 lines is architecture and what is procedure**, and
moves only the first. The classification at specs#205 named three pages and did
not open them; opening them shows they hold three different kinds of content,
and treating "contributor-facing" as a synonym for "belongs in the corpus" would
move a nine-step walkthrough into a document nobody walks through.

The precedent is osapi's. Its 005 reduced `development/adding-an-api-domain.md`
to a citation index rather than deleting it, because a procedure belongs beside
the code while the rules it obeys belong in the corpus stated once. This feature
applies that split to gohai.

Nothing here changes a collector, the OCSF output, or the 64 collector pages.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor learns which library to wrap (Priority: P1)

Somebody adding a collector needs to know that gohai wraps upstream libraries
rather than reimplementing them, in what order to try them, and what to do when
none covers a field. Today that is on a documentation page with no corpus
counterpart, so the corpus a skill reads first says nothing about it.

**Why this priority**: it is the rule all 62 collectors follow, and the reason
gohai's baseline excluded "how any individual collector gathers its facts" was
that 62 instances are not architecture. The rule they share is.

**Independent Test**: a reader given only gohai's memory names the decision
order for choosing a backing library and says what an extension may do.

**Acceptance Scenarios**:

1. **Given** gohai's memory, **When** a contributor asks which library to use
   for static hardware shape, **Then** the answer is ghw, with the reason.
2. **Given** gohai's memory, **When** they ask what an extension may read from,
   **Then** the answer names `avfs.VFS` and `executor.Executor` and says why.

### User Story 2 - A contributor follows the walkthrough and is warned (Priority: P2)

Somebody writing a collector works through nine steps. Step 4 is registering it
in `pkg/gohai/gohai.go`, and gohai's memory records that the error from that
registration is discarded and the test its comment defers to does not exist. The
walkthrough sends a contributor to the one step whose failure is silent and says
nothing about it.

**Why this priority**: the walkthrough stays where it is, so this is a change to
what it links to rather than to where it lives.

**Independent Test**: the reduced walkthrough's step 4 links to the limitation
and does not restate it.

### User Story 3 - A runbook nobody is sent to gets a reader (Priority: P3)

`docs/ocsf-validation.md` is a four-step procedure for validating gohai's OCSF
output against the upstream schema. Nothing cites it except the documentation
index, so a contributor changing a field has no path to it.

**Why this priority**: the smallest of the three and the only one whose problem
is its absence from a citation rather than its location.

### Edge Cases

- A reader arrives at `docs/methodology.md` from an old bookmark. The address
  has to resolve and the page has to read as a whole rather than as what is
  left.
- A reader arrives at `CONTRIBUTING.md` line 8, which calls `methodology.md`
  "reference material". After the move most of that reference material is
  elsewhere, so the sentence has to change or it misdescribes its own link.
- The three-tier field-naming ladder carries three counts, roughly 108, 74 and
  768 fields. They are stated with a tilde and no command. Moving them into the
  corpus makes them subject to `just memory-check`, which fails a count without
  one.

## Requirements *(mandatory)*

### Section 1 — the three-way split

- **FR-001**: The corpus MUST state that the three pages hold three kinds of
  content, and that only the first moves:

  | Kind                    | Example                                           | Disposition |
  | ----------------------- | ------------------------------------------------- | ----------- |
  | Design rule             | "wrap upstream, do not reimplement"               | **moves**   |
  | Procedure               | the nine steps, the four validation steps         | **stays**   |
  | Per-collector reference | the library-stack table, the Data Sources cascade | **stays**   |

  The third disposition is FR-028's argument from `system`'s 002 applied again:
  a table of which library each of 62 collectors wraps has the same reader as
  the collector catalogue, which is somebody using the library, and separating
  it from the catalogue beside it serves nobody.

- **FR-002**: The corpus MUST state the measured split, so the move can be
  checked rather than asserted. Measured at gohai `f5eefe2`:

  | Page                         |   Lines |    Moves |    Stays |
  | ---------------------------- | ------: | -------: | -------: |
  | `docs/methodology.md`        |     382 |     ~215 |     ~167 |
  | `docs/adding-a-collector.md` |     280 |        0 |      280 |
  | `docs/ocsf-validation.md`    |     107 |        0 |      107 |
  | **Total**                    | **769** | **~215** | **~554** |

  ```sh
  wc -l docs/methodology.md docs/adding-a-collector.md docs/ocsf-validation.md
  ```

  So the honest figure for this move is roughly **215 lines, not 769**, and the
  classification that produced 769 was right about who reads the pages and
  silent about what the pages contain. That gap between "who reads it" and "what
  it is" is this feature's finding, and it belongs in `system`'s 002 as a limit
  on what a classification can decide.

### Section 2 — where the architecture lands

- **FR-003**: The moved content MUST land in a **new subject document**,
  `components/gohai/.specify/memory/architecture/collectors.md`, rather than
  being appended to `spec.md`. gohai's memory is one document of about 220
  lines; adding 215 lines of a single subject to it makes the entry point half
  about one subject. `global/baseline` says a subject with enough in it to
  explain gets its own document, and this is the first gohai subject that does.

- **FR-004**: `spec.md` MUST gain a link and lose its exclusion. Its "Not
  covered here" says "How any individual collector gathers its facts", which
  stays true of the 62 instances and stops being true of the rule they share.
  The exclusion is reworded rather than deleted, because the instances are still
  excluded.

- **FR-005**: The new document MUST state the decision order for choosing a
  backing library, as the ordered list it is, with what each library is
  canonical for. Seven positions, ending in gohai's own extension as a last
  resort.

- **FR-006**: The new document MUST state the rule that makes extensions
  testable: an extension reads files through `avfs.VFS` and runs commands
  through `executor.Executor`, never `os.ReadFile` or `exec.Command` in a
  `Collect` method, so a test never touches the real host. This is the rule a
  reviewer checks and the one a new collector is most likely to break.

- **FR-007**: The new document MUST state the no-build-tags pattern and its
  consequence: collector code compiles on every target platform with no
  `//go:build` tag anywhere, so `go test ./...` on any machine compiles and runs
  every collector's tests. It MUST record that this is osapi's pattern from
  `internal/provider/`, cited rather than re-explained, because
  [osapi's providers](../../../osapi/.specify/memory/architecture/providers.md)
  state it and two statements of one rule is what the corpus forbids.

- **FR-008**: The new document MUST state the three-tier field-naming ladder,
  OCSF first, OpenTelemetry semantic conventions second, gohai convention third,
  with what the third tier's conventions are.

- **FR-009**: The ladder's counts MUST be measured or dropped. The page states
  roughly 108, 74 and 768 fields per tier, with a tilde and no command. Either a
  command reproduces each or the corpus states the shape without the numbers. A
  hedged count in memory fails `just memory-check`, and a count nobody can
  reproduce is what the Verification principle forbids.

- **FR-010**: The Ohai cross-reference obligation MUST be classified and the
  spec MUST say which it is. It reads as a contributor obligation, "read Ohai's
  plugin before writing code", and its content is a design rule: gohai matches
  Ohai's *collection approach* and not its output shape, because Ohai carries
  years of distro-specific bug fixes and its JSON shape is a Ruby artifact. The
  rule moves; the instruction to run `gh api` to fetch the files stays with the
  walkthrough.

### Section 3 — what the pages become

- **FR-011**: `docs/methodology.md` MUST be reduced to what remains its own: the
  per-collector library stack table, the Data Sources cascade, and the
  `methodology-gap` issue convention, under an opening that says where the rules
  went. Target: under 200 lines, reading as a reference table with context
  rather than as a page with holes in it.

- **FR-012**: `docs/adding-a-collector.md` MUST keep all nine steps and gain
  citations. It is a procedure, it belongs beside the code, and every rule it
  applies is stated once in the corpus after this feature. Target: no reduction
  beyond replacing restated rules with links.

- **FR-013**: `docs/adding-a-collector.md` step 4 MUST cite the registration
  limitation rather than restate it. The step says register the collector in
  `pkg/gohai/gohai.go`; the corpus says the error from that call is discarded
  and the test its comment defers to does not exist. A contributor at step 4 is
  the only reader who needs that, and they currently have no way to learn it.

- **FR-014**: `docs/ocsf-validation.md` MUST stay whole and gain a citation from
  `CONTRIBUTING.md`. Reducing it would be wrong: there is nothing in it to move,
  and its problem is that nothing sends anybody to it. Owner of the citation:
  this feature.

- **FR-015**: `docs/README.md` MUST be edited rather than left alone. It links
  all four of its siblings and its descriptions of the three describe what they
  held before, so its rows change even though no page it links disappears.

### Section 4 — the citations

- **FR-016**: Every address MUST still resolve. Three pages keep their paths, so
  what changes is what `CONTRIBUTING.md`'s three citation sites point at:

  | Site     | Today                                       | After                                               |
  | -------- | ------------------------------------------- | --------------------------------------------------- |
  | line 8   | `docs/methodology.md`, "reference material" | the corpus, for the rules; the page, for the tables |
  | line 436 | `docs/adding-a-collector.md`                | unchanged                                           |
  | line 489 | `docs/adding-a-collector.md`                | unchanged                                           |

- **FR-017**: The corpus MUST state which of the two possible citation targets
  this feature picked and why, without deciding it for the organization.
  `system`'s 002 FR-040 records that a citation can point at a feature
  specification, which keeps its requirement numbers forever, or at memory,
  which describes what is true today, and that nothing chooses. This feature
  points its own new links at **memory**, because the reader arriving from
  `CONTRIBUTING.md` is about to write code and wants the current description.
  FR-040 stays open.

### Section 5 — measurements

- **FR-018**: The corpus MUST carry the counts this feature depends on, each
  with its command, measured at gohai `f5eefe2`:

  | Measurement                      | Value | Command                                                                        |
  | -------------------------------- | ----: | ------------------------------------------------------------------------------ |
  | Contributor pages                |     3 | the classification at specs#205                                                |
  | Their total lines                |   769 | `wc -l docs/methodology.md docs/adding-a-collector.md docs/ocsf-validation.md` |
  | `CONTRIBUTING.md` citation sites |     3 | `grep -cE 'methodology\.md\|adding-a-collector\.md' CONTRIBUTING.md`           |
  | Collector pages, unaffected      |    64 | `ls docs/collectors/*.md \| wc -l`                                             |

### Section 6 — gaps

- **FR-019**: **Gap**: a classification by reader cannot predict what moves.
  gohai's classification was correct and produced 769 lines; the move is roughly
  215\. `system`'s 002 FR-036 already records that page count does not predict
  move size; this adds that neither does the classification, because "who reads
  this" and "what kind of content is this" are different questions and only the
  second decides where content lives. Owner: `system`'s 002.

- **FR-020**: **Gap**: the field-naming ladder's three counts cannot be
  reproduced from anything stated. Owner: this feature, under FR-009, and if no
  command can produce them the corpus states the ladder without them rather than
  carrying a number nobody can check.

### Section 7 — what this feature excludes

- **FR-021**: The corpus MUST state what it leaves out: what any individual
  collector reads, which stays in the per-collector Data Sources and the
  catalogue; the nine steps themselves, which stay beside the code; the four
  OCSF validation steps, likewise; deciding 002's FR-040 for the organization;
  and adding a link checker, which would be the mechanism that keeps FR-016 true
  and is its own change in its own repository.

### Key Entities

- **Design rule**: a statement about how every collector behaves. Moves.
- **Procedure**: an ordered list of things a contributor does. Stays.
- **Per-collector reference**: a fact about one collector among 62. Stays.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given only gohai's memory names the library decision
  order, says what an extension may read through, and states the field-naming
  ladder's three tiers in order. None of the three is answerable from memory
  today.
- **SC-002**: No rule is stated in both the corpus and a gohai page. Checked by
  reading the reduced pages against the new document, not by counting lines.
- **SC-003**: Every count in the new document reproduces, verified by
  `just memory-check` in the specs repository.
- **SC-004**: `docs/methodology.md` reads as a whole. The test is a reader
  asking what the page is for and answering from its opening rather than from
  what is missing.
- **SC-005**: All three page addresses resolve, and `CONTRIBUTING.md`'s three
  citation sites resolve to something that states what the citing sentence
  claims.
- **SC-006**: `just test` passes in the specs repository, including
  `just memory-docs`, which fails on an `FR-` label, a `MUST`, or an em dash in
  anything under `.specify/memory/`.

## Assumptions

- The line targets in FR-011 and FR-002 are estimates from the section headings
  rather than from a drafted reduction. The planning stage refines them; a
  target missed by a wide margin is a signal that the split was drawn in the
  wrong place.
- `docs/methodology.md`'s "Methodology work" section, which describes the
  `methodology-gap` issue label, is treated as a repository convention and
  stays. It describes how gohai tracks work, which `global/tracking` governs and
  the corpus does not restate.
- gohai's memory gains its first `architecture/` directory here. osapi is the
  only component with one today, and the shape is the same.
