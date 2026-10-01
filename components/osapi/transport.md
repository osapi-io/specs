# The message bus

Everything in osapi that is not a single HTTP request goes over NATS. The queue
the [job system](job-system.md) describes, the registration and facts an
[agent's identity](agent-identity.md) rests on, and the [audit trail](audit.md)
are all subjects and buckets on one bus.

**osapi runs the bus itself.** `cmd/nats_setup.go`'s `setupNATSServer` starts a
NATS server as a goroutine in the controller's own process, through
[nats-server](../nats-server/README.md), and then talks to it through
[nats-client](../nats-client/README.md). The two wrappers are separate
repositories and neither knows the other exists; osapi is where they meet.

So there is no broker to install and no broker to operate, and the cost is that
the bus lives and dies with the process holding it. `setupNATSServer` calls
`LogFatal` if the server does not start or JetStream cannot be configured, so a
controller that cannot raise a bus does not come up degraded.

It is also startable on its own: `osapi nats server start` runs the same
function without a controller, which is how a deployment separates the bus from
the API.

## What lives on it

| Name             | Kind         | Holds                                            |
| ---------------- | ------------ | ------------------------------------------------ |
| `JOBS`           | stream       | the job notifications an agent consumes          |
| `job-queue`      | KV bucket    | job definitions and their status events          |
| `job-responses`  | KV bucket    | the signed result an agent writes back           |
| `agent-registry` | KV bucket    | registrations, the only thing targeting resolves |
| `agent-facts`    | KV bucket    | what an agent gathers on its own schedule        |
| `agent-state`    | KV bucket    | drain flags and timeline events                  |
| `file-objects`   | object store | file bodies too large for a KV value             |
| `AUDIT`          | stream       | the audit entries                                |

Two buckets rather than one for a job's life is deliberate: a definition is
written by the controller and read by an agent, a response is written by the
agent and read by the controller, and separating them means neither side writes
where the other writes. Their TTL does not separate, which
[the job system](job-system.md) explains.

## Two osapi deployments can share one server

Nothing about the names above is fixed. `job.Init` in `internal/job/subjects.go`
takes a namespace: empty leaves the default `jobs.query` and `jobs.modify`, and
a value prepends itself, so `osapi` gives `osapi.jobs.query`.

```go
Init("")      // jobs.query, jobs.modify
Init("osapi") // osapi.jobs.query, osapi.jobs.modify
```

Bucket and stream names take the same namespace a different way.
`ApplyNamespaceToInfraName` joins with a hyphen rather than a dot, because a KV
bucket name cannot contain one, so the namespace `osapi` turns `job-queue` into
`osapi-job-queue`.

Two mechanisms for one setting is the thing to notice. A subject is
dot-separated and a bucket name cannot be, so the same configured namespace
appears in two shapes, and anybody adding a third kind of NATS object has to
pick which.

## Nothing on the bus is trusted because it arrived

A job and a response both travel as a `SignedEnvelope`, in
`internal/job/types.go`, carrying an Ed25519 signature over the payload. An
agent verifies before acting and the controller verifies before recording.

Publish access to NATS gets a message onto a subject and does not get it run,
which is why [agent identity](agent-identity.md) can say a key is changed only
by enrollment and mean it.

## What osapi cannot control from here

Three things are settled inside the two wrapper repositories, and a consumer of
either cannot reach them. They are recorded here because this is where somebody
debugging the bus will look, and because osapi is the only consumer either
wrapper has.

**Trace logging is on and cannot be turned off.** `nats-server`'s `Start()`
calls `SetLogger(wrapper, true, true)` with both literals, so every embedded
server runs with debug and trace logging enabled. Nothing in osapi's
configuration reaches it.

**Startup logging does not arrive in osapi's logger.** The same `Start()`
attaches the logger after the server is already accepting connections, so
anything the server logs while coming up goes to NATS's own default logger. A
controller whose bus never became ready leaves no trace of why in the handler
osapi passed in.

**osapi is never told the connection dropped.** `nats-client` sets no
reconnection options and registers no disconnect, reconnect or closed handler,
and osapi passes only host, port, auth and a name. The upstream library's
default reconnection still applies, so a short outage recovers on its own; what
is absent is any notification, so osapi cannot log a drop, cannot report one on
`/health`, and cannot tell a slow request from a bus that went away and came
back.

Changing any of the three needs a change in the wrapper, not here.

## Where this connects

[The job system](job-system.md) is what the bus carries and why at-least-once
delivery shapes everything downstream. [Agent identity](agent-identity.md) is
what the signatures protect. [Configuration](configuration.md) is where the
namespace, the bucket names and the auth mode come from.

______________________________________________________________________

Written from `cmd/nats_setup.go`, `internal/job/subjects.go`,
`internal/job/config.go`, `internal/job/types.go` and `internal/cli/nats.go`.
