# Agent wiring

Two files connect a provider to the job pipeline. Nothing else changes: not
`agent/types.go`, not `agent/agent.go`, not the `JobClient` interface. The
registry handles dispatch and facts wiring.

## 1. The processor

`internal/agent/processor_{domain}.go` turns a job request into a provider call
and its result into JSON.

```go
func process{Domain}Operation(
    provider {domain}.Provider,
    logger *slog.Logger,
    req job.Request,
) (json.RawMessage, error) {
    // switch on req.Operation, call the provider, marshal the result
}
```

Two shapes, depending on whether the domain is its own category:

- **Its own category**, as `schedule` and `docker` are: add a
  `New{Domain}Processor` factory beside the helpers.
- **Inside an existing category**, usually `node`: add a `case` to that
  category's processor and delegate to helpers in the new file. Read
  `processor_node.go` for the current switch.

Operation constants are defined once in `pkg/sdk/client/operations.go` as
`JobOperation` strings shaped `{category}.{domain}.{operation}`, for example
`"node.sysctl.list"`. `internal/job/types.go` aliases each one as
`Operation{Domain}{Operation}` for use inside the repository. Add the constant
to `operations.go` and the alias beside its siblings, and never write the string
literal at a call site: that is how a handler and an agent come to disagree
about an operation name.

## What a domain does not touch

The sibling NATS projects stay out of this. Nothing under `internal/provider/`,
`internal/controller/` or `pkg/sdk/` imports `osapi-io/nats-client`; only
`cmd/` wiring, `internal/agent/consumer.go` and `internal/cli` do. A new domain
reuses the subjects that already exist (`jobs.query.*` and `jobs.modify.*`,
routed per host) and the buckets that already exist, so it adds no stream, no
consumer and no KV bucket.

Streams and buckets are declared once in `internal/job/config.go`. A domain
that genuinely needs storage of its own is a change to the job layer, with its
own spec, rather than part of adding a domain. Meta providers write through the
file-state KV the file provider already owns.

## 2. The registration

`cmd/agent_setup.go` constructs the provider and registers it.

```go
// A new category
registry.Register("{domain}",
    agent.New{Domain}Processor({domain}Prov, log),
    {domain}Prov)

// An existing category: pass the provider into that category's
// processor factory, and include it in the providers list so
// WireProviderFacts reaches it. Read the current parameter list.
```

Platform selection happens here, not in the provider. `Detect` and
`IsContainer` come from `pkg/sdk/platform`:

```go
switch osFamily {
case "debian":
    if platform.IsContainer() {
        prov = {domain}.NewDebianDockerProvider(...)
    } else {
        prov = {domain}.NewDebianProvider(execManager, ...)
    }
case "darwin":
    prov = {domain}.NewDarwinProvider(...)
default:
    prov = {domain}.NewLinuxProvider()
}
```

An SDK-based provider has no switch. Construct it, check availability, and
leave it nil when unavailable so the operation reports unsupported rather than
panicking.

## Delivery semantics worth knowing before you add an operation

The agent acknowledges a message once the operation has run and its response and
status are recorded, whether it succeeded or failed. Before running, it checks
whether it has already answered that job and skips re-execution if so, which
covers a crash between executing and acknowledging.

What that means for a new operation:

- **A failure is reported, not retried.** Return an error from the provider and
  it becomes a failed job with the message, once.
- **Redelivery must not be your safety net.** The provider's idempotency is what
  makes a repeat safe.
- **A long operation is kept alive** while it runs, so it is not redelivered
  mid-flight. Nothing to do per domain.
- `job retry` creates a new job rather than replaying the old message.

## Facts

`provider.WireProviderFacts(a.GetFacts, registry.AllProviders()...)` injects
facts into every registered provider. A provider registered through the registry
is covered; one constructed and passed somewhere else is not.

## Tests

- `internal/agent/processor_{domain}_public_test.go`: one suite method per
  helper, table rows covering each sub-operation, an unknown operation, and a
  provider error.
- Mock the provider from `internal/provider/{category}/{domain}/mocks/`.
- `cmd/` is excluded from the coverage gate by `.coverignore`, so the wiring in
  `agent_setup.go` is proved by the integration suite rather than a unit test.
