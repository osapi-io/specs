# Data Model: One shape for every component baseline

**Feature**: `002-baseline-shape` | **Date**: 2026-09-29

Phase 1. This feature's entities are the units of work it obliges and the two
artifacts it produces itself. What each unit must contain is fixed here so that
nine features written by whoever picks them up produce the same document.

## What this feature writes

| Artifact          | Path                                                      | Contents                                                         |
| ----------------- | --------------------------------------------------------- | ---------------------------------------------------------------- |
| The fragment      | `.charter/fragments/global/baseline.md`                   | 14 lines, wording fixed in [research.md](research.md) Decision 1 |
| Its registration  | `.charter/manifest.yml`                                   | one entry, so composition picks it up                            |
| The map           | `system/.specify/memory/plan.md`, `## The Repository Map` | the graph, with the commands that produce it                     |
| Six constitutions | `components/*/.specify/memory/constitution.md`            | recomposed, not hand-edited                                      |

Nothing else. The baselines are other features' work — FR-016.

## The map, as it stands today

Measured 2026-09-29. It will change, which is why FR-002 makes each baseline
state its own edges and why the map carries its commands rather than only its
conclusions.

| Repository           | Depends on                   | Depended on by       | What it is                                           |
| -------------------- | ---------------------------- | -------------------- | ---------------------------------------------------- |
| `osapi`              | `nats-client`, `nats-server` | `osapi-orchestrator` | The API and the agent: manages Linux hosts over NATS |
| `osapi-orchestrator` | `osapi`                      | —                    | Drives osapi's SDK to run ordered work across hosts  |
| `nats-client`        | —                            | `osapi`              | NATS client wrapper                                  |
| `nats-server`        | —                            | `osapi`              | Embedded NATS server                                 |
| `gohai`              | —                            | —                    | SDK-first system fact collection, standalone         |
| `osapi-justfiles`    | —                            | all six, by fetch    | Shared justfile modules                              |

Commands: `grep -oE "osapi-io/[a-z-]+" */go.mod` for the Go edges, and
`grep -n justfiles */justfile` for the build edge. The build edge is one every
repository has and no `go.mod` records, which is why it is listed separately
rather than left to the Go graph.

**One finding the map surfaces**: `osapi-justfiles` is fetched from
`refs/heads/main` — unpinned — by all six. `global/tooling` says a tool whose
output is committed is pinned. Recorded as FR-024's sibling; owned by those
repositories, not by this feature.

## The eleven units

### Unit 1 — this feature

Produces the four artifacts above. Merges before anything else starts, because
the shape is what the rest is written against.

### Unit 2 — `osapi`'s baseline

The largest, and first by FR-029. A new feature under `components/osapi/specs/`.

What makes it unusual: **osapi already has 1,840 lines of memory**, from five
archived features. The baseline does not restate any of it. Its job is the frame
that memory lacks — sections 1, 2 and 3 — and to classify the 221 documentation
pages that remain after the backfill.

| Section         | For osapi                                                                                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 What it is    | The API and the agent; hosts managed over NATS; who calls it                                                                                                         |
| 2 Where it sits | Below: `nats-client`, `nats-server`. Above: `osapi-orchestrator`. What breaks each way                                                                               |
| 3 Architecture  | Controller, agent, job system, providers, SDK, CLI — what each is for and what passes between them, citing but not restating `#### The job system` already in memory |
| 4 The contract  | Cites the provider contract, the agent key store, the job system, building a domain — all already in memory                                                          |
| 5 Measurements  | 2,739 Go files, 221 doc pages, and the rest, each with its command                                                                                                   |
| 6 Gaps          | Whatever reading the code against the remaining site pages turns up                                                                                                  |
| 7 Excludes      | Everything the five archived features already state, by citation                                                                                                     |

Section 4 is mostly citation, which is correct: osapi's contract *is* already
stated. A baseline that restated it would be the second statement the whole
exercise forbids.

### Unit 3 — `gohai`'s baseline amendment

Adds sections 2 and 3 and the classification of 68 pages. An amendment to a
merged and archived feature, so its own pull request. [research.md](research.md)
Decision 4 gives the contents.

### Units 4, 6, 8, 10 — the four moves

One per repository with contributor documentation still in place. Each is driven
by its baseline's classification and leaves every address resolving.

| Unit | Repository           | Pages to classify | Known to stay                                       |
| ---- | -------------------- | ----------------- | --------------------------------------------------- |
| 4    | `gohai`              | 68                | `docs/collectors/` — a consumer's catalogue, FR-028 |
| 6    | `osapi-orchestrator` | 140               | to be decided by its baseline                       |
| 8    | `nats-client`        | 8                 | to be decided by its baseline                       |
| 10   | `nats-server`        | 5                 | to be decided by its baseline                       |

### Units 5, 7, 9, 11 — the four remaining baselines

`osapi-orchestrator`, `nats-client`, `nats-server`, `osapi-justfiles`. Written
under the fragment rather than under advice, because unit 1 and unit 2 precede
them.

`osapi-justfiles` is the one that tests FR-011 and FR-013: no Go, no doc pages,
so its contract section states recipe names and their behaviour, and its
measurements count modules rather than files. If the shape cannot be filled
there, the shape is wrong.

## Entities

- **Unit of work**: one feature or one amendment, in one project. Eleven of
  them.
- **Baseline**: the seven-section inventory of one repository. Six exist when
  the programme finishes, one of them by amendment.
- **Move**: the relocation of a repository's contributor documentation into the
  corpus, driven by its baseline's classification. Four of them.
- **Classification**: the per-page verdict — user-facing or contributor-facing —
  that a baseline records and a move obeys. 221 pages across five repositories.
- **Edge**: a dependency between two repositories, stated by both baselines and
  held once in the map.
