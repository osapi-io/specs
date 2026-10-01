# The job system

Work reaches a managed host by being queued, not by being called. The controller
does not run anything itself. It writes a job, announces it, and waits; an agent
picks the job up, runs a provider, and writes a response back.

Everything awkward about the system comes out of that split: at-least-once
delivery, the idempotency the providers owe, two independent timeouts, and a
per-host result instead of one answer.

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

**The prefix is namespaced, not literal.** `internal/job/subjects.go` builds
both from a base a deployment can change, so do not hardcode `jobs.query`.

A target resolves four ways.

| Target           | Means                                      |
| ---------------- | ------------------------------------------ |
| a hostname       | that one host                              |
| a machine ID     | that one machine, whatever it calls itself |
| `_all`, `_any`   | a broadcast                                |
| a label selector | every host matching                        |

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

## Three limits, bounding different things

This is the part an operator misreads most often.

| Clock                        | Default       | Bounds                                                 |
| ---------------------------- | ------------- | ------------------------------------------------------ |
| `controller.api.job_timeout` | `30s`         | how long the controller waits for an answer            |
| the agent's command deadline | per operation | how long the work may run                              |
| `DefaultCommandTimeout`      | `10m`         | the **ceiling** on any command, applied to all of them |

**Mind the gap between the first two.** The controller stops waiting long before
the work has to stop. So "timed out" means the controller gave up, and says
nothing about whether the operation ran or is still running.

The ten minutes is a ceiling rather than a fallback. `internal/exec` wraps every
command's context in it unconditionally, so a caller can ask for less and cannot
ask for more. See [running commands](exec.md).

Cancelling the originating API request does not stop a running operation, and
`job delete` removes the queue entry rather than the process. An operation stops
for one of three reasons: its own deadline, the ten-minute ceiling, or the agent
shutting down.

## What a caller gets back

A per-host result carries one of four statuses, and the difference between them
matters.

| Status    | Means                                                  |
| --------- | ------------------------------------------------------ |
| `ok`      | it ran and succeeded                                   |
| `failed`  | it ran and did not succeed                             |
| `skipped` | it does not apply to that host's OS family             |
| `timeout` | the controller stopped waiting; unknown whether it ran |

`pkg/sdk/client/status.go` holds them, and the timeout row is synthesised by
`internal/job/client/client.go` rather than reported by an agent, which is why
it cannot say more.

A failure carries a **machine-readable cause** beside its message, so a caller
branches on the cause rather than parsing prose. A cause a reader does not
recognise is still a cause and should be surfaced rather than swallowed.

## Bucket lifetimes

One setting, `nats.kv.ttl`, is passed to both `job-queue` and `job-responses`,
so a job's definition, its status events and its response age out together.
Per-bucket configuration is what would let them diverge, and there is none:
`BuildJobKVConfig` and `BuildResponseKVConfig` in `internal/cli/nats.go` read
the same field.

The shipped `osapi.yaml` sets it to one hour. `osapi.dev.yaml` omits it, and the
parse error is discarded, so a deployment from that file gets no expiry at all
rather than a default.

```sh
sed -n '/^  kv:/,/^  [a-z]/p' configs/osapi.dev.yaml   # no ttl line
```

`job-queue` holds definitions and status events, `job-responses` holds results,
and `agent-facts` holds what an agent gathers on its own schedule rather than in
answer to a job.

## One request, end to end

Setting a sysctl value on twenty hosts, because a trace is worth more than the
parts listed separately.

1. **CLI or SDK** calls the endpoint with `_all` as the hostname, or a label
   selector.
2. **The handler** validates the input against the OpenAPI specification and
   delegates. It does not touch the operating system, and it does not know what
   a sysctl is.
3. **The job client** writes the definition to `jobs.{job-id}`, then announces
   it. `ExpectedAgentHostnames` fixes which agents the broadcast expects an
   answer from, built only from verified registrations.
4. **Each agent** receives a notification carrying the job's identity, fetches
   the definition, and checks `HasJobResponse`. If it has answered this job
   before it acknowledges and stops.
5. **The sysctl provider** runs on the host. It manages its own configuration
   files with a reserved filename prefix, so it will not clobber something an
   operator wrote by hand, and it validates the key itself rather than trusting
   that the request path did.
6. **The result** carries the resource, whether anything changed, and a
   per-resource error. The agent writes an append-only status event and the
   result to `job-responses`, extending the ack deadline by keepalive while the
   work runs.
7. **The controller** collects for up to `controller.api.job_timeout`, 30
   seconds by default, and returns a collection with one row per expected host.

### Why a row might not say `ok`

`skipped` means the host's OS family does not implement sysctl the way this
provider does, so the provider returned the unsupported outcome. On a mixed
fleet this is normal rather than a fault.

`failed` means it ran on that host and did not succeed. The machine-readable
cause beside the message says why.

`timeout` means the **controller** stopped waiting. It says nothing about the
host: the work may be finished, may still be running under the 10-minute
ceiling, or may never have started. Cancelling the request would not have
stopped it.

**A missing row** is the one that is easy to overlook. Nineteen rows for twenty
machines means an agent was not in the expected set, because its registration is
not verified. That is not a timeout, because nothing was waiting for it. See
[agent identity](agent-identity.md).

## Where this connects

What a provider must return, and what makes an operation idempotent, is
[providers](providers.md).

Response signing and how the controller knows an answer came from the agent it
addressed is [agent identity](agent-identity.md).

Adding an operation to a domain, including which of the four job-client methods
to call, is [building a domain](domains.md).

______________________________________________________________________

Written from `internal/job/`, `internal/agent/` and `cmd/root.go`. History:
`../../history/osapi-004-job-system/`.
