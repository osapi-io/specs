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
