# Implementation Plan: A baseline for nats-client

**Branch**: `001-nats-client-baseline` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/nats-client/specs/001-nats-client-baseline/spec.md`

## Summary

State what `nats-client` is, so its memory stops holding only a constitution.
Eighteen requirements, every one of the form "the corpus MUST state X".

Unit 7 of twelve, and the first written **after** the shape had been tested. The
two baselines before it each found something about the shape itself — osapi's
that a hub's contract section is mostly citation, `osapi-justfiles`' that a
contract need not be code and that three section headings had drifted. This one
inherits both corrections and reports whether inheriting them worked, which is
FR-018.

**Nothing lands in the `nats-client` repository.** The deliverable is the
inventory.

## Technical Context

**Language/Version**: Markdown. The repository being inventoried is Go — 33
files, 20 of them not tests, `go 1.26.0` — and nothing in it changes.

**Primary Dependencies**: None. The corpus depends on nothing at runtime. The
repository being inventoried depends on no other repository in the organization.

**Storage**: `components/nats-client/specs/` for the specification — a directory
this feature creates, since it is the project's first — and
`components/nats-client/.specify/memory/` for what archival consolidates into.

**Testing**: `just test` in the specs repository. There is no code to unit test.
Every count carries the command that reproduces it, and re-running those nine
commands is what checks the inventory — the formatting gate cannot tell a right
count from a wrong one, and FR-016 records two counts that were wrong.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the `nats-client` repository. No count without its
command. Section names verbatim from 002. Every gap recorded with both sides and
an owner, none corrected here.

**Scale/Scope**: One repository inventoried, the second smallest with Go code. A
contract of one constructor, 25 methods and 9 types; one dependency edge, stated
from both ends.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                 |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | The eight documentation pages are cited rather than copied; what the wrapper *adds* is stated once, here.                                                                     |
| **Verification**  | Nine counts, each with its command — and **two were wrong on the first run**, both because of a missing exclusion rather than bad arithmetic. FR-016 records both.            |
| **Tooling**       | Nothing provisioned. FR-014 records the absent tags as the rule they strain rather than as a violation.                                                                       |
| **Correction**    | Three gaps with owners, none corrected. FR-016 records this feature's own measurement errors rather than presenting the corrected figures as though they were the first ones. |
| **Workflow**      | Stages 1 to 4 in one branch, which is what CONTRIBUTING's lifecycle table specifies and what the two preceding units did across three pull requests instead.                  |
| **Baseline**      | This memory holds no decisions yet, so the baseline is the whole of it — the condition `global/baseline` describes in reverse.                                                |
| **Repositories**  | The edge is verified from **both ends** rather than from this repository alone, which is what would have caught `osapi-justfiles`' missing seventh consumer.                  |
| **Tracking**      | Nothing becomes an issue. The two gaps implying work name their owner.                                                                                                        |

**Result**: no violations.

## What this unit inherits, and whether inheriting worked

Three corrections were available to it, and the plan records which were applied
because a later baseline will ask.

**The section names came from a corrected file.** `osapi-justfiles`' FR-021a
recorded that three of its seven headings had drifted from 002's names — each an
improvement in isolation — and predicted that later baselines would copy the
file rather than re-read 002. That is exactly what happened here, and because
the file had been corrected first, the drift did not propagate. FR-018 records
it: the prediction was right about the mechanism and the correction reached this
unit in time.

**The contract section did not need reinterpreting.** `osapi-justfiles` had to
decide that a contract need not be code. `nats-client` exposes Go, so section 4
is the ordinary case — and the decision that mattered instead was the opposite
one: the contract is not only the exported surface, because **upstream NATS
types leak through it** (FR-007). A consumer depends on `jetstream.Msg` whether
or not this repository names it.

**The both-ends check came from a failure.** `osapi-justfiles`' baseline listed
its consumers from the frame of the six components and missed `specs`, which its
own task list caught. Here the single edge was verified from
`nats-client/go.mod` *and* `osapi/go.mod` before it was written down. One edge
is a small test of the habit, and the habit is what matters for
`osapi-orchestrator`, which has more.

## Project Structure

### Documentation (this feature)

```text
components/nats-client/specs/001-nats-client-baseline/
├── spec.md              # 18 requirements, 7 outcomes
├── plan.md              # This file
├── checklists/
│   └── requirements.md
└── tasks.md
```

### What is being inventoried

```text
nats-client/                 # nothing here changes
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

**Structure Decision**: no corpus subject file beyond `spec.md`, and no skill
gains a reference. No skill in the specs repository reaches NATS client
construction; a citation for a reader who does not exist is the rule invented to
fill a template.

## What the verification checks, and what it cannot

The nine commands check the **counts**, and FR-016 exists because two of them
were wrong before they were run. Three things they do not check:

- **Whether the 25 methods are the right 25.** They are the contract as it
  stands; whether the wrapper should expose more or fewer is a judgement.
- **Whether the leaked upstream types matter to a consumer.** FR-015 records
  that the leak is undocumented; whether it is a problem depends on what a
  future consumer expects.
- **Whether the eight documentation pages are accurate.** They are cited as the
  place a method's behaviour is described, not verified against the code. A page
  that has drifted from its method would not show up here, and that is the gap
  class osapi's baseline found three of.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
