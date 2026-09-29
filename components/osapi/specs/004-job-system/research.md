# Research: The job system

**Feature**: `004-job-system` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

The specification is already the output of this phase for the parts that needed
code reading: 24 requirements, each citing a file, three of them recording a gap
between what the page said and what the code does. This records what remains —
the decisions the writing left open — rather than repeating the specification.

## Decision 1: the corrections land in both places, in the osapi change

Three of the page's statements were wrong (spec FR-004, FR-014, FR-021). The
corpus now states the right values and records the wrong ones. The question this
leaves is what the *page* says afterwards, since the operator half survives.

**Decision**: the surviving page states none of the three. The job key shape and
the consumer settings are contributor knowledge and leave with the rest of the
mechanics; the bucket TTL leaves too, because an operator who needs it reads the
configuration file, which is the statement of record for a configured value
under `global/documentation`.

**Alternative considered**: correcting the numbers in place on the page and
leaving them there. Rejected — that keeps two statements of each, which is what
the subject moved to end, and the page's version has already drifted once.

## Decision 2: which skill reference changes, and how far

`.claude/skills/add-a-domain/references/agent.md` covers "processor, registry
registration, platform selection, delivery semantics". The last of those is what
`004` now states.

**Decision**: the delivery-semantics section becomes a citation table naming
FR-009 through FR-015. The processor, registration and platform-selection
material stays as it is: it is how to wire a domain into the agent, not how the
job system behaves, and `005` is where it goes if it goes anywhere.

**Alternative considered**: rewriting the whole reference now. Rejected — it
mixes two subjects in one change, and the part that belongs to `005` has not
been specified yet.

## Decision 3: how much of the page moves

Roughly 430 of 630 lines. The split is recorded line by line in
[003's data-model](../003-corpus-backfill/data-model.md) and confirmed against
the live file by 003's T001.

**Decision**: the page keeps the job states as observed, polling, the CLI
command reference, and the metrics worth watching — and gains nothing. A page
that keeps its operator content and loses its mechanics is shorter, not
different in kind.

## What was already verified, and where it is recorded

| Claim                         | Verified against                                                  | Result                                                                                      |
| ----------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Job definition key            | `internal/job/client/client.go`                                   | `jobs.{job-id}`; the page's `{status}.{uuid}` described the status-event keys. Spec FR-004. |
| Status event key              | `internal/job/client/jobs.go`, `agent.go`                         | `status.{job-id}.{state}.{source}.{unix-nano}`. Spec FR-003.                                |
| Consumer settings             | `cmd/root.go`, `configs/osapi.yaml`, `internal/agent/consumer.go` | `MaxDeliver` 5, `AckWait` 2m, not 3 and 30s. Spec FR-014.                                   |
| Bucket TTL                    | `configs/osapi.yaml`                                              | One TTL of `1h` for `job-queue`, not 24h per status. Spec FR-021.                           |
| Subject prefixes              | `internal/job/subjects.go`                                        | `jobs.query` and `jobs.modify`, built from a configurable base. Spec FR-006, FR-007.        |
| Redelivery obligation         | `internal/job/client/types.go`, `internal/agent/handler.go`       | `HasJobResponse` before executing; ack without re-running. Spec FR-009.                     |
| Keepalive                     | `internal/agent/handler.go`                                       | `startInProgressKeepAlive` extends the deadline while an operation runs. Spec FR-015.       |
| Command deadline and backstop | `internal/exec/types.go`                                          | `DefaultCommandTimeout`. Spec FR-016, FR-017.                                               |
| Row statuses and causes       | `pkg/sdk/client/status.go`, `internal/job/errors.go`              | Four statuses; a machine-readable cause beside the message. Spec FR-019, FR-020.            |

## The risk this feature carries

The specification is merged, so the corpus states these rules now. The site
states them too, and until the osapi change lands the duplication is real —
including for the three the page gets wrong, which is the worst version of it: a
reader who finds the page first gets numbers the code has not used for some
time.

[003's research Finding 3](../003-corpus-backfill/research.md) describes this
window in general. For this subject it is not theoretical: it exists as of the
merge of spec.md, and the task list treats the osapi change as the completion of
this feature rather than as follow-up.
