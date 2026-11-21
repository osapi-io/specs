# Observability

`internal/telemetry` has four separate subsystems. Each answers a different
question.

| Subsystem | Answers                                      |
| --------- | -------------------------------------------- |
| `tracing` | where did this request go                    |
| `metrics` | what is the state of this process, over time |
| `process` | is this process healthy right now            |
| `httplog` | what did the HTTP layer see                  |

## Tracing carries across the queue

`InitTracer` configures OpenTelemetry with an OTLP exporter. For development, it
uses a stdout exporter.

Propagation is the important part. `ExtractTraceContext` and
`ExtractTraceContextFromHeader` get a trace context from an incoming request.
Work gets to a host through the queue, not through a call. Thus that context
must go **with the job**, not down a stack. If a trace stops at the API, it
shows a request that queued something, and nothing after it.

### The span tree of a request

Each request that sends a job makes this tree. A broadcast has one `job.process`
for each agent:

```text
osapi-controller  GET /api/...                        otelecho, the root
├─ job.publish                                        kind producer
│  ├─ kv.put                                          the job
│  └─ nats.publish                                    nats-client, producer
│     └─ osapi-agent  nats.process                    nats-client, one for each agent
│        └─ job.process
│           ├─ kv.get, kv.put                         the job, the status, the answer
│           ├─ behavior.<name>.<method>               a behavior only
│           ├─ exec <program>                         each command
│           └─ file.write                             each file that changes
├─ job.collect                                        the wait for the answers
│  └─ kv.watch                                        nats-client
├─ response.encode                                    the answer as JSON
└─ response.write                                     the answer to the client
```

The controller starts the trace, and gives it back in the `traceresponse` header
of each response (W3C Trace Context level 2). The CLI prints the trace ID at the
end of the summary line, after the job ID, and the SDK gives it as
`Response.TraceID()`. Thus the trace flows through the system that the CLI
already talks to. The machine of the CLI needs no access to the tracing backend,
which a company network often does not allow.

A CLI with a tracing exporter opens a span for the command, and the trace starts
there. A CLI without an exporter sends no trace context. If it sent the context
of a span that it never exports, each trace would show a parent that never
arrives.

`job.process` is under `job.publish`, not under the request. The context that
goes with the job is the context of `nats.publish`, a child of `job.publish`,
because that span sent the message. nats-client continues it in `nats.process`
on the agent, and gives the handler that context. `job.collect` is a sibling of
`job.publish`. Thus the time of the request is the time to publish, then the
time to collect, then the time to encode, and the agents are under the publish.

Two spans follow the handler. `response.encode` is the encode of the answer as
JSON, from the moment the handler has its answer to the status line.
`response.write` is the write of the body, from the status line to the last
write, with `http.response.body.size`. For a broadcast to many hosts, the encode
can be a large part of the request: in the lab, 37ms of 75ms for a 148 KB
package list. The write waits on the network, so it is a separate span. The
first version had one span to the last write, and a slow moment of the network
showed as 4.7s of "encode".

The code that oapi-codegen generates encodes after every middleware has
returned, so no middleware can open a span around it.
`internal/telemetry/respspan` times both from three marks instead:
`ScopeMiddleware`, which each domain uses, marks when the handler returns;
echo's `Response.Before` gives the status line, which goes out after the encode;
and `Response.After` gives the last write. The spans are made after the fact,
with those times. A behavior marks before its own `c.JSON`. The first mark wins:
a behavior runs inside `ScopeMiddleware`, which would mark again after the
behavior wrote its answer. A response that osapi writes without the mark, such
as a 401, has no spans, and no span ends before it starts.

A store or a client operation that makes more than one call has its own span,
from `internal/telemetry/opspan`, and its calls are its children. Outside a
trace, such as a metrics refresh or a health probe, `opspan` opens no span, as
nats-client does for a call. The first version opened one, and each refresh of
the health metrics started a trace of its own: on the lab, a `job.summary` or an
`agent.list` root every few seconds. A request that sends no job has one of
these spans instead of `job.publish`:

| Span                                                                | From                            | DETAIL                    |
| ------------------------------------------------------------------- | ------------------------------- | ------------------------- |
| `job.list`                                                          | the job client                  | the count, `2 jobs`       |
| `job.get`, `job.retry`, `job.delete`                                | the job client                  | the job ID                |
| `job.summary`                                                       | the job client                  |                           |
| `agent.list`, `agent.get`, `agent.timeline`                         | the job client                  | the count, or the agent   |
| `admission.list`, `.get`, `.admit`, `.reject`, `.revoke`, `.delete` | `internal/controller/admission` | the count, or the machine |
| `audit.list`, `audit.get`, `audit.export`                           | `internal/audit`                | the count, or the entry   |
| `traces.read`                                                       | `internal/telemetry/traces`     | the trace ID              |

Without them, `trace get` showed `GET /api/job` with only the two response
spans, because it leaves out the NATS calls, and the trace did not tell what the
time of the request was for (osapi-io/osapi#866). `traces.read` is the HTTP call
to Jaeger, which no other span showed. An operation of one call, such as a file
`info`, has no span of its own: the span of its NATS call is enough. An
`agent.get` for a hostname, not a machine ID, has an `agent.list` under it,
because it scans the registry. The controller takes DETAIL from two tables,
`opCounts` and `opDetail` in `internal/controller/endpoints/telemetry/tree.go`.
`trace get` and the Traces page show what it answers. Each had a copy of the
rules, `internal/cli/trace.go` and `trace-tree.ts`, until osapi-io/osapi#904.

`trace get` and the Traces page show what ran each span in the `ON` column, the
role of the service that made it: `controller`, `agent` or `cli`. A blank cell
had stood for the controller, and a reader had to know that. DETAIL names each
value as `key=value`, so a value says what it is: `host=debian-1` on a
`job.process`, `target=_all`, `agents=3`, `op=` and `target=` of a job. A failed
span leads with `error=`, and a value with a space is quoted, as in logfmt.
`--json` gives each span's whole `attributes` map instead.

`trace get` shows the size on `response.write`. The request span has the size
too, from otelecho, but its DETAIL stays the status. On `job.publish`, DETAIL is
the operation and the target that the caller gave, such as
`behavior.sysctl.get to debian-1`. The NATS subject names one host by its
machine ID, such as `osapi.jobs.query.host.d530664e…`, so that a renamed host
still gets its jobs, and the subject stays in `messaging.destination.name`. A
trace from before shows the subject.

These choices are deliberate:

- **The agent span names the host.** `job.process` has `osapi.agent.hostname`,
  `osapi.agent.machine_id` and `host.arch`. The agent resolved them before the
  job, so a span looks up nothing. The resource of a span has only
  `service.name` and `service.version`. A tracer resource detector would look up
  the host again, and on a controller the host does not tell anything.
- **A skipped host is not an error.** Its `job.process` has `job.status`
  `skipped` and a `job.skipped` event. A failed job has the error status. A
  timed-out agent is an event on `job.collect`, and is not an error of the
  request.
- **A command span has no arguments.** An argument can hold a secret. The span
  has the program, `osapi.exec.sudo` and the exit code.
- **Each call to NATS is a span, from nats-client.** osapi calls NATS only
  through nats-client, which makes a span for each call inside a trace. A call
  outside a trace, such as a heartbeat, makes no span.
  [The transport](../../ARCHITECTURE.md#the-transport) has the rule.
- **A file write has no content.** `file.write`, from `internal/atomicfile`, has
  `file.path`, `file.mode` and `file.size`. A caller writes only a file whose
  content differs, so the span is a change.
- **The health endpoints and the files of the UI have no spans.** A probe and
  the UI call them each few seconds, and their traces hide the traces of the
  jobs.
- **The startup ping of Docker has no span.** On a host without Docker, it is an
  error with no request behind it.

Two tests hold the tree at the one place where it crosses a process: the headers
of the NATS message. The test in `internal/job/client` checks that `job.publish`
and `job.collect` are under the request, and that the context that goes with the
job is under `job.publish`, with the watch for the answers under `job.collect`.
It also checks that each read span is under the request, with its NATS calls
under it, and has the error status when the call fails. The test in
`internal/agent` gives the handler the context that nats-client reads from the
headers, and checks that `job.process` is a child of it, with the host and the
status.

### Reading a trace through the controller

`osapi client telemetry trace get --id <trace>` and the Traces page of the UI
show the span tree of a trace. They ask the controller, at
`GET /api/telemetry/trace/{id}`, with `trace:read`. The controller answers the
summary of the trace and its spans as a tree: each span with ON, STATUS, DETAIL,
the span as the backend has it, and its children. Without the query parameter
`all`, it leaves out the NATS calls, moves the spans under them up, and counts
them. `--all` and the check box of the Traces page send it. The controller asks
the tracing backend. Thus the machine of the CLI needs no access to the backend,
as with the trace ID.

OpenTelemetry has no standard API to read a trace. The controller reads the
query API of Jaeger, `/api/v3/traces/{id}`, which answers OTLP JSON, at
`telemetry.tracing.url`. For Jaeger, that is the same address where a person
opens the UI, so one setting is enough. `internal/telemetry/traces` holds the
reader, and a different backend, for example Tempo, is a second reader beside
it. Without the setting, the route answers 503 and names the setting.

The backend gets the spans a few seconds after the request. The controller
answers 404 for a trace that it does not have yet, and the message says to try
again.

The CLI shows a span under its parent, with the host of the `job.process` above
it. STATUS is the job status on a `job.process`, `changed` or `unchanged` on a
behavior write, and `ok` or `error` on the other spans. DETAIL is the error of a
failed span, or what the span acted on: the inputs that a behavior records, a
file or a subject.

The NATS calls are the bookkeeping of the job queue, and they are most of the
spans: 34 of the 42 of a package list on three hosts. The CLI leaves them out by
default and counts them, and a span under one moves up to the span above it.
Thus the tree shows the work: the request, each agent, each behavior, command
and file change. `--all` shows the NATS calls, and DETAIL says what each key is
for, from the shape of the key: `status: started`, `response`, `file record`,
`registration`, `drain flag`. The raw key stays in `--json` and in the backend.
The UI shows the same tree with a timing bar, and a check box for the NATS
calls.

`NewTraceHandler` wraps `slog`, so that a log line has its trace and span IDs.
This connects a log to a trace without a separate correlation ID. For the same
reason, an audit entry has `trace_id`. Thus you can join three records of the
same request.

## Metrics run on their own port

The metrics port is `controller.metrics.port`, 9090 by default. It is separate
from the API port, 8080. Thus a scrape does not go through the authenticated
API, and a scraper needs no token. The tradeoff: the metrics port has no
authentication. Put it behind a firewall. Do not expose it.

Three metrics are about liveness:

| Metric                        | Is                                              |
| ----------------------------- | ----------------------------------------------- |
| `osapi_component_up`          | whether a component reports itself healthy      |
| `osapi_subsystem_up`          | the same, one level down, per `SubsystemStatus` |
| `osapi_heartbeat_age_seconds` | how long since an agent last checked in         |

Four metrics count jobs:

| Metric                       | Recorded by | Is                                                     |
| ---------------------------- | ----------- | ------------------------------------------------------ |
| `osapi_jobs_created_total`   | controller  | each job that the controller published, one per target |
| `osapi_jobs_processed_total` | agent       | each job that the agent finished, by `status`          |
| `osapi_jobs_active`          | agent       | the jobs that the agent runs now                       |
| `osapi_job_duration_seconds` | agent       | how long each job ran on the agent, as a histogram     |

Each component also records `osapi_nats_client_operation_duration_seconds`, from
nats-client, for each call to NATS: by operation and by bucket or stream, with
`error_type` on a failure. A key or a subject is never a label. Each connection
gets the meter provider of its component, so each metrics server shows the calls
of its own component.

No metric measures the queue depth: the jobs that the API queued and that no
agent has taken. If you need it now, read it from the job status events in
`job-queue`. Know about this gap before you plan a dashboard.

## A sub-component has an address and a URL

The health response lists the sub-components of each component under its
registry entry, as `components`, sorted by name. The heartbeat names them
`controller.api`, `agent.metrics` and `nats.server`. Under its component, a
sub-component is `api`, `metrics` or `server`. `osapi client health status`
prints each component with its sub-components under it, as a tree. The answer
had them in one map of the whole fleet, keyed `controller.api`, and the CLI and
the UI each matched the prefix to find the component (osapi-io/osapi#904).

`GET /api/controller/status`, `/api/nats/status` and `/api/agent/status` answer
the components of one type, with their sub-components, as a list with its count.
They filter the health status, so the data is the same.
`osapi client nats status` and the others print the same tree for one type.

The controller also checks its connection to NATS and to KV for each answer.
These are in `checks`, each with its name, its status and, when it failed, its
error.

Each sub-component can have two endpoints:

| Field     | Is                                       | Comes from                |
| --------- | ---------------------------------------- | ------------------------- |
| `address` | the endpoint that the process listens on | the listen host and port  |
| `url`     | the location where a person opens it     | a `url` key in the config |

No code reads `address` to connect. A process connects through its own config:
the CLI uses `controller.client.url`, and the exporter uses
`telemetry.tracing.otlp_endpoint`. Thus `address` shows the bind address, and on
a host that listens on all interfaces it is `0.0.0.0`. A person cannot open that
address.

osapi does not calculate `url`. Only the operator knows the path from a person
to the process: a tailnet name, a reverse proxy or an SSH tunnel. Thus `url`
comes only from the config. When the key is empty, the response does not include
`url`, and the output is the same as before. osapi checks that each `url` is an
absolute `http` or `https` URL with a host when it loads the config, with the
`http_url` rule of the validator. The port and the path are optional.
`nats.server.url` is different: it must start with `nats://` or `tls://`,
because a person reaches NATS with a client, not a browser. osapi does not send
a request to a URL.

| Sub-component        | `address` from                         | `url` from                |
| -------------------- | -------------------------------------- | ------------------------- |
| `controller.api`     | `controller.api.host` and `.port`      | `controller.api.url`      |
| `controller.ui`      | `controller.api.host` and `.port`      | `controller.ui.url`       |
| `controller.metrics` | `controller.metrics.host` and `.port`  | `controller.metrics.url`  |
| `controller.tracing` | `telemetry.tracing.otlp_endpoint`      | `telemetry.tracing.url`   |
| `agent.metrics`      | `agent.metrics.host` and `.port`       | `agent.metrics.url`       |
| `nats.server`        | `nats.server.host` and `.port`         | `nats.server.url`         |
| `nats.metrics`       | `nats.server.metrics.host` and `.port` | `nats.server.metrics.url` |

Each listener that osapi starts has a `host` key for its bind address. The API
got `controller.api.host` with the `url` field. Before that, the API listened on
all interfaces, and the health response showed `0.0.0.0` as a fixed string. An
empty `controller.api.host` keeps that behavior. The UI uses the listener of the
API. Thus you cannot bind the UI to `127.0.0.1` and the API to all interfaces.
Set the two together.

Tracing is different from the other sub-components. It listens on nothing: it
sends spans to `otlp_endpoint`. Thus its `address` is that destination, as
`grpc://<otlp_endpoint>`, and only when the exporter is `otlp`. It is the one
`address` that is not a bind address. `telemetry.tracing.url` points to the
trace viewer, for example Jaeger. osapi does not run that viewer. The URL lets a
person go from the health output to the traces.

Each process sends its sub-components in its heartbeat, in
`job.SubComponentInfo`: the controller from `internal/controller/heartbeat.go`,
an agent and the NATS server from theirs. The health handler also gets the
sub-components of the controller from `internal/controller/handlers.go`, as
`health.SubComponentInfo`. An entry from the registry replaces an entry of the
same name, thus the heartbeat is the copy that a person sees. Both structs get
`url` with `omitempty`. An agent of an older version sends no `url`, and the
controller shows only its `address`.

Each registration has the build version of the component's binary, such as
`v0.2.1-0.20261119003517-f6bc5af55ceb`, which ends with the commit. `cmd` has it
from `appVersion()` and gives it to the agent (`SetVersion`), to the controller
(`controller.WithVersion`) and to the NATS server (`StartHeartbeat`). The health
status has it on each registry entry as `version`, `health status` prints a
VERSION column, and the dashboard shows it on each component row. The top-level
`version` of the health status is the controller's, which is also the UI's: the
controller serves the UI from its own binary. The controller and the NATS server
had a literal `0.1.0` (osapi-io/osapi#878).

Each registration also has the process metrics of the component itself, as
`process`: its CPU share, its RSS and its goroutine count. The process
conditions, such as memory pressure, come from them. gohai reads the process:
`Read` of its process collector, with the component's own PID, reads that one
process and not the others (osapi-io/gohai#305). The CPU share is the difference
of gohai's `cpu_seconds` between two heartbeats, over the time between them, so
a spike shows in the next heartbeat and an average since start does not hide it.
The goroutine count comes from the Go runtime (osapi-io/osapi#960).

An agent's row in the registry takes the agent's scheduling state from its
registration, as `agent list` does: a drained agent is `Draining` or `Cordoned`,
in amber, and an agent with no state is `Ready`. The API always gives `state`.
The agent had a `status` field too, which was always `Ready`. It is removed. The
entry had the literal `Ready`, so `health status` showed a drained agent as
ready while `agent list` showed it as cordoned (osapi-io/osapi#879). The
controller and the NATS server have no scheduling state, and their `Ready` means
that they are registered.

`agent list` and the health status take an agent's state by one rule,
`job.EffectiveState`, from the state the agent reported and its drain flag. A
drain that the agent has not applied yet is `Draining`, and it is `Cordoned`
only once the agent reports that its consumers stopped. `agent list` had said
`Cordoned` as soon as the flag was set, while the agent could still be running
jobs (osapi-io/osapi#884). The UI's card waits for `Cordoned` before it clears
the feedback of a drain.

The `agents` count of the health status, the dashboard's Agents tile, follows
the same state: `ready` counts the agents whose state is `Ready`, and `total`
counts each registered agent. A drained agent is in `total` and not in `ready`.
The count had `ready` equal to `total`, so the tile said `3/3 ready` with an
agent cordoned.

The agent takes jobs only when it is `Ready`, with one set of consumers.
`startConsumers` at startup starts them only in `Ready`, because the heartbeat
starts first and can find the drain flag and cordon the agent before startup
reaches the consumers. Starting consumers while a set runs does nothing, and
stopping them clears the set, so a drain always stops every consumer it waits
for. Before osapi-io/osapi#876, an agent that started with its drain flag set
took jobs while cordoned, the undrain started a second set over the first, and
the next drain waited for the first set forever, inside the heartbeat: the agent
stopped heartbeating and dropped out of the registry, though the process ran.

A drain never holds the heartbeat. It cancels the consumers, moves the agent to
`Draining` and returns, and a goroutine waits for the cancelled set and moves
the agent to `Cordoned`. Each set has its own wait group, so a drain waits only
for the set it cancelled. When the consumers have not stopped after a minute,
the agent logs a warning and reports the `DrainStuck` condition, amber in the
CLI and the UI, and goes on heartbeating. An undrain that comes while the agent
is still `Draining` applies once the drain has finished.

`osapi client health status`, and the `status` command of `agent`, `controller`
and `nats`, print the components from their type, as each command does
([the CLI](cli.md#output-comes-from-the-output-type)). Each sub-component is a
row under its component, as a tree. The address and the URL are columns, so a
long URL is not cut, and a column with no value in any row is left out:

```
Components (1):
  TYPE          HOSTNAME  STATUS  CONDITIONS  ADDRESS                URL
  controller    hub       Ready   -
  ├─ api                  ok      -           http://0.0.0.0:8080    http://hub.example.ts.net:8080/
  ├─ heartbeat            ok      -
  ├─ metrics              ok      -           http://127.0.0.1:9090
  └─ tracing              ok      -           grpc://127.0.0.1:4317  http://hub.example.ts.net:16686/
```

This replaced `displayComponentTable` in `cmd/`, which put the URL on a line of
its own under each row (osapi-io/osapi#904).

The dashboard has the same layout. `ComponentRow` in
`ui/src/components/domain/component-row.tsx` puts the URL on a line under the
row. An `http` or `https` URL is a link in the text color that opens in a new
tab, as the [UI colors](ui.md) say. A URL with a different scheme, such as
`nats://`, is text, because a browser cannot open it.

## Behaviors measure their own work

A [behavior](behaviors.md) gets telemetry, and you write no telemetry code.
`internal/behaviors/telemetry.go` wraps each method call. Thus osapi measures a
new behavior when you register it. Providers that are not behaviors yet record
none of this.

Each call opens a span with the name `behavior.<name>.<method>`, under the job
span of the agent. Thus a trace goes from the API request, through the queue, to
the method that did the work. The span has `osapi.behavior.name`, `.method`,
`.verb`, `.outcome` and `.changed`.

osapi adds two kinds of input field as `osapi.behavior.input.<field>`: the field
that the method names with `.Key`, and each field with the tag
`telemetry:"attr"`. It adds no other field, and never a field with the tag
`secret:"true"`. Thus a password cannot get into a trace by accident.
managedfile tags `path`, because its methods have no `.Key`. Thus the span of a
file write that sysctl causes shows the file.

The same wrapper makes three metrics, through the meter provider of the agent:

| Metric                            | Is                                                   |
| --------------------------------- | ---------------------------------------------------- |
| `osapi_behavior_calls_total`      | calls, by behavior, method and outcome               |
| `osapi_behavior_duration_seconds` | how long each call took, by behavior and method      |
| `osapi_behavior_changes_total`    | writes that changed the host, by behavior and method |

`osapi behavior get --name <name>` prints the span and metric names of a
behavior. It also prints which inputs osapi records.

## Conditions are a yes or no, not a number

`EvaluateProcessConditions` in `internal/agent/condition.go` returns three
booleans. Each has a reason string. A metric is a number over time. A condition
is an answer now. A fleet view needs that answer to show that a host is
degraded, so that an operator does not have to read a graph.

| Condition                 | True when                                 | Default                         |
| ------------------------- | ----------------------------------------- | ------------------------------- |
| `ConditionHighLoad`       | 1-minute load average > CPUs × multiplier | `high_load_multiplier: 2.0`     |
| `ConditionMemoryPressure` | memory used % over the threshold          | `memory_pressure_threshold: 90` |
| `ConditionDiskPressure`   | **any** mount over the threshold          | `disk_pressure_threshold: 90`   |

The three are under `agent.conditions` in `osapi.yaml`. Two details can surprise
you:

- The high-load condition changes with the CPU count. It is not absolute. A 2.0
  multiplier means load 8 on a four-core machine, and load 64 on a 32-core
  machine.
- Disk pressure examines each mount. It becomes true on the first mount that is
  over the threshold. Thus a full `/boot` degrades the host.

Each condition has the numbers that made it true, for example
`"load 9.12, threshold 8.00 for 4 CPUs"`. Thus an operator does not have to find
the numbers to decide if the condition is important.

**The API gives only the conditions that are true.** `agent list` and
`agent get` leave out a condition that is false, and a condition in the answer
has no `status` field. The health status gives the same set, as a list of names.
The agent's registration keeps all three, with the time of each change. The
notifier reads them from there, and thus it sees when a condition becomes false.
The UI, the CLI and the health registry each removed the false conditions by
themselves (osapi-io/osapi#904).

## Where this connects

[The audit trail](audit.md) has the `trace_id` on an audit entry, and how it
joins to a log line.

The published site has the health endpoints that an orchestrator polls. They are
separate from these metrics, and an operator looks for them there.

[Configuration](configuration.md) has `telemetry` as a config section.

______________________________________________________________________

Written from `internal/telemetry/`.
