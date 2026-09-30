# Feature Specification: A baseline for nats-client

**Feature Branch**: `001-nats-client-baseline`

**Created**: 2026-09-30

**Status**: Draft

**Input**: `nats-client`'s `.specify/memory/` holds only a constitution composed
from `.charter/`, so it states what binds every repository and nothing about
this one. Unit 7 of the baseline programme `system`'s
[002](../../../../system/specs/002-baseline-shape/spec.md) defines, and the
first of the two NATS repositories osapi imports.

## What this specification is, and what it is not

**Its subject is a description, not a change.** Nothing lands in the
`nats-client` repository: no Go code changes, no method is renamed, no page
moves. What this produces is an inventory of how the repository behaves today,
which lives in this feature directory and reaches memory through archival.

**Prose was a lead, never a source.** The repository carries a 62-line README
and eight documentation pages. None was transcribed. Every count came from a
command, the commands are given so a reader re-measures, and **the first attempt
at one of them was wrong** — recorded in FR-016 rather than quietly corrected,
because it is the same mistake osapi's baseline made.

**It is read while reading osapi's.** This repository exists to be imported, so
its section 2 is written to be read alongside
[osapi's baseline](../../../osapi/specs/006-osapi-baseline/spec.md), whose
FR-115 states the same edge from the other end.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A consumer knows what the wrapper gives them (Priority: P1)

Somebody working in osapi, or writing a new consumer, can state what
`nats-client` does for them that the upstream NATS client does not — and what
they still have to do themselves.

**Why this priority**: it is the question a wrapper exists to answer, and the
only one whose answer is not in the upstream library's own documentation.

**Independent Test**: a reader given the corpus alone states what the wrapper
adds, names the three authentication modes, and says which JetStream primitives
it covers — without opening `pkg/client`.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a reader asks how a consumer authenticates,
   **Then** the three modes and what each needs are stated.
2. **Given** the corpus, **When** a reader asks what happens when the connection
   drops, **Then** the answer is stated rather than left to the upstream
   library's defaults.

______________________________________________________________________

### User Story 2 - A breaking change is recognisable before it is made (Priority: P1)

Somebody changing `pkg/client` knows what osapi depends on, and that osapi pins
a commit rather than a tag — so nothing breaks there until somebody bumps it.

**Why this priority**: the consequence is delayed rather than absent, which is
the more dangerous shape. A rename lands green here and breaks at the bump, by
which time the change is no longer in view.

**Independent Test**: this specification states the exported surface as a
contract, and states the pin.

______________________________________________________________________

### User Story 3 - The seven sections read the same as every other baseline (Priority: P2)

Somebody reading all six baselines in order finds the same answer in the same
place each time.

**Why this priority**: lower on its own and the reason the programme exists.
`osapi-justfiles`' baseline found that three section **headings** had drifted
from `system`'s names while the order and meaning were right, and this is the
first baseline written after that was corrected.

### Edge Cases

- **A wrapper's contract is what it adds, not what it exposes.** Twenty-five
  `Client` methods and nine exported types are the surface; a consumer depends
  on those *plus* the upstream `jetstream.Msg` and `nats.Conn` types that leak
  through them. Stating only the former would describe the package and not the
  dependency.
- **A count that includes a dependency's files.** The first measurement of
  documentation pages returned 9, not 8, because `docs/node_modules/` holds a
  vendored `README.md`. 002 recorded 8 and 002 was right. Recorded in FR-016
  because it is the same class of error as osapi's 219-against-221, and the
  correction here is the exclusion rather than a definition.
- **A test suite is exported.** Fourteen of the twenty-three exported type names
  in `pkg/client` are `*TestSuite` types in `_test.go` files, so an
  exported-surface count taken without excluding tests overstates the contract
  by more than half.
- **A repository with no dependents but one consumer.** Nothing in the
  organization imports `nats-client` except osapi, and `nats-client` imports
  nothing from the organization. Its section 2 is therefore one edge, stated
  from both ends.

## Requirements *(mandatory)*

Every requirement is *the corpus MUST state X*, and each names how it was
checked. The seven section names below are `system`'s 002 FR-001 names verbatim.

### 1. What this repository is

- **FR-001**: The corpus MUST state that `nats-client` is a **Go library
  wrapping the upstream NATS client**, exposing one package, `pkg/client`, and
  one constructor. It is not a service, has no entry point and ships no binary.
  Verified:
  `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' | wc -l`
  returns 11 files, and the only exported function is `New`.
- **FR-002**: The corpus MUST state what the wrapper **adds** over the upstream
  library, because that is the only part a consumer cannot read in NATS' own
  documentation: a single `Client` holding connection and JetStream context
  together, authentication reduced to three declared modes, and create-or-update
  helpers for streams, consumers, key-value buckets and object stores. What it
  does not add is a new protocol, a new wire format, or any retry policy of its
  own.

### 2. Where it sits

- **FR-003**: The corpus MUST state that `nats-client` depends on **no other
  repository in the organization**, and that **one** imports it: `osapi`.
  Verified from both ends — `grep -oE "osapi-io/[a-z-]+" go.mod` in this
  repository returns only its own module path, and the same command in
  `osapi/go.mod` returns `nats-client`.
  [osapi's baseline FR-115](../../../osapi/specs/006-osapi-baseline/spec.md)
  states the same edge from the other side.
- **FR-004**: The corpus MUST state what breaks in that direction and **when**:
  a change to the exported surface of `pkg/client` breaks osapi's transport
  layer, but osapi pins a **pseudo-version commit rather than a tag**
  (`v0.0.0-20260412170202-5d1c1a26fa5a`), so nothing breaks there until somebody
  bumps it. The consequence is delayed rather than absent, which is why a rename
  and its bump want to land together.
- **FR-005**: The corpus MUST state that `nats-client` also depends on
  `osapi-justfiles` for its build — the `go`, `just` and `md` modules — that
  this edge appears in no `go.mod` because it is fetched by a justfile recipe,
  and that the fetch is unpinned. Owner of the pinning: those repositories. See
  [osapi-justfiles' baseline FR-017](../../../osapi-justfiles/specs/001-justfiles-baseline/spec.md).

### 3. Architecture

Stated at the level 002's FR-004 to FR-006 require: what each part is for and
what passes between parts, nothing a rename would falsify.

- **FR-006**: The corpus MUST state that the package is **one type with one
  responsibility per file**, and what each file is for rather than what it
  currently calls: connecting and authenticating (`connect.go`,
  `connect_wrapper.go`), connection state and lifecycle (`connection.go`), core
  publish and subscribe (`core.go`), JetStream streams (`jetstream.go`),
  consumers (`consumer.go`), key-value (`kv.go`), key-value with publish
  (`kv_stream.go`), object stores (`objectstore.go`), and the option and
  authentication types (`types.go`). A consumer holds one `Client` and reaches
  all of it.
- **FR-007**: The corpus MUST state what passes across the boundary in each
  direction: an `Options` struct in, and **upstream NATS types out** —
  `jetstream.Msg` reaches a consumer's handler, and `nats.Conn` is reachable
  through the wrapper. The wrapper is therefore not an abstraction over NATS; it
  is a convenience layer that does not hide it, and a consumer who expected
  isolation would be wrong.
- **FR-008**: The corpus MUST state that a `NATSConnector` interface exists so
  the connection can be substituted in tests, and that this is the **only** seam
  — everything else is concrete. Verified:
  `grep -hE '^type [A-Z][A-Za-z]* interface' pkg/client/*.go` returns one
  result.
- **FR-009**: The corpus MUST state that the repository ships **five runnable
  examples** under `examples/`, one per authentication mode and one per
  JetStream pattern it supports, and that these are the executable form of the
  documentation rather than an extra to keep in step.

### 4. The contract

- **FR-010**: The corpus MUST state that the contract is the **exported surface
  of `pkg/client`**: one constructor, 25 `Client` methods, and 9 exported types.
  Everything under `pkg/client/mocks/` is generated and is not the contract.
  Verified with the test files excluded — see FR-016 for why that exclusion is
  not optional.
- **FR-011**: The corpus MUST state the **three authentication modes** and what
  each requires, because they are the part of the contract a consumer must
  satisfy before anything else works: `NoAuth`; `UserPassAuth`, needing a
  username and password; and `NKeyAuth`, needing the path to an Ed25519 private
  seed file. Verified: `AuthType` and `AuthOptions` in `pkg/client/types.go`.
- **FR-012**: The corpus MUST state what the contract does **not** promise: no
  retry or reconnection policy of the wrapper's own, no abstraction over the
  upstream types FR-007 names, and no stability guarantee beyond what the pin in
  FR-004 gives — the repository publishes no tags, so a consumer depends on a
  commit.

### 5. Measurements

- **FR-013**: The corpus MUST state each count with the command that reproduces
  it. Measured 2026-09-30 at `cfe12f6`:

  | Measurement                    | Value | Command                                                                                                                     |
  | ------------------------------ | ----: | --------------------------------------------------------------------------------------------------------------------------- |
  | Go files                       |    33 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                        |
  | Go files excluding tests       |    20 | the same, plus `-not -name '*_test.go'`                                                                                     |
  | Non-test files in `pkg/client` |    11 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                                                  |
  | `Client` methods               |    25 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^func \(c \*Client\) [A-Z]' {} + \| wc -l` |
  | Exported types in `pkg/client` |     9 | the same, with `grep -hE '^type [A-Z]'`                                                                                     |
  | Exported functions             |     1 | the same, with `grep -hE '^func [A-Z]'` — `New`                                                                             |
  | Documentation pages            |     8 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                             |
  | README lines                   |    62 | `wc -l README.md`                                                                                                           |
  | Runnable examples              |     5 | `ls -d examples/*/ \| wc -l`                                                                                                |

### 6. Gaps

- **FR-014**: The corpus MUST record that the repository **publishes no tags**,
  so its only consumer pins a pseudo-version commit. Nothing is wrong with the
  code; what is missing is a way for a consumer to say which version it wants.
  The rule this strains is `global/tooling`'s "both provisioning paths resolve
  to the same version", which has no mechanism here rather than a divergent one
  — the same shape `osapi-justfiles`' unpinned fetch has, and stated the same
  way. Owner: `nats-client`, with a bump in `osapi`.

- **FR-015**: The corpus MUST record that the wrapper **leaks upstream types**
  (FR-007) and that this is a deliberate design rather than a defect — but that
  nothing in the repository says so, so a consumer who expected an abstraction
  learns otherwise by reading the signatures. Owner: `nats-client`, if it
  chooses to say so; this baseline records that it currently does not.

- **FR-016**: The corpus MUST record that **two of this baseline's own
  measurements were wrong on the first attempt**, and what the error was in each
  case, because both are errors of *command* rather than of arithmetic:

  - The documentation page count returned **9** instead of 8, because
    `docs/node_modules/prettier/README.md` is a vendored dependency's file
    rather than a page. `system`'s 002 recorded 8 and was right. The correction
    is an exclusion, and osapi's baseline needed the same one.
  - The exported-type count returned **23** instead of 9, because fourteen
    `*TestSuite` types live in `_test.go` files. An exported-surface count taken
    without excluding tests overstates the contract by more than half, and it
    overstates it in the direction that reads plausible.

  Both were caught by running the command rather than by re-reading a number,
  which is the argument for `global/baseline` pairing a count with its command.

### 7. What this inventory excludes

- **FR-017**: The corpus MUST state what it leaves out, so an omission is never
  mistaken for an oversight:

  - **How NATS itself works.** Streams, consumers, key-value and object stores
    are upstream concepts; this states what the wrapper does with them.
  - **What each of the 25 methods does.** They are named as the contract; their
    individual behaviour is the eight documentation pages' subject and is cited
    rather than copied.
  - **The generated mocks.** `pkg/client/mocks/` is generated and is not the
    contract.
  - **The repository's own contributor conventions.** Its `AGENTS.md` and
    `CONTRIBUTING.md`, cited rather than copied.
  - **Whether the wrapper is the right shape.** This states what it is, not
    whether a consumer should want it.

- **FR-018**: The corpus MUST state that **no section of the seven was
  omitted**, and that the section names are `system`'s 002 names verbatim. This
  is the first baseline written after `osapi-justfiles`' FR-021a recorded that
  three headings had drifted; copying that corrected file rather than
  re-deriving the names is what kept them right, which is exactly the
  propagation FR-021a predicted.

### Key Entities

- **Client**: The one type a consumer holds. Carries connection and JetStream
  context together and exposes 25 methods.
- **Options**: What a consumer passes in — host, port, name, and authentication.
- **Authentication mode**: One of three — none, user and password, or NKEY.
- **Leaked upstream type**: A NATS type reaching a consumer through the
  wrapper's signatures. `jetstream.Msg` and `nats.Conn` are the two that matter.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given the corpus alone states what the wrapper adds over
  the upstream library, names the three authentication modes, and says which
  JetStream primitives it covers.
- **SC-002**: Every count is paired with a command, and running the nine
  commands reproduces the nine values.
- **SC-003**: A reader can state what breaks when `pkg/client`'s surface
  changes, and **when** it breaks — not at the change, but at the bump.
- **SC-004**: The three gaps are stated with both sides named and an owner, and
  none is corrected here.
- **SC-005**: All seven sections are present, in 002's order, under 002's names
  verbatim.
- **SC-006**: `just test` passes in the specs repository.
- **SC-007**: Nothing in the `nats-client` repository changes.

## Assumptions

- The measurements are of `cfe12f6`. Counts will date; the commands are what
  survives, and FR-016 records that the commands are where the errors were.
- The eight documentation pages stay where they are. Each documents one part of
  the package's surface for a consumer of the library, which is the same reason
  002's FR-028 leaves `gohai/docs/collectors/` in place.
- `nats-server` is a separate repository with a separate baseline, unit 8. The
  two are read together by a reader of osapi's transport layer but neither
  imports the other.
- Nothing about the missing tags is being proposed here. FR-014 records that a
  consumer cannot name a version; what to do about it belongs to a change in the
  repository that owns it.
