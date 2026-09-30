# Observability

Four separate things under `internal/telemetry`, and they answer different
questions.

| Subsystem | Answers                                        |
| --------- | ---------------------------------------------- |
| `tracing` | where did this request go                      |
| `metrics` | what is the state of this process, over time   |
| `process` | is this process healthy right now              |
| `httplog` | what did the HTTP layer see                    |

## Tracing carries across the queue

`InitTracer` sets up OpenTelemetry with an OTLP exporter, or a stdout one for
development.

The part worth knowing is propagation. `ExtractTraceContext` and
`ExtractTraceContextFromHeader` pull a trace context out of an incoming request,
and because work reaches a host through the queue rather than through a call, that
context has to travel **with the job** rather than down a stack. A trace that
stopped at the API boundary would show a request that queued something and nothing
after it.

`NewTraceHandler` wraps `slog` so a log line carries its trace and span IDs. That
is what joins a log to a trace without a correlation ID of its own, and it is why
an audit entry carries `trace_id`: three records of the same request, joinable.

## Metrics run on their own port

`controller.metrics.port`, 9090 by default, separate from the API's 8080. So
scraping does not go through the authenticated surface, and a metrics endpoint
does not need a token.

`SubsystemStatus` is the shape a component reports.

## Process conditions are a judgement, not a gauge

`EvaluateProcessConditions` takes `ConditionThresholds` and decides whether a
process is in a condition worth reporting. That is different from a metric: a
metric is a number over time, a condition is an answer now.

It is what a fleet view reads to say a host is degraded rather than making an
operator interpret a graph, and it is why an agent card can show a condition
without anybody configuring an alert.

## Where this connects

The `trace_id` on an audit entry, and how it joins to a log line, is
[the audit trail](audit.md).

The health endpoints an orchestrator polls, which are a separate thing from these
metrics, stay on the published site where an operator will look.

`telemetry` as a config section is [configuration](configuration.md).

______________________________________________________________________

Written from `internal/telemetry/` rather than from a feature.
