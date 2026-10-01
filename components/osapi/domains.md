# Building a domain

A domain is a coherent area of system behaviour exposed as API endpoints. Adding
one touches every layer, and the obligation is **consistency**: a domain appears
in every place an existing domain appears.

That makes the completeness check mechanical rather than a matter of judgement.
Pick a finished domain, `sysctl` or `cron`, and search the codebase for its
name. Anything that exists for it and not for yours is missing.

## Node-targeted or controller-only

This decides where the code goes, and **the directory is the consequence rather
than the rule**.

An operation is **node-targeted** when the work happens on a managed machine: it
is addressed to a host, dispatched through the job system, and carried out by a
provider on an agent. Those live under `internal/controller/api/node/{domain}/`.

An operation is **controller-only** when the controller answers it itself. Those
live directly under `internal/controller/api/{domain}/`.

A contributor who picks the directory first and reasons backwards gets this
wrong.

## The request path

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

The provider runs on the agent, not the controller. That is the fact that
explains why a handler cannot simply do the work, and it is what makes the job
system unavoidable rather than an implementation choice.

## What the build order forces, and what is habit

Some of the sequence is imposed by code generation. Stating the rest as a rule
would freeze a preference.

**Forced by tooling:**

1. The OpenAPI specification precedes generation, because generation reads it.
2. Generation precedes the handler, because the handler implements a generated
   interface.
3. The **combined** specification precedes the SDK client, because the SDK
   generates from the combined file.

That third one has a consequence worth stating on its own.
`internal/controller/api/gen/api.yaml` is assembled by `redocly join` from every
domain's own `gen/api.yaml` inside `just generate`. **A domain absent from the
combined file is invisible to the SDK however complete its own specification
is**. It fails silently too, because nothing reports a domain that simply is not
there.

Everything else in the nine-step walkthrough is convention, and the walkthrough
is where it belongs.

## Validation

The OpenAPI specification is the source of truth for input validation. A tag
goes in three places and does nothing in a fourth.

| Where                                    | What                                |
| ---------------------------------------- | ----------------------------------- |
| request body properties                  | `x-oapi-codegen-extra-tags`         |
| query parameters, at **parameter** level | not inside `schema:`                |
| UUID path parameters                     | `format: uuid`                      |
| path parameters                          | **nothing. No tags are generated.** |

The last row is a property of the generator's configuration. `cfg.yaml` sets
`strict-server: true`, which makes oapi-codegen produce an interface taking
typed parameters rather than raw request objects, and in that mode it generates
no validation tags on path parameters at all. So a path parameter needing
validation beyond `format: uuid` is validated by hand in the handler. There is
**no shared helper** for it: `validateHostname` is unexported and exists per
domain, so a handler writes its own or calls into `internal/validation` where a
registered validator fits.

A custom validation rule belongs in `internal/validation` with a hint in
`customHints`, so a 400 tells the caller what shape was expected rather than
naming a tag. `sysctl_key` and `cron_schedule` are the pattern.

## Verbs

A mutable domain uses **separate verbs for create and update**.

- `POST` creates, with the name in the body.
- `PUT /{name}` updates, taking the name from the path.

A combined set or upsert endpoint is forbidden, and the reason is that it is
what gives 404 a meaning. If one endpoint both creates and updates, a caller
cannot find out that the thing they meant to change does not exist.

## Design guidelines

Endpoints group by functional domain under their own top-level prefix. Paths are
resource-oriented, with sub-resources nested under their parent. An area
expected to grow is split into its own category early rather than after it gets
crowded. Everything targeting a managed machine sits under `/node/{hostname}`.
Path parameters identify; query parameters filter.

`{hostname}` accepts a literal hostname, the reserved values `_any` and `_all`,
or a `key:value` label selector. `IsBroadcastTarget` in
`internal/job/subjects.go` decides which, and **it has one implementation.** A
domain must not write its own target parser.

## Broadcast is not optional

Every operation under `/node/{hostname}/...` supports broadcast targeting, and
**both paths return the same collection shape.** A single target returns one
result; a broadcast returns as many as there are agents. Every result item
carries `hostname` and `error`.

So a caller writes one parser rather than two, and a partial failure is a row
rather than an exception.

## The job client needs nothing added

`JobClient` has four generic methods: `Query`, `QueryBroadcast`, `Modify`,
`ModifyBroadcast`. A new operation adds **none**, because a handler passes a
category string and an operation constant rather than calling a per-operation
method.

## Wiring

A domain package exports `Handler()`, returning route-registration closures, and
wraps the handler in scope middleware itself. **The `Server` struct does not
change.** Startup wiring is one appended line in `registerControllerHandlers` in
`cmd/controller_setup.go`.

On the agent side, two files connect a provider: a processor under
`internal/agent/` and the registration in `cmd/agent_setup.go`. What does
**not** change is `agent/types.go`, `agent/agent.go` and the `JobClient`
interface, because the registry handles dispatch and facts wiring.

## Permissions

How to choose one is [permissions](permissions.md)' subject, in a sentence there
about blast radius. What belongs here is the mechanics.

A new one has to be added in four places, and [permissions](permissions.md) says
what each omission costs. **A permission that exists in the specification and in
no role reaches nobody**, and nothing reports it.

## Where this connects

What the provider you are adding must implement, and the three boundary rules it
owes, is [providers](providers.md).

Delivery semantics, the two clocks and the four result statuses are
[the job system](job-system.md).

The generated client the combined specification also feeds is
[the embedded UI](ui.md).

______________________________________________________________________

Traced to `../../history/osapi-005-building-a-domain/`, which moved this off the
published site and found four places where the page disagreed with the code. The
sharpest: it told a contributor to call a shared `node.validateHostname()`
helper that does not exist and would not compile from another package.
