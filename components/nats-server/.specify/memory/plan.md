# Main Implementation Plan

> **Revision**: 2026-09-30 — Seeded from the NATS server baseline
> (`specs/001-nats-server-baseline`). A documentation feature: nothing in the
> `nats-server` repository changed. What is recorded here is what the repository
> is, what it decides on a consumer's behalf, and why reading four statements in
> sequence was the method rather than counting.

## What nats-server Is, and Where It Sits

**First, for the reason `global/baseline` gives**: memory states what the
repository is before it states what was decided about it.

`nats-server` is a Go library that **runs a NATS server inside its consumer's
process**. One package, `pkg/server`, one constructor, no binary, no entry point
of its own — the server it starts is a goroutine in somebody else's program.

It does four things, all of them in `Start()`: starts the upstream server in a
goroutine, blocks until it reports ready or the timeout lapses, turns a failure to
become ready into an error, and routes the server's own logging into the
consumer's `slog`.

**Three of those four have consequences a consumer cannot change**, and none is
visible from a signature — see "What Start() decides" below.
[Source: specs/001-nats-server-baseline/spec.md -> FR-001]
[Source: specs/001-nats-server-baseline/spec.md -> FR-002]

**Where it sits**: it depends on no other repository in the organization, and one
imports it — `osapi`, which pins a pseudo-version commit rather than a tag, so a
change to this package's surface does not break osapi until somebody bumps it. It
also depends on `osapi-justfiles` for its build through an unpinned justfile fetch
that appears in no `go.mod`.
[Source: specs/001-nats-server-baseline/spec.md -> FR-003]
[Source: specs/001-nats-server-baseline/spec.md -> FR-004]

## What Start() Decides, and the Consumer Cannot

The three findings, kept together because they are one reading rather than three
discoveries:

**Debug and trace are switched on unconditionally.** `SetLogger` is called with
both flags as literal `true`, and nothing in `Options` or `New()` can change
either. A consumer embedding this in a production binary gets full trace output.
`docs/server/logging.md` documents where trace output *lands* — the `Tracef()` →
`slog.Debug()` mapping — but not that it is always on, and documenting where a
signal goes is not documenting that the signal never stops.

**The logger is attached after the server is already running.** The order is:
construct, `go Start()`, wait for `ReadyForConnections`, *then* `SetLogger`. So
everything logged during startup goes to the upstream default logger, and a
consumer debugging a server that failed to become ready finds their own logger
empty and the reason on stderr. `SetLogger` appears in no documentation page.

**`ReadyTimeout` has no default.** `New()` performs no defaulting, so an unset
value reaches `ReadyForConnections` as a zero duration. All four examples set it
to 5 seconds, which is how the absence stays invisible — and the mechanism is
structural: `configuration.md`'s `Options` table has columns Field, Type and
Description and **no Default column at all**. A table that cannot express a
default cannot record the absence of one.
[Source: specs/001-nats-server-baseline/spec.md -> FR-014]
[Source: specs/001-nats-server-baseline/spec.md -> FR-015]
[Source: specs/001-nats-server-baseline/spec.md -> FR-016a]

## Technical Context

**Language/Version**: Go, `go 1.26.0`. 12 files, 10 of them not tests — the
smallest Go repository in the organization.
[Source: specs/001-nats-server-baseline/plan.md -> "Language/Version"]

**Primary Dependencies**: The upstream `nats-server/v2` library. Nothing from this
organization.

**Storage**: None of its own. What the embedded server persists is configured
through the upstream options a consumer reaches via the embedded struct.

**Testing**: Generated mocks under `pkg/server/mocks/`, substituted through the
one interface the package declares — `NATSServerInstance`, naming the four
upstream methods this package calls. That is the only seam.
[Source: specs/001-nats-server-baseline/spec.md -> FR-009]

**Target Platform**: Wherever its consumer runs.

**Project Type**: Go library, one package.

**Constraints**: `Options` **embeds** `*natsserver.Options`, so the contract this
repository maintains is mostly not its own — a consumer can reach every upstream
option through it, and a change upstream changes this package's surface with no
commit here. `types.go` is four lines long and is the most consequential file in
the repository.
[Source: specs/001-nats-server-baseline/spec.md -> FR-011]

**Scale/Scope**: One constructor, two methods on `Server`, six on `SlogWrapper`,
four exported types, one interface, five documentation pages, four runnable
examples.
[Source: specs/001-nats-server-baseline/spec.md -> FR-016]

## Project Structure

```text
nats-server/
├── pkg/server/                 # the one package: 4 non-test files
│   ├── server.go               #   lifecycle, and the order Start() uses
│   ├── types.go                #   Options: upstream's struct, plus ReadyTimeout
│   ├── server_wrapper.go       #   NATSServerInstance, the only seam
│   ├── logger.go               #   SlogWrapper: NATS logging into slog
│   └── mocks/                  #   generated; not the contract
├── examples/                   # 4 runnable, all setting ReadyTimeout explicitly
└── docs/                       # 5 pages
```

**Structure Decision**: one type a consumer holds, two methods to call, and
everything else reachable through the embedded upstream options.
[Source: specs/001-nats-server-baseline/spec.md -> FR-006]

## Why Reading Order Was the Method

Every baseline before this one was mostly counting. This one counted too, and the
counting found nothing: ten figures, all unremarkable, all reproducing first time.

**The three findings came from reading four statements in sequence.** Each
statement in `Start()` is unobjectionable; the *order* is what produces a consumer
whose logger never sees the startup it was attached to observe. No count reveals
an order, and `Start() error` says nothing about when the logger arrives. The same
reading found two literal arguments at a call site, and the absence of a
defaulting statement — a fact about what is *not* there.

This is `global/verification`'s "reading code and concluding is a hypothesis" from
the other side: the hypothesis was that a thin wrapper decides nothing, and
reading it falsified that. The counts could not have.

A future baseline for a small wrapper should copy that reading rather than
assuming a short file holds nothing.
[Source: specs/001-nats-server-baseline/plan.md -> "Why reading order was the method here"]

## What Verification Checks, and What It Cannot

The ten commands check the counts, and the counts were never in doubt. What no
command settles:

- **The statement order in `Start()`.** A reading, and the source of everything
  above.
- **Whether the three decisions matter to a consumer.** Debug and trace being
  unconditional is a fact; whether it is a problem depends on what a consumer
  embeds this in. **osapi does, and osapi's baseline does not mention it either.**
- **Whether the five pages are accurate about what they do cover.** They were read
  for what they omit, not verified line by line.
[Source: specs/001-nats-server-baseline/plan.md -> "What the verification checks, and what it cannot"]
