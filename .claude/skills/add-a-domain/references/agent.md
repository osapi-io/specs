# Agent wiring

Two files connect a provider to the job pipeline, and the registry handles
dispatch and facts wiring.

## Two rules are in the corpus, not here

| What you need to know | Where |
| --- | --- |
| Two files connect a provider, and what does **not** change: `agent/types.go`, `agent/agent.go`, the `JobClient` interface | [FR-009](../../../../components/osapi/domains.md) |
| The `FactsAware` obligation: embed it, add the compile-time `FactsSetter` check | [FR-010](../../../../components/osapi/domains.md) |

This file holds the shapes and the file names. The rules above are stated once,
in the corpus, so a change to either is a change in one place.

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

The job system's guarantees are specified in the corpus, which is where to read them
in full. What matters when adding an operation, and where each rule is stated:

| What you are relying on | Stated in |
| --- | --- |
| Delivery is at-least-once, and the agent checks for a recorded response before executing | [FR-009](../../../../components/osapi/job-system.md) |
| Which operations make that check load-bearing rather than theoretical | [FR-010](../../../../components/osapi/job-system.md) |
| A job that has run is terminal, a failure is reported, not retried by redelivery | [FR-011](../../../../components/osapi/job-system.md) |
| What happens when the response cannot be written after the work ran | [FR-012](../../../../components/osapi/job-system.md) |
| Which failures terminate a message instead of redelivering it | [FR-013](../../../../components/osapi/job-system.md) |
| The consumer's delivery settings, as defaults a deployment may override | [FR-014](../../../../components/osapi/job-system.md) |
| A long operation is kept alive while it runs, so it is not redelivered mid-flight | [FR-015](../../../../components/osapi/job-system.md) |

Two consequences for a new operation, which are yours rather than the system's:

- **Redelivery is not your safety net.** The provider's idempotency is what makes a
  repeat safe, the contract's own requirement, not this one.
- **`job retry` creates a new job** rather than replaying the old message, so
  nothing per-domain handles it.

## Facts

`provider.WireProviderFacts(a.GetFacts, registry.AllProviders()...)` injects
facts into every registered provider, one call, in `internal/agent/agent.go`. A
provider registered through the registry is covered; one constructed and passed
somewhere else is not. The obligation on the provider struct itself is
[FR-010](../../../../components/osapi/domains.md), and what a provider does with facts is
[001](../../../../components/osapi/providers.md) FR-008.

## Tests

- `internal/agent/processor_{domain}_public_test.go`: one suite method per
  helper, table rows covering each sub-operation, an unknown operation, and a
  provider error.
- Mock the provider from `internal/provider/{category}/{domain}/mocks/`.
- `cmd/` is excluded from the coverage gate by `.coverignore`, so the wiring in
  `agent_setup.go` is proved by the integration suite rather than a unit test.
