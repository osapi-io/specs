# Main Project Specification

> **Revision**: 2026-09-30 — Seeded from nats server baseline
> (`specs/001-nats-server-baseline`): 3 user stories, 19 functional requirements, 4
> entities, 4 edge cases, 7 measurable outcomes, 4 assumptions.
> Nothing folded — the project's first archival, so every entry is new under the
> feature's own IDs.

> **Revision**: 2026-09-30 — Every finding in this baseline came from **reading
> `Start()` in order**, not from counting. The ten counts reproduced first time and
> revealed nothing. What the reading found was a statement order, two literal
> arguments, and an absent statement: the logger is attached after the server has
> started, debug and trace are switched on unconditionally, and one option has no
> default. No count reveals an order and no signature does either.

> **Revision**: 2026-09-30 — The specification claimed all three facts were stated
> in none of the five documentation pages. **Two of them are partly documented**,
> and the refinement is archived rather than the overclaim: where trace output lands
> is documented while its being unconditional is not, and `ReadyTimeout` is
> documented in three pages while the absence of a default is not — because the
> `Options` table has no Default column at all.

## What this repository is

- **FR-001**: `nats-server` is a Go library that runs a NATS server **inside its
  consumer's process**. It exposes one package, `pkg/server`, and one constructor.
  It is not a daemon, ships no binary, and has no entry point of its own — the
  server it starts is a goroutine in somebody else's program. `pkg/server` holds
  four non-test files, and `New` is the only exported function.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-001]

- **FR-002**: The package does four things for a consumer, and `Start()` is where
  all four happen. It starts the upstream server in a goroutine, blocks until that
  server reports itself ready or the timeout lapses, turns a failure to become
  ready into an error, and routes the server's own logging into the consumer's
  `slog`.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-002]

## Where it sits

- **FR-003**: `nats-server` depends on no other repository in the organization,
  and one imports it: `osapi`. The edge is verified from both ends —
  `grep -oE "osapi-io/[a-z-]+" go.mod` here returns only its own module path, and
  the same command in `osapi/go.mod` returns `nats-server`.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-003]

- **FR-004**: osapi pins it by pseudo-version commit rather than by tag, so a
  change to this package's surface does not break osapi until somebody bumps it.
  The consequence is delayed rather than absent, which is the same shape
  `nats-client` has at the other end of the transport, and the reason a rename and
  its bump want to land together.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-004]

- **FR-005**: It also depends on `osapi-justfiles` for its build. That edge appears
  in no `go.mod`, because a justfile recipe fetches it, and the fetch is unpinned.
  Pinning it belongs to those repositories.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-005]

## Architecture

- **FR-006**: Four non-test files, one subject each. `server.go` holds the
  lifecycle and the order `Start()` performs it. `types.go` holds the option struct
  and what it embeds. `server_wrapper.go` holds the interface that makes the
  upstream server substitutable. `logger.go` holds the adapter that routes NATS'
  logging into `slog`. A consumer holds one `Server` and calls two methods.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-006]

- **FR-007**: `Start()` does things in this order: construct the upstream server,
  start it in a goroutine, wait for `ReadyForConnections`, **then** attach the
  logger, then record the instance. The order matters more than any single
  statement in it — two of this repository's three gaps are consequences of it, and
  neither is visible from the signatures.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-007]

- **FR-008**: The contract exposes exactly two methods: `Start`, which returns an
  error, and `Stop`, which returns nothing. Everything else a consumer can reach
  comes through the embedded upstream option struct rather than through this
  package's own surface.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-008]

- **FR-009**: `NATSServerInstance` is the only seam. It declares the four upstream
  methods this package calls — `Start`, `ReadyForConnections`, `SetLogger` and
  `Shutdown` — so the upstream server can be substituted in tests and nothing else
  can be.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-009]

- **FR-010**: Four runnable examples ship with it, one per authentication mode
  plus a plain server. They are the executable form of the documentation rather
  than an extra to keep in step.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-010]

## The contract

- **FR-011**: `Options` **embeds `*natsserver.Options`** — the upstream server's
  entire option struct — and adds exactly one field of its own, `ReadyTimeout`. So
  the contract this repository maintains is mostly not its own: a consumer can
  reach every upstream option through it, and a change upstream changes this
  package's surface with no commit here. `types.go` is four lines long and is the
  most consequential file in the repository.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-011]

- **FR-012**: Beyond that embedding, the contract is one constructor, two methods,
  three exported types — `Server`, `Options` and `SlogWrapper` — and the one
  interface. Everything under `pkg/server/mocks/` is generated and is not the
  contract.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-012]

- **FR-013**: Two things the contract does not let a consumer decide, and neither
  is visible from a signature: whether debug and trace logging are on, and whether
  the logger sees startup. They always are, and it does not. See the gaps below.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-013]

## Measurements

- **FR-016**: Measured 2026-09-30 at `7ac142e`. Each count carries the command
  that reproduces it, because a number alone is a claim that was true when somebody
  typed it.

  | Measurement                    | Value | Command                                                                                     |
  | ------------------------------ | ----: | ------------------------------------------------------------------------------------------- |
  | Go files                       |    12 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                        |
  | Go files excluding tests       |    10 | the same, plus `-not -name '*_test.go'`                                                     |
  | Non-test files in `pkg/server` |     4 | `find pkg/server -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                  |
  | Exported functions             |     1 | the same, with `grep -hE '^func [A-Z]'` — `New`                                             |
  | Exported methods               |     8 | the same, with `grep -hE '^func \([a-z]+ \*[A-Za-z]+\) [A-Z]'` — 2 on `Server`, 6 on `SlogWrapper` |
  | Exported types                 |     4 | the same, with `grep -hE '^type [A-Z]'`                                                     |
  | Interfaces                     |     1 | the same, with `grep -hE '^type [A-Z][A-Za-z]* interface'`                                  |
  | Documentation pages            |     5 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                              |
  | README lines                   |    58 | `wc -l README.md`                                                                           |
  | Runnable examples              |     4 | `ls -d examples/*/ \| wc -l`                                                                |

  The `node_modules` exclusion on the page count is unnecessary here and carried on
  purpose: `nats-client` got that count wrong for want of it, and two sibling
  baselines using different commands invites a reader to wonder which is right.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-016]

## Gaps

Three, all found by reading `Start()` rather than by counting anything. Two of the
three are partly documented, and how far is stated with each. None was corrected
by the baseline.

- **FR-014**: **Debug and trace logging are enabled unconditionally.** `Start()`
  calls `SetLogger(wrapper, true, true)`, and nothing in `Options` or `New()` can
  change either flag. A consumer embedding this in a production binary gets full
  trace output from the NATS server. `docs/server/logging.md` documents the
  *mapping* — `Tracef()` → `slog.Debug()`, alongside the other five levels — so a
  reader learns where trace output lands. What no page says is that trace is
  switched on unconditionally, and documenting where a signal goes is not
  documenting that the signal never stops. Owner: `nats-server`.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-014]

- **FR-015**: **The logger is attached after the server has started and become
  ready**, so everything logged during startup goes to the upstream default logger
  rather than the consumer's `slog`. A consumer debugging a server that failed to
  become ready finds their own logger empty and the reason on stderr. `SetLogger`
  appears in none of the five documentation pages. Owner: `nats-server`.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-015]

- **FR-016a**: **`ReadyTimeout` has no default.** `New()` performs no defaulting,
  so a consumer who leaves it unset passes a zero duration to
  `ReadyForConnections`. All four examples set it to 5 seconds explicitly, which is
  how the absence stays invisible: every path a reader is shown supplies the value.
  `docs/server/configuration.md` documents the field — an `Options` table with
  columns Field, Type and Description — and **that table has no Default column**.
  So the omission is structural rather than careless: a table that cannot express a
  default cannot record the absence of one, and a reader sees a documented field
  with an example value and has no reason to ask. Owner: `nats-server`.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-016a]

## What this inventory excludes

- **FR-017**: Named omissions, so an omission is never mistaken for an oversight.
  **How the NATS server itself works** — clustering, JetStream, accounts,
  authentication — is upstream's subject; this states what the wrapper does with the
  upstream server. **The upstream option struct's fields**, which `Options` embeds
  and a consumer can reach, are upstream's to document and change, and restating
  them here would drift. **What each of the five documentation pages says**: they
  are cited as where configuration, lifecycle and logging are described, and the
  gaps above record what each does and does not say about the three findings.
  **The generated mocks.** And **whether embedding a NATS server is the right
  design for osapi**, which is osapi's question.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-017]

- **FR-018**: No section of the seven was omitted, and the section names are
  `system`'s 002 names verbatim — inherited from `nats-client`'s baseline, which
  inherited them from `osapi-justfiles`' after that one recorded three of them
  drifting. Two hops without drift was the first evidence the correction holds
  rather than merely having been made once.
  [Source: specs/001-nats-server-baseline/spec.md -> FR-018]

## What the words mean

- **Server**: The one type a consumer holds. Two methods, `Start` and `Stop`.
- **Options**: The upstream option struct embedded whole, plus `ReadyTimeout`.
- **SlogWrapper**: The adapter turning NATS' logger interface into `slog` calls,
  mapping trace onto debug because `slog` has no trace level.
- **Undocumented decision**: Something `Start()` settles that a consumer cannot
  change and no page mentions. Three exist.
  [Source: specs/001-nats-server-baseline/spec.md -> Key Entities]
