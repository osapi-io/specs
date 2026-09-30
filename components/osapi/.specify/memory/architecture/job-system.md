# The job system

Work reaches a managed host by being queued, not by being called. The controller
does not run anything itself. It writes a job, announces it, and waits; an agent
picks the job up, runs a provider, and writes a response back.

That indirection is the whole reason the API cannot simply do the work, and
almost everything below follows from it.

```
REST API → job client → NATS → agent → provider
                ↓                  ↓
            job-queue         job-responses
```

## A job is stored before it is announced

The definition goes to the `job-queue` bucket under `jobs.{job-id}` first. Only
then does a notification go out, and **the notification carries the job's
identity rather than its content**. An agent that receives one fetches the
definition, so nothing on the wire has to be trusted or kept in sync.

Status is recorded as **append-only events** rather than by mutating a field, so
a job's history survives the job. A reader can see that something was queued,
started and failed, in that order, after the fact.

Results go to a **separate bucket**, `job-responses`, so a caller reading a
result does not walk the job's status history looking for it. Both buckets are
declared in `internal/config/nats.go`.

## Routing and targeting

An operation routes by dot-notation subject under one of two prefixes:
`jobs.query` for reads, `jobs.modify` for writes. The split exists so a consumer
can subscribe to one class of work without filtering out the other.

**The prefix is namespaced, not literal.** `internal/job/subjects.go` builds both
from a base a deployment can change, so `jobs.query` names a shape rather than a
string.

A target resolves four ways.

| Target          | Means                                     |
| --------------- | ----------------------------------------- |
| a hostname      | that one host                             |
| a machine ID    | that one machine, whatever it calls itself |
| `_all`, `_any`  | a broadcast                               |
| a label selector | every host matching                      |

`job.ExpectedAgentHostnames` decides which agents a broadcast expects to hear
from, which is what lets a broadcast report a host that never answered rather
than silently returning fewer rows.

## Delivery is at-least-once, and the agent owes idempotency

The bus will deliver the same job twice. Nothing prevents it, so **the agent
checks before executing**: `HasJobResponse` asks whether a response has already
been recorded for that job, and if one has, the agent acknowledges without
running anything again.

Four operations make that load-bearing rather than theoretical, because they
cannot be made safe to repeat:

- `command.exec`
- `command.shell`
- `power.reboot`
- `power.shutdown`

**A job that has run is terminal.** The agent acknowledges after recording a
response, success or failure alike, so a failed operation is not retried by
redelivery. Failure is an outcome, not a reason to try again.

### When the response cannot be written

The operation already ran. Leaving the message unacknowledged would redeliver it
and run the operation a second time, which is worse than losing the record. So
the failure is recorded best-effort and the message is acknowledged anyway.

### Which failures terminate a message

A malformed payload, an unparsable subject and a failed signature all terminate
immediately, because none of them can succeed on a retry.

A failure to read the job data itself is treated as possibly transient and left
to redeliver. `internal/agent/handler.go` draws that line.

### Consumer defaults

`MaxDeliver` 5 and `AckWait` 2m, set in `cmd/root.go` as
`agent.consumer.max_deliver` and `agent.consumer.ack_wait`, and shipped with the
same values in `configs/osapi.yaml`. A deployment may override both.

An operation that outlives `AckWait` is **not** redelivered mid-flight, because
the agent extends the deadline while the work runs. The keepalive in
`internal/agent/handler.go` does that.

## Two clocks, bounding different things

This is the part an operator misreads most often.

| Clock                        | Default | Bounds                                    |
| ---------------------------- | ------- | ----------------------------------------- |
| `controller.api.job_timeout` | `30s`   | how long the controller waits for an answer |
| the agent's command deadline | per operation | how long the work may run             |
| `DefaultCommandTimeout`      | `10m`   | the backstop for a command with no deadline |

**The gap between the first two is the point.** The controller stops waiting long
before the work has to stop. So "timed out" means the controller gave up, and
says nothing about whether the operation ran or is still running.

Cancelling the originating API request does not stop a running operation, and
`job delete` removes the queue entry rather than the process. An operation stops
for one of three reasons: its own deadline, the backstop, or the agent shutting
down.

## What a caller gets back

A per-host result carries one of four statuses, and the difference between them
matters.

| Status    | Means                                              |
| --------- | -------------------------------------------------- |
| `ok`      | it ran and succeeded                               |
| `failed`  | it ran and did not succeed                         |
| `skipped` | it does not apply to that host's OS family         |
| `timeout` | the controller stopped waiting; unknown whether it ran |

`pkg/sdk/client/status.go` holds them, and the timeout row is synthesised by
`internal/job/client/client.go` rather than reported by an agent, which is why it
cannot say more.

A failure carries a **machine-readable cause** beside its message, so a caller
branches on the cause rather than parsing prose. A cause a reader does not
recognise is still a cause and should be surfaced rather than swallowed.

## Bucket lifetimes

TTLs are configured per bucket rather than per status, so a job's definition, its
status events and its response do not age out independently of each other.
`job-queue` holds definitions and status events, `job-responses` holds results,
and `agent-facts` holds what an agent gathers on its own schedule rather than in
answer to a job.

## Where this connects

What a provider must return, and what makes an operation idempotent, is
[providers](providers.md).

Response signing and how the controller knows an answer came from the agent it
addressed is [agent identity](agent-identity.md).

Adding an operation to a domain, including which of the four job-client methods
to call, is [building a domain](domains.md).

______________________________________________________________________

Traced to `specs/004-job-system/`, which moved this off the published site and
found three places where that page disagreed with the code: it described the
status-event key shape as though it were the job key, and it gave `MaxDeliver: 3`
and `AckWait: 30s` against actual defaults of 5 and 2m.
