# Main Implementation Plan

> **Revision**: 2026-09-30 — Seeded from the NATS client baseline
> (`specs/001-nats-client-baseline`). A documentation feature: nothing in the
> `nats-client` repository changed, and nothing does from a baseline. What is
> recorded here is what the repository is, what it adds over the library it wraps,
> what it does not add, and what its one consumer depends on.

## What nats-client Is, and Where It Sits

**First, for the reason `global/baseline` gives**: memory states what the
repository is before it states what was decided about it.

`nats-client` is a Go library wrapping the upstream NATS client. One package,
`pkg/client`, one constructor, no entry point, no binary. What it **adds** is the
only part a consumer cannot read in NATS' own documentation: a single `Client`
holding connection and JetStream context together, authentication reduced to
three declared modes, and create-or-update helpers for streams, consumers,
key-value buckets and object stores.

What it does **not** add: a new protocol, a new wire format, and **no
reconnection behaviour of its own** — it passes no reconnect options and
registers no disconnect, reconnect or closed handler, so the upstream default
governs and a consumer is never notified when a drop or a recovery happens.
Resilience is not configurable through this wrapper.

**It does not hide NATS.** Upstream types reach a consumer through the wrapper's
signatures — `jetstream.Msg` in a handler, `nats.Conn` through the connection —
so this is a convenience layer rather than an abstraction, and a consumer who
expected isolation would be wrong. Nothing in the repository says so.
[Source: specs/001-nats-client-baseline/spec.md -> FR-002]
[Source: specs/001-nats-client-baseline/spec.md -> FR-007]
[Source: specs/001-nats-client-baseline/spec.md -> FR-012a]

**Where it sits**: it depends on no other repository in the organization, and one
imports it — `osapi`. A change to `pkg/client`'s exported surface breaks osapi's
transport layer, but osapi pins a **pseudo-version commit rather than a tag**, so
nothing breaks there until somebody bumps it. The consequence is delayed rather
than absent, which is why a rename and its bump want to land together. It also
depends on `osapi-justfiles` for its build, through an unpinned justfile fetch
that appears in no `go.mod`.
[Source: specs/001-nats-client-baseline/spec.md -> FR-003]
[Source: specs/001-nats-client-baseline/spec.md -> FR-004]

## Technical Context

**Language/Version**: Go, `go 1.26.0`. 33 files, 20 of them not tests.
[Source: specs/001-nats-client-baseline/plan.md -> "Language/Version"]

**Primary Dependencies**: The upstream NATS client and JetStream packages.
Nothing from this organization.
[Source: specs/001-nats-client-baseline/plan.md -> "Primary Dependencies"]

**Storage**: None of its own. It gives a consumer access to JetStream streams,
consumers, key-value buckets and object stores; what goes in them is the
consumer's.
[Source: specs/001-nats-client-baseline/spec.md -> FR-002]

**Testing**: Generated mocks under `pkg/client/mocks/`, substituted through the
one interface the package declares — `NATSConnector`. That is the only seam;
everything else is concrete.
[Source: specs/001-nats-client-baseline/spec.md -> FR-008]

**Target Platform**: Wherever its consumer runs. The library has none of its own.

**Project Type**: Go library, one package.
[Source: specs/001-nats-client-baseline/plan.md -> "Project Type"]

**Constraints**: The exported surface of `pkg/client` is the contract; everything
under `mocks/` is not. The repository publishes no tags, so a consumer depends on
a commit.
[Source: specs/001-nats-client-baseline/spec.md -> FR-010]
[Source: specs/001-nats-client-baseline/spec.md -> FR-012]

**Scale/Scope**: One constructor, 25 `Client` methods, 9 exported types, 8
documentation pages and 5 runnable examples. One dependency edge, verified from
both ends.
[Source: specs/001-nats-client-baseline/spec.md -> FR-013]

## Project Structure

```text
nats-client/
├── pkg/client/              # the one package: 11 non-test files
│   ├── types.go             #   Options, AuthOptions, AuthType
│   ├── connect.go           #   connecting and authenticating
│   ├── connection.go        #   connection state and lifecycle
│   ├── core.go              #   core publish and subscribe
│   ├── jetstream.go         #   streams
│   ├── consumer.go          #   consumers
│   ├── kv.go, kv_stream.go  #   key-value, and key-value with publish
│   ├── objectstore.go       #   object stores
│   └── mocks/               #   generated; not the contract
├── examples/                # 5 runnable, one per auth mode and pattern
└── docs/                    # 8 pages, one per part of the surface
```

**Structure Decision**: one type with one responsibility per file, and a consumer
holds one `Client` to reach all of it. The five examples are the executable form
of the documentation rather than an extra to keep in step.
[Source: specs/001-nats-client-baseline/spec.md -> FR-006]
[Source: specs/001-nats-client-baseline/spec.md -> FR-009]

## What Verification Checks, and What It Cannot

Re-running the nine commands checks the counts, and **two of them were wrong
before they were run** — a page count including a vendored file, and an
exported-type count including fourteen test suites. Both were errors of command
rather than arithmetic.

**A command could not have caught the third error.** An acceptance scenario
promised that the connection-drop behaviour was stated, and nothing stated it. No
count was wrong; a claim was. Only a reader asking the question found it, which is
what SC-001 is for and why it is a reading rather than a grep.

Three things the commands still do not check:

- **Whether the 25 methods are the right 25.** They are the contract as it
  stands; whether the wrapper should expose more or fewer is a judgement.
- **Whether the leaked upstream types matter.** The leak is undocumented in the
  repository; whether that is a problem depends on what a future consumer expects.
- **Whether the eight documentation pages are accurate.** They are cited as where
  a method's behaviour is described, not verified against the code. A page that has
  drifted from its method would not show up — the gap class osapi's baseline found
  three of.
[Source: specs/001-nats-client-baseline/plan.md -> "What the verification actually checks"]
