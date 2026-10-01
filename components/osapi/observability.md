# Observability

Four separate things under `internal/telemetry`, and they answer different
questions.

| Subsystem | Answers                                      |
| --------- | -------------------------------------------- |
| `tracing` | where did this request go                    |
| `metrics` | what is the state of this process, over time |
| `process` | is this process healthy right now            |
| `httplog` | what did the HTTP layer see                  |

## Tracing carries across the queue

`InitTracer` sets up OpenTelemetry with an OTLP exporter, or a stdout one for
development.

The part worth knowing is propagation. `ExtractTraceContext` and
`ExtractTraceContextFromHeader` pull a trace context out of an incoming request,
and because work reaches a host through the queue rather than through a call,
that context has to travel **with the job** rather than down a stack. A trace
that stopped at the API boundary would show a request that queued something and
nothing after it.

`NewTraceHandler` wraps `slog` so a log line carries its trace and span IDs.
That is what joins a log to a trace without a correlation ID of its own, and it
is why an audit entry carries `trace_id`: three records of the same request,
joinable.

## Metrics run on their own port

`controller.metrics.port`, 9090 by default, separate from the API's 8080, so
scraping does not go through the authenticated surface and a scraper needs no
token. The tradeoff is that the metrics port has no authentication at all, so it
has to be firewalled rather than exposed.

Three metrics, all about liveness rather than about work:

| Metric                        | Is                                              |
| ----------------------------- | ----------------------------------------------- |
| `osapi_component_up`          | whether a component reports itself healthy      |
| `osapi_subsystem_up`          | the same, one level down, per `SubsystemStatus` |
| `osapi_heartbeat_age_seconds` | how long since an agent last checked in         |

```sh
grep -rhoE 'osapi_[a-z_]+' --include='*.go' internal/ | sort -u | wc -l   # 3
```

Nothing counts jobs, measures provider latency or tracks queue depth. If you
need that today you read it off the job status events in `job-queue`, which is
the gap worth knowing about before you plan a dashboard.

## Conditions are a yes or no, not a number

`EvaluateProcessConditions` in `internal/agent/condition.go` returns three
booleans with a reason string each. A metric is a number over time; a condition
is an answer right now, which is what a fleet view needs to say a host is
degraded without an operator reading a graph.

| Condition                 | True when                                 | Default                         |
| ------------------------- | ----------------------------------------- | ------------------------------- |
| `ConditionHighLoad`       | 1-minute load average > CPUs × multiplier | `high_load_multiplier: 2.0`     |
| `ConditionMemoryPressure` | memory used % over the threshold          | `memory_pressure_threshold: 90` |
| `ConditionDiskPressure`   | **any** mount over the threshold          | `disk_pressure_threshold: 90`   |

All three are under `agent.conditions` in `osapi.yaml`. Two details that bite:
the high-load one scales with CPU count rather than being absolute, so a 2.0
multiplier means load 8 on a four-core box and load 64 on a 32-core one; and
disk pressure loops over every mount and trips on the first one over the
threshold, so a full `/boot` degrades the host.

Each condition carries the numbers that tripped it,
`"load 9.12, threshold 8.00 for 4 CPUs"`, so an operator does not have to go and
look them up to decide whether it matters.

## Where this connects

The `trace_id` on an audit entry, and how it joins to a log line, is
[the audit trail](audit.md).

The health endpoints an orchestrator polls, which are a separate thing from
these metrics, stay on the published site where an operator will look.

`telemetry` as a config section is [configuration](configuration.md).

______________________________________________________________________

Written from `internal/telemetry/`.
