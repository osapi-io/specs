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
host that answered. A job stored before targets were kept has none, and the API
gives the host that answered. A token with a target scope sees only the jobs
whose stored target is in its scope. Thus a list for a scoped token reads the
definition of each job before it counts and pages them, and an unscoped list
reads only its page. [Permissions](permissions.md#a-tokens-target-scope) has the
rule. The answer of `GET /api/job/{id}` has the responses and the agent states
as lists sorted by hostname, each with its hostname, and the operation as its
`type` and its `data`. The controller writes the definition inside a signed
envelope. Each reader of the definition, the list, the detail and a retry
included, takes the envelope's payload and checks its signature with the
controller's key first. A reader that parsed the envelope as the definition
would find no created time and no operation.

### A secret in the definition is sealed

Built in osapi-io/osapi#1247. The job client seals each `secret.Value` of the
data before it stores the definition (`request` in `internal/job/client`,
`internal/secret/seal`):

1. It makes a new random 256-bit job key, and encrypts each secret value that is
   not empty with it, with AES-256-GCM and a new random nonce. The job ID is the
   additional data, so a value that somebody copies to a different job does not
   open. The data has each value as the string `sealed:<base64>`, in the field
   of the value. Thus the data has the same shape, and `secret.Value` reads it
   as a string.
2. It makes a new P-256 key for the job, and seals the job key to the P-256 key
   of each agent that the target can reach. The key-encryption key is
   HKDF-SHA256 of the ECDH secret, and AES-256-GCM encrypts the job key with it.
   `job.Recipients` gives the agents: each agent that takes jobs for `_all`,
   `_any` or a label, and the agent of one host. The admission store gives the
   P-256 key of each agent. An agent with no key gets no sealed key.
3. The operation has `sealed_keys`, a map from machine ID to the sealed job key,
   and `sealed_from`, the public P-256 key that sealed them. The signed envelope
   covers them, so an agent knows that the controller sealed the job.

The job key is the only part that has one copy for each agent. Thus a large
value goes in the job one time, also to `_all`. JetStream, the job KV and the
audit log never see the value.

Each algorithm is a FIPS 140-3 approved algorithm from the Go standard library,
and the seal has one construction (osapi-io/osapi#1382). The osapi docs page of
secrets has the wire format. Each GCM nonce is random, from
`cipher.NewGCMWithRandomNonce`, because FIPS 140-3 only mode refuses a nonce
that the caller selects.

The agent opens its own job key with its P-256 key when it takes the job
(`openJob` in `internal/agent`). The dispatch of a behavior decodes the input
into the type of the method, opens each `secret.Value` with `secret.Map`, and
gives the provider the input. The values live only in that call. A job with no
key for the agent fails with `seal.ErrNotSealedToAgent`, "the job was not sealed
to this agent", and does not run. Such an agent joined after the controller
queued the job, or has no P-256 key. A retry keeps the sealed keys of the job,
so it reaches only the same agents.

PKI is always on (osapi-io/osapi#1307), so the controller has the P-256 key of
each admitted agent. A job client with no agent keys, such as the one of an
agent, refuses a job with a secret with `client.ErrNoAgentKeys`. Thus no secret
goes in a job as plain text.

osapi records the status as **events that it only adds**. It does not change a
field. Thus the history of a job stays after the job. Later, a reader can see
that something was queued, started and failed, in that order.

`internal/config/nats.go` declares a **separate bucket** for results,
`job-responses`. The agent does not write to it: `WriteJobResponse` puts each
result in `job-queue` under `responses.{job-id}.{host}.{time}`. Thus
`job-responses` stays empty, and its TTL limits nothing. osapi-io/osapi#1095
decides whether to remove the bucket or to write the results to it.

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

`MaxDeliver` is 5 and `AckWait` is 2m. `agent start` declares them as the
defaults of `agent.consumer.max_deliver` and `agent.consumer.ack_wait`, in
`internal/cli/commands/agentcmd/defaults.go`. A deployment can change the two.

An operation that runs longer than `AckWait` is **not** delivered again during
the work, because the agent extends the deadline while the work runs. The
keepalive in `internal/agent/handler.go` does that.

### An idle consumer goes away

Each consumer of an agent is durable, and its name has the machine ID of the
agent: `query_direct_<id>`, `modify_label_group_web_<id>`. An agent has six or
more. `agent.consumer.inactive_threshold` sets the `InactiveThreshold` of each,
24h by default. NATS removes a consumer that has no fetch for that time. An
agent that starts again in that time continues with the same consumers.

Before osapi-io/osapi#1154 the consumers had no threshold. Thus a host that got
a new machine ID, such as a rebuilt VM, kept its old consumers in `osapi-JOBS`.
In the lab, 125 old machine IDs filled the limit of 1000 consumers, and no agent
could make its consumers.

The agent makes each consumer with `CreateOrUpdate` each time it starts. Thus a
consumer that had no threshold gets it at the next start of its agent. An old
consumer whose agent does not start again has no threshold. It stays until a
person removes it.

**A new consumer gets only the jobs that come after it.** The agent makes each
consumer with `DeliverNew`. Thus a new host, a new machine ID or a new label
does not run the jobs that the stream kept from before the consumer existed. A
durable consumer keeps its position. Thus an agent that starts again with the
same consumers gets the jobs that came while it was away. A start time on the
agent cannot do that, so the deliver policy is the start point
(osapi-io/osapi#1169).

**Keep the threshold at or above `nats.stream.max_age`.** Then the consumer of
an agent that is away stays while the stream keeps a job for it. A consumer that
NATS removed is made again with `DeliverNew`, and the agent does not get the
jobs that came while it was away.

NATS does not change the deliver policy of a consumer that exists. When
`CreateOrUpdateConsumer` fails, the job client looks at the consumer that
exists. If its deliver policy is different, such as a consumer that an earlier
build made with `DeliverAll`, the client removes the consumer, makes it again
and logs a warning. Thus an upgraded agent gets its consumers with no person.

A drained agent does not fetch. Thus a drain that is longer than the threshold
removes the consumers of the agent, and the undrain makes them again.

### An agent without its consumers

When the agent cannot make or bind a consumer, for example when the stream has
its maximum number of consumers, it logs the error, reports the
`ConsumersUnavailable` condition, and tries again each 10 seconds. The reason of
the condition gives the number of consumers that do not run and the error of one
of them. The condition clears when each consumer runs, or when a drain stops
them. `startConsumer` in `internal/agent/consumer.go` does this.

The scheduling state stays `Ready`. The state is the drain state that an
operator sets, and the controller reads it to decide which agents must answer a
broadcast. The condition is the signal that the agent is not ready. A broadcast
still waits for the agent and shows a `timeout` row when it does not answer, so
the result does not lose the host without a signal. Before osapi-io/osapi#1154
the agent logged the error and reported nothing, and each job failed with
`500 the job could not be sent`.

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

`osapi nats setup`, or the server that osapi runs, sets the TTL of the buckets
from the config of the server. A connection of the agent or the controller does
not change it (osapi-io/osapi#1096). Thus the TTL of the server decides how long
a job stays.

The default is one hour, from `nats start`. Until osapi-io/osapi#1387 only the
shipped `osapi.yaml` set it. A file without the key, such as `osapi.dev.yaml`,
got no expiry.

```sh
osapi config get --key nats.kv.ttl   # 1h, source default
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

[Behaviors](behaviors.md#how-a-behavior-is-served) tells how the generated
handler of a method queues its job, on one host or on each host of the target.

______________________________________________________________________

Written from `internal/job/`, `internal/agent/` and `cmd/root.go`.
