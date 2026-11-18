# The job system

osapi queues work for a managed host. It does not call the host. The controller
runs nothing itself. It writes a job, announces it and waits. An agent takes the
job, runs a provider, and writes a response back.

All of the difficult parts of the system come from that split:

- at-least-once delivery
- the idempotency that the providers must have
- two independent timeouts
- a result for each host, not one answer

```
REST API → job client → NATS → agent → provider
                ↓                  ↓
            job-queue         job-responses
```

## A job is stored before it is announced

The definition goes to the `job-queue` bucket under `jobs.{job-id}` first. Only
after that does a notification go out. **The notification has the identity of
the job, not its content.** An agent that gets one reads the definition. Thus
nothing on the wire must be trusted or kept in sync.

The definition holds the job's ID, its created time, its NATS subject, the
target that the request gave (`_all`, a hostname or a label) and its operation.
The job list and `osapi client job get` show the target from it, not the one
host that answered. With PKI on, the controller writes the definition inside a
signed envelope. Each reader of the definition, the list, the detail and a retry
included, takes the envelope's payload and checks its signature with the
controller's key first. A reader that parsed the envelope as the definition
would find no created time and no operation.

osapi records the status as **events that it only adds**. It does not change a
field. Thus the history of a job stays after the job. Later, a reader can see
that something was queued, started and failed, in that order.

Results go to a **separate bucket**, `job-responses`. Thus a caller that reads a
result does not search the status history of the job for it.
`internal/config/nats.go` declares the two buckets.

## Routing and targeting

An operation goes to a dot-notation subject under one of two prefixes:
`jobs.query` for reads, `jobs.modify` for writes. The split lets a consumer
subscribe to one class of work, and not filter out the other.

**The prefix has a namespace. It is not a literal.** `internal/job/subjects.go`
makes the two from a base that a deployment can change. Thus do not hardcode
`jobs.query`.

A target resolves in four ways.

| Target           | Means                                      |
| ---------------- | ------------------------------------------ |
| a hostname       | that one host                              |
| a machine ID     | that one machine, whatever it calls itself |
| `_all`, `_any`   | a broadcast                                |
| a label selector | every host matching                        |

`job.ExpectedAgentHostnames` decides which agents must answer a broadcast. Thus
a broadcast can report a host that did not answer. It does not return fewer rows
without a signal.

## Delivery is at-least-once, and the agent owes idempotency

The bus can deliver the same job two times. Nothing prevents it. Thus **the
agent checks before it runs the job**. `HasJobResponse` asks if osapi already
recorded a response for that job. If it did, the agent acknowledges the message
and runs nothing again.

Four operations make this important in practice, because nobody can make them
safe to do again:

- `command.exec`
- `command.shell`
- `power.reboot`
- `power.shutdown`

**A job that ran is complete.** The agent acknowledges after it records a
response, for success and for failure. Thus a new delivery does not try a failed
operation again. A failure is a result, not a reason to try again.

### When the response cannot be written

The operation already ran. If the agent does not acknowledge the message, the
bus delivers it again, and the operation runs a second time. That is worse than
the loss of the record. Thus the agent tries to record the failure, and
acknowledges the message in all cases.

### Which failures terminate a message

A malformed payload, a subject that the agent cannot parse, and a failed
signature stop the message immediately. None of them can succeed on a second
try.

A failure to read the job data can be temporary. Thus the agent lets the bus
deliver the message again. `internal/agent/handler.go` makes that decision.

### Consumer defaults

`MaxDeliver` is 5 and `AckWait` is 2m. `cmd/root.go` sets them as
`agent.consumer.max_deliver` and `agent.consumer.ack_wait`, and
`configs/osapi.yaml` ships the same values. A deployment can change the two.

An operation that runs longer than `AckWait` is **not** delivered again during
the work, because the agent extends the deadline while the work runs. The
keepalive in `internal/agent/handler.go` does that.

## Three limits, bounding different things

Operators misunderstand this part most often.

| Clock                        | Default       | Bounds                                                 |
| ---------------------------- | ------------- | ------------------------------------------------------ |
| `controller.api.job_timeout` | `30s`         | how long the controller waits for an answer            |
| the agent's command deadline | per operation | how long the work may run                              |
| `DefaultCommandTimeout`      | `10m`         | the **ceiling** on any command, applied to all of them |

**Know the difference between the first two.** The controller stops its wait a
long time before the work must stop. Thus "timed out" means that the controller
stopped. It does not tell if the operation ran or still runs.

The ten minutes is a maximum, not a fallback. `internal/exec` always wraps the
context of each command in it. Thus a caller can ask for less time, but not for
more. Refer to [running commands](exec.md).

If you cancel the API request, a running operation does not stop. `job delete`
removes the queue entry, not the process. An operation stops for one of three
reasons:

- its own deadline
- the ten-minute maximum
- the agent stops

## What a caller gets back

The result for each host has one of four statuses. The difference between them
is important.

| Status    | Means                                                  |
| --------- | ------------------------------------------------------ |
| `ok`      | it ran and succeeded                                   |
| `failed`  | it ran and did not succeed                             |
| `skipped` | it does not apply to that host's OS family             |
| `timeout` | the controller stopped waiting; unknown whether it ran |

`pkg/sdk/client/status.go` has them. `internal/job/client/client.go` makes the
timeout row. No agent reports it. That is why it cannot tell more.

A failure has a **machine-readable cause** next to its message. Thus a caller
uses the cause to decide, and does not parse prose. A cause that a reader does
not know is still a cause. Show it. Do not hide it.

## Bucket lifetimes

One setting, `nats.kv.ttl`, goes to `job-queue` and to `job-responses`. Thus the
definition, the status events and the response of a job expire together. Only a
setting for each bucket can make them different, and there is none. `bus.JobKV`
and `bus.ResponseKV` in `internal/bus/bus.go` read the same field.

The shipped `osapi.yaml` sets it to one hour. `osapi.dev.yaml` does not set it,
and osapi ignores the parse error. Thus a deployment from that file gets no
expiry, not a default.

```sh
sed -n '/^  kv:/,/^  [a-z]/p' configs/osapi.dev.yaml   # no ttl line
```

`job-queue` has definitions and status events. `job-responses` has results.
`agent-facts` has what an agent collects on its own schedule, not as an answer
to a job.

## One request, end to end

This example sets a sysctl value on twenty hosts. A trace is more useful than a
list of the parts.

1. **The CLI or the SDK** calls the endpoint with `_all` as the hostname, or
   with a label selector.
2. **The handler** validates the input against the OpenAPI specification, and
   gives the work to the job client. It does not touch the operating system, and
   it does not know what a sysctl is.
3. **The job client** writes the definition to `jobs.{job-id}`, then announces
   it. `ExpectedAgentHostnames` decides which agents must answer the broadcast.
   It uses only verified registrations.
4. **Each agent** gets a notification with the identity of the job. It reads the
   definition, and checks `HasJobResponse`. If it answered this job before, it
   acknowledges and stops.
5. **The sysctl provider** runs on the host. It manages its own configuration
   files with a reserved filename prefix. Thus it does not overwrite a file that
   an operator wrote by hand. It validates the key itself. It does not trust the
   validation of the request path.
6. **The result** has the resource, if anything changed, and an error for each
   resource. The agent writes a status event and the result to `job-responses`.
   While the work runs, the keepalive extends the ack deadline.
7. **The controller** collects results for `controller.api.job_timeout` or less,
   30 seconds by default. It returns a collection with one row for each expected
   host.

### Why a row might not say `ok`

`skipped` means that the OS family of the host does not implement sysctl in the
way that this provider does. Thus the provider returned the unsupported result.
On a mixed fleet, this is normal, not a fault.

`failed` means that it ran on that host and did not succeed. The
machine-readable cause next to the message tells why.

`timeout` means that the **controller** stopped its wait. It tells nothing about
the host. The work can be complete. It can still run under the 10-minute
maximum. It can also not have started. A cancel of the request does not stop it.

**A missing row** is easy to miss. Nineteen rows for twenty machines means that
an agent was not in the expected set, because its registration is not verified.
That is not a timeout, because nothing expected it. Refer to
[agent identity](agent-identity.md).

## Where this connects

[Providers](providers.md) tells what a provider must return, and what makes an
operation idempotent.

[Agent identity](agent-identity.md) tells about response signatures, and how the
controller knows that an answer came from the agent that it addressed.

[Building a domain](domains.md) tells how to add an operation to a domain, and
which of the four job-client methods to call.

______________________________________________________________________

Written from `internal/job/`, `internal/agent/` and `cmd/root.go`.
