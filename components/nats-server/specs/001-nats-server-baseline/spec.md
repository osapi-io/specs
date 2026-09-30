# Feature Specification: A baseline for nats-server

**Feature Branch**: `001-nats-server-baseline`

**Created**: 2026-09-30

**Status**: Draft

**Input**: `nats-server`'s `.specify/memory/` holds only a constitution composed
from `.charter/`, so it states what binds every repository and nothing about
this one. Unit 8 of the baseline programme `system`'s
[002](../../../../system/specs/002-baseline-shape/spec.md) defines, and the
second of the two NATS repositories osapi imports.

## What this specification is, and what it is not

**Its subject is a description, not a change.** Nothing lands in the
`nats-server` repository. What this produces is an inventory of how it behaves
today, which lives in this feature directory and reaches memory through
archival.

**Prose was a lead, never a source** — and here that mattered more than in any
baseline so far. Five documentation pages and a 58-line README describe this
package, and **three facts a consumer needs are in none of them**: the logger is
attached after the server has already started, debug and trace are switched on
unconditionally, and one option has no default. All three were found by reading
`Start()`, and all three are recorded as gaps rather than as prose.

**It is read alongside `nats-client`'s.** The two repositories are the transport
half of osapi and neither imports the other. Their baselines are deliberately
shaped the same way so a reader moving between them finds the same answer in the
same place.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A consumer knows what embedding the server costs them (Priority: P1)

Somebody embedding NATS in their own binary can state what this package does on
their behalf, what it decides for them without asking, and what they must still
supply.

**Why this priority**: it is the whole question. A package this small either
saves a consumer the four lines it wraps or makes decisions they did not know
were being made, and the difference is only visible by reading `Start()`.

**Independent Test**: a reader given the corpus alone states what `Start()` does
in order, names what is not configurable, and says which option has no default —
without opening `pkg/server`.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a reader asks what logging they will get,
   **Then** the answer states that debug and trace are on unconditionally and
   that startup logs do not reach their logger.
2. **Given** the corpus, **When** a reader asks what they must set in `Options`,
   **Then** `ReadyTimeout` is named along with the fact that it has no default.

______________________________________________________________________

### User Story 2 - The contract is recognised as mostly somebody else's (Priority: P1)

Somebody changing this package knows that `Options` **embeds** the upstream
server's entire option struct, so the contract they are maintaining is largely
not theirs.

**Why this priority**: equal to the first. An embedded struct is a contract a
consumer can reach every field of, and a change to the upstream library changes
this package's surface without any commit here.

**Independent Test**: this specification states that the contract is the
upstream option struct plus one field, and names the field.

______________________________________________________________________

### User Story 3 - The two NATS baselines read as a pair (Priority: P2)

Somebody reading `nats-client`'s baseline and then this one finds the same seven
sections in the same order, and can see that the two packages wrap opposite ends
of the same library.

**Why this priority**: lower than the two above, and it is the programme's
purpose. Both were written to `system`'s section names verbatim, and this one
inherited them from a file that had already been corrected once.

### Edge Cases

- **A wrapper that decides something for its consumer.** `Start()` calls
  `SetLogger(wrapper, true, true)` — debug and trace unconditionally, with no
  option to turn either off. A consumer embedding this in a production binary
  gets full trace logging and nothing in the repository tells them so.
- **A logger attached too late to see the thing it was attached for.** The
  sequence in `Start()` is: construct, `go Start()`, wait for readiness, *then*
  `SetLogger`. Everything the server logs while starting and becoming ready goes
  to the upstream default logger, not the consumer's `slog`. A consumer
  debugging a failed start finds their logger empty.
- **An option with no default.** `New()` does no defaulting, so a consumer who
  leaves `ReadyTimeout` unset passes a zero duration to `ReadyForConnections`.
  All four examples set it explicitly to 5 seconds, which is exactly how the
  absence of a default stays invisible: every path a reader is shown supplies
  the value.
- **Trace and debug are indistinguishable downstream.** `SlogWrapper.Tracef`
  calls `logger.Debug`, so NATS trace output arrives in a consumer's logs at
  debug level with nothing marking it as trace. Deliberate — `slog` has no trace
  level — and **documented**: `docs/server/logging.md` carries the mapping
  table. It is listed here because it compounds FR-014 rather than because it is
  hidden: a consumer who cannot turn trace off also cannot filter it out.

## Requirements *(mandatory)*

Every requirement is *the corpus MUST state X*, and each names how it was
checked. The seven section names below are `system`'s 002 FR-001 names verbatim.

### 1. What this repository is

- **FR-001**: The corpus MUST state that `nats-server` is a **Go library that
  runs a NATS server inside its consumer's process**, exposing one package,
  `pkg/server`, and one constructor. It is not a daemon, ships no binary, and
  has no entry point of its own — the server it starts is a goroutine in
  somebody else's program. Verified:
  `find pkg/server -maxdepth 1 -name '*.go' -not -name '*_test.go' | wc -l`
  returns 4, and the only exported function is `New`.
- **FR-002**: The corpus MUST state what the package **does for a consumer**,
  because it is small enough that the answer is short and specific: it starts
  the upstream server in a goroutine, blocks until it reports ready or the
  timeout lapses, turns a failure to become ready into an error, and routes the
  server's own logging into the consumer's `slog`. Four things, and `Start()` is
  where all four happen.

### 2. Where it sits

- **FR-003**: The corpus MUST state that `nats-server` depends on **no other
  repository in the organization**, and that **one** imports it: `osapi`.
  Verified from both ends — `grep -oE "osapi-io/[a-z-]+" go.mod` here returns
  only its own module path, and the same command in `osapi/go.mod` returns
  `nats-server`.
- **FR-004**: The corpus MUST state that osapi pins a **pseudo-version commit
  rather than a tag**, so a change to this package's surface does not break
  osapi until somebody bumps it. The consequence is delayed rather than absent,
  which is the same shape
  [nats-client's baseline FR-004](../../../nats-client/specs/001-nats-client-baseline/spec.md)
  records for the other half of the transport.
- **FR-005**: The corpus MUST state that it also depends on `osapi-justfiles`
  for its build, that this edge appears in no `go.mod` because a justfile recipe
  fetches it, and that the fetch is unpinned. Owner of the pinning: those
  repositories.

### 3. Architecture

- **FR-006**: The corpus MUST state what each of the four non-test files is
  **for**: the server's lifecycle and the order `Start()` performs it
  (`server.go`), the option struct and what it embeds (`types.go`), the
  interface that makes the upstream server substitutable (`server_wrapper.go`),
  and the adapter that routes NATS' logging into `slog` (`logger.go`). A
  consumer holds one `Server` and calls two methods.
- **FR-007**: The corpus MUST state **the order `Start()` does things in**,
  because two of this repository's three gaps are consequences of it and neither
  is visible from the signatures: construct the upstream server, start it in a
  goroutine, wait for `ReadyForConnections`, **then** attach the logger, then
  record the instance. Verified: `pkg/server/server.go`.
- **FR-008**: The corpus MUST state that the contract exposes exactly **two
  methods** — `Start` returning an error and `Stop` returning nothing — and that
  everything else a consumer can reach comes through the embedded upstream
  option struct rather than through this package's own surface.
- **FR-009**: The corpus MUST state that `NATSServerInstance` is the **only**
  seam, declaring the four upstream methods this package calls — `Start`,
  `ReadyForConnections`, `SetLogger`, `Shutdown` — so the upstream server can be
  substituted in tests and nothing else can. Verified:
  `grep -hE '^type [A-Z][A-Za-z]* interface'` returns one result.
- **FR-010**: The corpus MUST state that the repository ships **four runnable
  examples**, one per authentication mode plus a plain server, and that they are
  the executable form of the documentation rather than an extra to keep in step.

### 4. The contract

- **FR-011**: The corpus MUST state that `Options` **embeds
  `*natsserver.Options`** — the upstream server's entire option struct — and
  adds exactly one field of its own, `ReadyTimeout`. So **the contract this
  repository maintains is mostly not its own**: a consumer can reach every
  upstream option through it, and a change upstream changes this package's
  surface with no commit here. Verified: `pkg/server/types.go`.
- **FR-012**: The corpus MUST state that the contract is otherwise one
  constructor, two methods, and three exported types — `Server`, `Options` and
  `SlogWrapper` — plus the one interface. Everything under `pkg/server/mocks/`
  is generated and is not the contract.
- **FR-013**: The corpus MUST state what the contract does **not** let a
  consumer decide, because this is the part a signature does not show: whether
  debug and trace logging are on (they always are — FR-014), and whether the
  logger sees startup (it does not — FR-015).

### 5. Measurements

- **FR-016**: The corpus MUST state each count with the command that reproduces
  it. Measured 2026-09-30 at `7ac142e`:

  | Measurement                    | Value | Command                                                                                            |
  | ------------------------------ | ----: | -------------------------------------------------------------------------------------------------- |
  | Go files                       |    12 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                               |
  | Go files excluding tests       |    10 | the same, plus `-not -name '*_test.go'`                                                            |
  | Non-test files in `pkg/server` |     4 | `find pkg/server -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                         |
  | Exported functions             |     1 | the same, with `grep -hE '^func [A-Z]'` — `New`                                                    |
  | Exported methods               |     8 | the same, with `grep -hE '^func \([a-z]+ \*[A-Za-z]+\) [A-Z]'` — 2 on `Server`, 6 on `SlogWrapper` |
  | Exported types                 |     4 | the same, with `grep -hE '^type [A-Z]'`                                                            |
  | Interfaces                     |     1 | the same, with `grep -hE '^type [A-Z][A-Za-z]* interface'`                                         |
  | Documentation pages            |     5 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                    |
  | README lines                   |    58 | `wc -l README.md`                                                                                  |
  | Runnable examples              |     4 | `ls -d examples/*/ \| wc -l`                                                                       |

  The `node_modules` exclusion is carried deliberately. It is not needed here —
  this repository has no vendored markdown — but
  [nats-client's baseline FR-016](../../../nats-client/specs/001-nats-client-baseline/spec.md)
  records a count that was wrong for exactly that reason, and a command that
  differs between two sibling baselines invites the reader to wonder which one
  is right.

### 6. Gaps

Three, all found by reading `Start()`. **Two of the three are partly documented
and the amendment below says exactly how far** — the original wording claimed
all three were "stated in none of the five documentation pages", which was true
of one and an overclaim about two. None is corrected here.

- **FR-014**: The corpus MUST record that **debug and trace logging are enabled
  unconditionally**. `Start()` calls `SetLogger(wrapper, true, true)`, and
  nothing in `Options` or `New()` can change either flag. A consumer embedding
  this in a production binary gets full trace output from the NATS server and
  nothing in the repository warns them. Verified: `pkg/server/server.go:59`, and
  `grep -rn 'SetLogger' pkg/server/*.go` finds the one call site. Owner:
  `nats-server`.

  **What the pages do say, and where the line falls.** `docs/server/logging.md`
  documents the *mapping* — a table giving `Tracef()` → `slog.Debug()` alongside
  the other five levels — so a reader learns where trace output lands. What no
  page says is that trace is **switched on unconditionally**, which is the fact
  that makes the mapping matter: a reader could reasonably take that table as
  describing what happens *if* trace is enabled. Documenting where a signal goes
  is not documenting that the signal is always on.

- **FR-015**: The corpus MUST record that **the logger is attached after the
  server has started and become ready**, so everything logged during startup
  goes to the upstream default logger rather than the consumer's `slog`. A
  consumer debugging a server that failed to become ready finds their own logger
  empty and the reason on stderr. Verified: the statement order in `Start()`.
  Owner: `nats-server`.

- **FR-016a**: The corpus MUST record that **`ReadyTimeout` has no default**.
  `New()` performs no defaulting, so a consumer who leaves it unset passes a
  zero duration to `ReadyForConnections`. All four examples set it to 5 seconds
  explicitly, which is how the absence stays invisible: every path a reader is
  shown supplies the value, so nothing reveals that the value is required.
  Owner: `nats-server`.

  **What the pages do say, and the precise mechanism of the omission.**
  `docs/server/configuration.md` documents the field — an `Options` table with
  columns Field, Type and Description, giving `ReadyTimeout` as "Max wait time
  for server readiness after start" — and its example sets it to 5 seconds.
  **That table has no Default column.** So the omission is not carelessness in
  the prose; it is structural. A table that cannot express a default cannot
  record the absence of one, and a reader sees a documented field with an
  example value and has no reason to ask.

### 7. What this inventory excludes

- **FR-017**: The corpus MUST state what it leaves out, so an omission is never
  mistaken for an oversight:

  - **How the NATS server itself works.** Clustering, JetStream, accounts and
    authentication are upstream concepts; this states what the wrapper does with
    the upstream server, not what that server is.
  - **The upstream option struct's fields.** `Options` embeds them and a
    consumer can reach all of them; they are upstream's to document and change,
    and restating them here would drift — `global/documentation`.
  - **What each of the five documentation pages says.** They are cited as where
    configuration, lifecycle and logging are described for a consumer, not
    copied. FR-014, FR-015 and FR-016a record what each page does and does not
    say about the three findings — one is absent entirely, and two are partly
    covered in a way that reads as complete.
  - **The generated mocks.** `pkg/server/mocks/` is generated and is not the
    contract.
  - **Whether embedding a NATS server is the right design for osapi.** That is
    osapi's question and its baseline's.

- **FR-018**: The corpus MUST state that **no section of the seven was
  omitted**, and that the section names are `system`'s 002 names verbatim,
  inherited from `nats-client`'s baseline — which inherited them from
  `osapi-justfiles`' after that one recorded three of them drifting. Two hops
  without drift is the first evidence the correction holds rather than merely
  having been made once.

### Key Entities

- **Server**: The one type a consumer holds. Two methods, `Start` and `Stop`.
- **Options**: The upstream option struct embedded whole, plus `ReadyTimeout`.
- **SlogWrapper**: The adapter turning NATS' logger interface into `slog` calls,
  mapping trace onto debug because `slog` has no trace level.
- **Undocumented decision**: Something `Start()` settles that a consumer cannot
  change and no page mentions. Three exist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given the corpus alone states what `Start()` does in
  order, names the two things that are not configurable, and says which option
  has no default.
- **SC-002**: Every count is paired with a command, and running the ten commands
  reproduces the ten values.
- **SC-003**: A reader can state that the contract is mostly the upstream option
  struct, and that a change upstream changes this package's surface with no
  commit here.
- **SC-004**: The three gaps are stated with what was measured, where, and an
  owner, and none is corrected here.
- **SC-005**: All seven sections are present, in 002's order, under 002's names
  verbatim.
- **SC-006**: `just test` passes in the specs repository.
- **SC-007**: Nothing in the `nats-server` repository changes.

## Assumptions

- The measurements are of `7ac142e`. Counts will date; the commands are what
  survives.
- The five documentation pages stay where they are. Each describes one part of
  the package for a consumer of the library, which is 002's FR-028 reasoning.
- The three gaps are recorded, not fixed. Each implies a change in `nats-server`
  and each is that repository's to make: a flag for debug and trace, attaching
  the logger before the goroutine starts, and a default for `ReadyTimeout`.
- `nats-client` is the other half of the transport and has its own baseline,
  unit 7. Neither repository imports the other.
