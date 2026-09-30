# Implementation Plan: A baseline for nats-server

**Branch**: `001-nats-server-baseline` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/nats-server/specs/001-nats-server-baseline/spec.md`

## Summary

State what `nats-server` is, so its memory stops holding only a constitution.
Nineteen requirements, every one of the form "the corpus MUST state X".

Unit 8 of twelve, and the smallest repository with Go code in the organization —
twelve files, four of them the package. **The smallness is why it is worth
reading closely rather than a reason to hurry.** A wrapper this thin either
saves a consumer the four lines it wraps or makes decisions on their behalf, and
the difference is invisible from the signatures. Reading `Start()` found three
decisions the consumer cannot change and no page mentions.

**Nothing lands in the `nats-server` repository.** The deliverable is the
inventory.

## Technical Context

**Language/Version**: Markdown. The repository being inventoried is Go — 12
files, 10 of them not tests, `go 1.26.0` — and nothing in it changes.

**Primary Dependencies**: None. The corpus depends on nothing at runtime. The
repository being inventoried depends on no other repository in the organization.

**Storage**: `components/nats-server/specs/` for the specification — a directory
this feature creates, since it is the project's first — and
`components/nats-server/.specify/memory/` for what archival consolidates into.

**Testing**: `just test` in the specs repository. There is no code to unit test.
Every count carries its command, and ten commands re-run is what checks the
counts — but **the three findings that matter here are not counts**, and no
command would have produced them.

**Target Platform**: The corpus.

**Project Type**: Documentation.

**Constraints**: No change to the `nats-server` repository. No count without its
command. Section names verbatim from 002. Gaps recorded with what was measured,
where, and an owner.

**Scale/Scope**: One repository inventoried, the smallest with Go code. A
contract of one constructor, two methods, and an embedded upstream option struct
that is most of the surface.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Documentation** | The five pages are cited rather than copied, and the upstream option struct is deliberately not restated — it is upstream's to change.                                                                 |
| **Verification**  | Ten counts with commands. More importantly, the three gaps came from **reading `Start()`**, which is the case where "a claim about the codebase is measured" means reading order rather than counting. |
| **Tooling**       | Nothing provisioned.                                                                                                                                                                                   |
| **Correction**    | Three gaps with owners, none corrected here. Each implies a change this repository must make, and naming the change is not making it.                                                                  |
| **Workflow**      | Stages 1 to 4 in one branch, as CONTRIBUTING's lifecycle table specifies.                                                                                                                              |
| **Baseline**      | This memory holds no decisions, so the baseline is the whole of it.                                                                                                                                    |
| **Repositories**  | The single edge is verified from both ends.                                                                                                                                                            |
| **Tracking**      | Nothing becomes an issue. The three gaps name their owner.                                                                                                                                             |

**Result**: no violations.

## Why reading order was the method here

Every baseline before this one was mostly counting: files, pages, recipes,
methods. This one counts too, and the counting found nothing interesting — ten
figures, all unremarkable, all reproducing first time.

**The three findings came from reading four statements in sequence.** `Start()`
constructs the upstream server, starts it in a goroutine, waits for readiness,
and *then* attaches the logger. Each statement is unobjectionable; the order is
what produces a consumer whose logger never sees the startup it was attached to
observe. No count reveals an order, and no signature does either —
`Start() error` says nothing about when the logger arrives.

The same reading found `SetLogger(wrapper, true, true)`, where the interesting
part is the two literals, and the absence of any defaulting in `New()`, where
the interesting part is what is *not* there.

This is what `global/verification`'s "reading code and concluding is a
hypothesis" looks like from the other side: the hypothesis was that a thin
wrapper decides nothing, and reading it falsified that. The counts could not
have.

## What the five documentation pages did not say

Worth recording because it bears on how much weight a page carries. The
repository documents `configuration.md`, `lifecycle.md` and `logging.md` — the
three subjects the three gaps fall under — and **none of the three facts appears
in any of them.** A reader who trusted the prose would believe logging was
configurable, that startup was observable, and that `Options` had sensible
defaults.

That is not a criticism of the pages; each describes what it describes
correctly. It is the argument for FR-090's discipline in osapi's corpus — prose
is a lead and the code is the source — holding even where the prose is recent
and the repository is small.

## Project Structure

### Documentation (this feature)

```text
components/nats-server/specs/001-nats-server-baseline/
├── spec.md              # 19 requirements, 7 outcomes
├── plan.md              # This file
├── checklists/
│   └── requirements.md
└── tasks.md
```

### What is being inventoried

```text
nats-server/                    # nothing here changes
├── pkg/server/                 # the one package: 4 non-test files
│   ├── server.go               #   lifecycle, and the order Start() uses
│   ├── types.go                #   Options: upstream's struct, plus ReadyTimeout
│   ├── server_wrapper.go       #   NATSServerInstance, the only seam
│   ├── logger.go               #   SlogWrapper: NATS logging into slog
│   └── mocks/                  #   generated; not the contract
├── examples/                   # 4 runnable, all setting ReadyTimeout explicitly
└── docs/                       # 5 pages; three facts are in none of them
```

**Structure Decision**: no corpus subject file beyond `spec.md`, and no skill
gains a reference. No skill in the specs repository starts an embedded NATS
server.

## What the verification checks, and what it cannot

The ten commands check the counts, and the counts were never in doubt. What the
task list cannot automate is the part that found everything:

- **Reading `Start()` in order.** T007 is a reading rather than a command,
  because the finding is a sequence.
- **Whether the three gaps matter to a consumer.** Debug and trace being
  unconditional is a fact; whether it is a problem depends on what a consumer
  embeds this in. osapi does, and osapi's baseline does not mention it either.
- **Whether the five pages are accurate about what they do cover.** They were
  read for what they omit, not verified line by line against the code.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
