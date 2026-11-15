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

`NewTraceHandler` wraps `slog`, so that a log line has its trace and span IDs.
This connects a log to a trace without a separate correlation ID. For the same
reason, an audit entry has `trace_id`. Thus you can join three records of the
same request.

## Metrics run on their own port

The metrics port is `controller.metrics.port`, 9090 by default. It is separate
from the API port, 8080. Thus a scrape does not go through the authenticated
API, and a scraper needs no token. The tradeoff: the metrics port has no
authentication. Put it behind a firewall. Do not expose it.

There are three metrics. They are about liveness, not about work:

| Metric                        | Is                                              |
| ----------------------------- | ----------------------------------------------- |
| `osapi_component_up`          | whether a component reports itself healthy      |
| `osapi_subsystem_up`          | the same, one level down, per `SubsystemStatus` |
| `osapi_heartbeat_age_seconds` | how long since an agent last checked in         |

```sh
grep -rhoE 'osapi_[a-z_]+_(up|seconds)' --include='*.go' internal/ | grep -v '^osapi_behavior_' | sort -u | wc -l   # 3
```

No metric counts jobs or measures the queue depth. If you need that now, read it
from the job status events in `job-queue`. Know about this gap before you plan a
dashboard.

## A sub-component has an address and a URL

The health response lists the sub-components of each component, for example
`controller.api`, `agent.metrics` and `nats.server`. Each sub-component can have
two endpoints:

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

`displayComponentTable` in `cmd/client_health_status.go` prints the
sub-components for `osapi client health status`, and for the `status` command of
`agent`, `controller` and `nats`. Each row has the same shape. The status and
the address are on the row. The URL is on a line of its own under it, so a long
URL is never cut, and a row without a URL takes one line. Each part has its own
style: the status word in its status color, the address dim because nothing
connects through it, and the URL cyan because a person opens it. The table sizes
and cuts cells by visible width, thus the escape sequences of the styles do not
count:

```
controller  hub           Ready
            ├─ api        ok http://0.0.0.0:8080
            │             ↳ http://hub.example.ts.net:8080/
            ├─ heartbeat  ok
            ├─ metrics    ok http://127.0.0.1:9090
            ├─ tracing    ok grpc://127.0.0.1:4317
            │             ↳ http://hub.example.ts.net:16686/
            └─ ui         ok http://0.0.0.0:8080
                          ↳ http://hub.example.ts.net:8080/
```

The dashboard has the same layout. `ComponentRow` in
`ui/src/components/domain/component-row.tsx` puts the URL on a line under the
row. An `http` or `https` URL is a link that opens in a new tab, in
`--color-link`, the cyan of the `URLStyle` of the CLI. It is not green, because
green means `ok`. A URL with a different scheme, such as `nats://`, is text,
because a browser cannot open it.

## Behaviors measure their own work

A [behavior](behaviors.md) gets telemetry, and you write no telemetry code.
`internal/behaviors/telemetry.go` wraps each method call. Thus osapi measures a
new behavior when you register it. Providers that are not behaviors yet record
none of this.

Each call opens a span with the name `behavior.<name>.<method>`, under the job
span of the agent. Thus a trace goes from the API request, through the queue, to
the method that did the work. The span has `osapi.behavior.name`, `.method`,
`.verb`, `.outcome` and `.changed`.

osapi adds an input field with the tag `telemetry:"attr"` as
`osapi.behavior.input.<field>`. It never adds a field without the tag. Thus a
password cannot get into a trace by accident.

The same wrapper makes three metrics, through the meter provider of the agent:

| Metric                            | Is                                                   |
| --------------------------------- | ---------------------------------------------------- |
| `osapi_behavior_calls_total`      | calls, by behavior, method and outcome               |
| `osapi_behavior_duration_seconds` | how long each call took, by behavior and method      |
| `osapi_behavior_changes_total`    | writes that changed the host, by behavior and method |

```sh
grep -rhoE 'osapi_behavior_[a-z_]+' --include='*.go' internal/behavior/ | sort -u | wc -l   # 3
```

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

## Where this connects

[The audit trail](audit.md) has the `trace_id` on an audit entry, and how it
joins to a log line.

The published site has the health endpoints that an orchestrator polls. They are
separate from these metrics, and an operator looks for them there.

[Configuration](configuration.md) has `telemetry` as a config section.

______________________________________________________________________

Written from `internal/telemetry/`.
