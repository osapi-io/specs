# Feature Specification: A baseline for osapi-orchestrator

**Feature Branch**: `001-orchestrator-baseline`

**Created**: 2026-09-30

**Status**: Completed, archived at specs#196. Amended 2026-09-30: FR-021 through
FR-024 add the page classification every baseline owes, which this one was
written before 002 required.

**Input**: `osapi-orchestrator`'s `.specify/memory/` holds only a constitution.
Unit 9 of the baseline programme `system`'s
[002](../../../../system/specs/002-baseline-shape/spec.md) defines, the largest
remaining, and the last of the six components to be baselined.

## What this specification is, and what it is not

**Its subject is a description, not a change.** Nothing lands in the
`osapi-orchestrator` repository.

**Prose was a lead, never a source, and here the prose held up.** This
repository carries 140 documentation pages against 81 Go files, more
documentation than code, and the reconciliation in FR-017 checked it in both
directions: 101 operation pages map one to one onto 101 operation methods, with
no orphan page and no undocumented method. That is the first documentation set
in this programme to reconcile, and it is stated as a measured result rather
than assumed.

**It is read after osapi's.** This repository consumes osapi's SDK and nothing
consumes it, so its section 2 is written to be read after
[osapi's baseline](../../../osapi/specs/006-osapi-baseline/spec.md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Somebody learns what the orchestrator is for (Priority: P1)

Somebody arriving can state what it does that calling osapi's SDK directly would
not, and what its unit of work is.

**Why this priority**: every one of its 101 operations wraps an SDK call. If the
wrapping adds nothing the repository has no reason to exist.

**Independent Test**: a reader given the corpus alone states what a `Step` is,
names three ways a step can be made conditional, and says what `Run` does with
them.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a reader asks what the orchestrator adds over
   the SDK, **Then** ordering, conditional execution, retry and multi-host
   result handling are named.
2. **Given** the corpus, **When** a reader asks how a step is made conditional,
   **Then** the guards and the host predicates are both described, with the
   difference between them.

______________________________________________________________________

### User Story 2 - A consumer of the SDK knows how deeply it reaches (Priority: P1)

Somebody changing osapi's SDK knows that this repository's **internal** engine
imports it too, so the coupling is not confined to the public layer built to
hold it.

**Why this priority**: equal to the first. A reader would reasonably expect
`internal/engine` to work on an abstraction. It does not, and that changes what
a rename costs.

**Independent Test**: the specification names the files in `internal/engine`
that import `osapi/pkg/sdk/client`, and states that the public package declares
no interface that would have insulated it.

______________________________________________________________________

### User Story 3 - The documentation's accuracy is known rather than assumed (Priority: P2)

Somebody deciding whether to trust 140 pages knows their coverage was checked in
both directions.

**Why this priority**: lower, and it is the finding most likely to be assumed
rather than measured. Three baselines before this one found prose disagreeing
with code; this one found prose that does not.

### Edge Cases

- **A documentation set that reconciles.** 125 pages under `docs/operations/`
  decompose into 101 operation pages and 24 directory indexes, and each of the
  101 matches a method by its `H1`. The check is a loop over headings rather
  than a comparison of totals, because 101 and 101 agreeing proves nothing about
  whether they are the same 101.
- **An internal package that is not insulated.** `internal/engine` holds the
  plan, the task and the runner, and four of its files import
  `osapi/pkg/sdk/client`. The name `internal` describes visibility, not
  independence.
- **A public package with no interfaces at all.** `pkg/orchestrator` declares
  zero. `nats-client` and `nats-server` each declare exactly one and use it as
  the seam for substituting what they wrap. This substitutes nothing.
- **Uniformity that is load-bearing.** All 101 operation methods return `*Step`.
  That is what makes the guards composable across every operation rather than
  per domain, and one operation returning something else would break the
  property silently.

## Requirements *(mandatory)*

The seven section names are `system`'s 002 FR-001 names verbatim.

### 1. What this repository is

- **FR-001**: The corpus MUST state that `osapi-orchestrator` is a Go library
  providing a declarative layer over osapi's SDK, exposing one package,
  `pkg/orchestrator`. It ships no binary and has no entry point; a consumer
  imports it, describes work, and calls `Run`.
- **FR-002**: The corpus MUST state the four things it adds over calling the SDK
  directly, because a layer that adds nothing has no reason to exist:
  **ordering** between units of work, **conditional execution** based on what
  earlier work did or on what a host is, **retry**, and **multi-host result
  handling** where one unit of work targets several machines and each can
  succeed, fail, change or be skipped independently.

### 2. Where it sits

- **FR-003**: The corpus MUST state that it depends on osapi and that nothing in
  the organization depends on it. It is the terminal node downstream, the only
  component with an incoming Go edge and no outgoing one. Verified from both
  ends.
- **FR-004**: The corpus MUST state that it pins osapi by pseudo-version commit
  rather than tag, so an SDK change does not reach here until somebody bumps it.
- **FR-005**: The corpus MUST state that it also depends on `osapi-justfiles`
  through an unpinned justfile fetch that appears in no `go.mod`.

### 3. Architecture

- **FR-006**: The corpus MUST state the two layers and what each is for.
  `pkg/orchestrator` is the vocabulary a consumer writes in. `internal/engine`
  executes a plan built from it. The boundary is a plan.
- **FR-007**: The corpus MUST state that the unit of work is a `Step`, that all
  101 operation methods return `*Step` and nothing else, and why that uniformity
  is load-bearing.
- **FR-008**: The corpus MUST state the two kinds of conditional and the
  difference between them. **Guards** ask what earlier work did:
  `OnlyIfChanged`, `OnlyIfFailed`, `OnlyIfAllChanged`, `OnlyIfAnyHostFailed`,
  `OnlyIfAnyHostSkipped`, `OnlyIfAllHostsFailed`, `OnlyIfAnyHostChanged`,
  `OnlyIfAllHostsChanged`. **Host predicates** ask what a host is: `OS`, `Arch`,
  `MinMemory`, `MinCPU`, `HasLabel`, `FactEquals`, `HasCondition`,
  `NoCondition`, `Healthy`, and `MatchAll` to combine them, reaching a step
  through `When` and `WhenFact`.
- **FR-009**: The corpus MUST state the rest of the `Step` vocabulary: `Named`,
  `After` for ordering, `Retry`, and `OnError` with `ContinueOnError`. Fifteen
  methods on `Step`.
- **FR-010**: The corpus MUST state that four files in `internal/engine` import
  osapi's SDK directly, so the engine works on osapi's generated types rather
  than on an abstraction.
- **FR-011**: The corpus MUST state that the repository ships 41 runnable
  examples, 23 for operations and 18 for features.

### 4. The contract

- **FR-012**: The corpus MUST state that the contract is the exported surface of
  `pkg/orchestrator`: 16 functions, 13 types and 127 methods, of which 101 are
  the operations. Everything under `internal/` is not the contract, including
  the parts that import osapi's SDK.
- **FR-013**: The corpus MUST state that `pkg/orchestrator` declares **no
  interfaces at all**, so a consumer cannot replace the SDK underneath it and
  the repository's own tests reach osapi's generated client directly.

### 5. Measurements

- **FR-016**: The corpus MUST state each count with the command that reproduces
  it, and each command MUST stand alone rather than referring to the row above
  it. Measured 2026-09-30 at `727ab40`.
- **FR-017**: The corpus MUST state that the documentation reconciles exactly
  against the code, **checked in both directions**, and MUST give the check
  rather than the conclusion. Every one of the 101 operation pages has an `H1`
  naming a method in `ops.go`, and every one of the 101 methods has a page whose
  `H1` is its name. Zero orphans either way.

### 6. Gaps

- **FR-014**: The corpus MUST record that `internal/engine` imports osapi's SDK,
  in `bridge.go`, `plan.go`, `task.go` and their tests. Not a defect on its
  face, since there may be no reason to abstract a dependency this repository
  exists to consume, but it is stated nowhere and a consumer cannot infer it.
  Owner: `osapi-orchestrator`.
- **FR-015**: The corpus MUST record that `pkg/orchestrator` declares no
  interface, which leaves FR-014 unmitigated: there is no seam at which osapi's
  client could be substituted. Owner: `osapi-orchestrator`.
- **FR-018**: The corpus MUST record that **nothing verifies the one-to-one
  documentation mapping**. It holds today and was checked by hand; no gate
  enforces it, so the 102nd operation can be added without a page and nothing
  will say so. The repository with the best documentation coverage in the
  organization has no mechanism protecting it. Owner: `osapi-orchestrator`.

### 7. What this inventory excludes

- **FR-019**: The corpus MUST state what it leaves out: what each of the 101
  operations does, which has its own page; what osapi's SDK does, which is
  osapi's; the 14 feature pages' content; the `dist/` build output; the
  repository's own contributor conventions; and whether the guard vocabulary is
  the right vocabulary.
- **FR-020**: The corpus MUST state that no section of the seven was omitted and
  that the section names are 002's verbatim, inherited through `nats-server`'s
  baseline from `nats-client`'s from `osapi-justfiles`', which is three hops
  without drift.

### The classification this baseline owed

- **FR-021**: The corpus MUST classify every one of the 140 documentation pages
  as user-facing or contributor-facing, **by who reads it** rather than by where
  it sits, which `system`'s 002 requires of every baseline and its T021 records
  as owed here. Every page is user-facing, so **nothing moves**.

  | Pages                |   # | Reader   | Why                                                     |
  | -------------------- | --: | -------- | ------------------------------------------------------- |
  | `docs/operations/**` | 125 | consumer | One page per operation: signature, options, idempotence |
  | `docs/features/*.md` |  14 | consumer | How to write a plan with the DSL                        |
  | `docs/README.md`     |   1 | consumer | The index                                               |
  | **Total**            | 140 |          | **140 stay, 0 move**                                    |

  Every page addresses somebody importing the library and writing a plan. An
  operation page gives the constructor, its options table and whether the
  operation is idempotent; a feature page shows the calls that compose a DAG.
  Nothing tells a reader how to change the orchestrator. The sweep for the
  markers that would say otherwise returns two files, and both are false
  positives: `docs/README.md` points at `CONTRIBUTING.md`, and
  `operations/security/user/add-key.md` says "Adding a key that already exists
  returns an error", which is prose about the operation.

  ```sh
  grep -rlniE 'adding a|add a new|regenerate|codegen|go generate|contribut|internal/' \
    docs --include='*.md'
  ```

- **FR-022**: The corpus MUST record that this **contradicts 002's own
  prediction**. 002's FR-027 table calls this repository's move "needed, the
  largest remaining" on the strength of its 140 pages, and the classification
  says there is no move at all. Page count does not predict move size: what
  predicts it is whether a repository's documentation was written for the people
  using it, and this one's was, uniformly. osapi had a quarter of the volume in
  contributor pages and a tenth the page count.

  Owner: `system`'s 002. The prediction is wrong in a merged table and needs
  correcting there rather than reinterpreted here.

- **FR-023**: The corpus MUST record what the classification found while reading
  every page, which is a disagreement about what the word "guard" means.

  | Source                     | Guards | Where `When` and `WhenFact` sit    |
  | -------------------------- | -----: | ---------------------------------- |
  | `pkg/orchestrator/step.go` |      8 | "When adds a guard condition"      |
  | `docs/features/guards.md`  |     10 | Task-level guards, in its table    |
  | This project's memory      |      8 | Host predicates, reached by `When` |

  The code and the page agree, and memory is the outlier. Memory's distinction
  is worth keeping, because a condition on what earlier steps did and a
  condition on what a machine is are genuinely different things and conflating
  them is the mistake it warns about. What memory got wrong is implying the code
  draws the line in the same place. It does not: `step.go:269` calls `When` a
  guard, and `guards.md` follows it.

  ```sh
  grep -cE '^func \(s \*Step\) OnlyIf' pkg/orchestrator/step.go   # 8
  grep -cE '^func \(s \*Step\) When' pkg/orchestrator/step.go     # 2
  sed -n '269p' pkg/orchestrator/step.go
  ```

  Owner: this project, and its memory is corrected with this amendment rather
  than after it. Memory is documentation, so a document known to be wrong is
  fixed; scheduling the fix would leave the only current description of the
  vocabulary disagreeing with the code it describes.

- **FR-024**: The corpus MUST state what the classification does **not** cover:
  `CONTRIBUTING.md`, `AGENTS.md` and the other convention files at the
  repository root. `osapi-justfiles`' baseline settled this shape, deciding that
  a file documenting the thing beside it stays beside it, and a convention file
  documents the repository it sits in. 002's FR-025 asks about a `docs/` tree's
  pages, and these are not pages in one.

### Key Entities

- **Step**: The unit of work. Every operation returns one, and guards attach to
  it.
- **Guard**: A condition on a `Step` asking what earlier work did. Eight of
  those; ten methods the repository itself calls guards, per FR-023.
- **Host predicate**: A condition asking what a host is. Ten, combinable.
- **Plan**: What the public package builds and the engine runs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given the corpus alone states what a `Step` is, names
  three ways a step can be made conditional, and says what `Run` does.
- **SC-002**: Every count is paired with a standalone command, and running them
  reproduces the values.
- **SC-003**: The one-to-one documentation mapping is verified in both
  directions, by iterating headings rather than comparing totals.
- **SC-004**: The three gaps are stated with what was measured, where, and an
  owner, and none is corrected here.
- **SC-005**: All seven sections present, in 002's order, under 002's names.
- **SC-006**: `just test` passes in the specs repository, `memory-check`
  included.
- **SC-007**: Nothing in the `osapi-orchestrator` repository changes.

## Assumptions

- Measurements are of `727ab40`. Counts date; the commands survive.
- The 140 documentation pages stay where they are. FR-017 records that their
  coverage is exact.
- The three gaps are recorded, not fixed. Each implies a change in
  `osapi-orchestrator`: an abstraction at the engine boundary or a stated
  decision not to have one, and a gate that fails when an operation has no page.
- This is the sixth and last component baselined. Whether the six read as one
  set is `system`'s 002 SC-001, which this unit makes answerable rather than
  answers.
