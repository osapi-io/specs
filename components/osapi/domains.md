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

The provider runs on the agent, not the controller, so a handler has nothing to
call: the work is on a different machine. Everything a domain owes the job
system comes from that.

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

Everything else is convention, and the nine-step procedure is in osapi's
`docs/docs/sidebar/development/adding-an-api-domain.md`, which belongs beside
the code rather than here.

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

## Whether the driver is in the URL

Most domains are implemented by some tool. `package` runs apt, `ntp` runs
chrony, `container` runs Docker, `schedule` writes crontab entries. Whether that
tool appears in the URL comes down to one question.

**Does the caller choose it, or does the host?**

A caller chooses a container runtime. Running Docker rather than Podman is a
decision somebody made and wants to address directly, so the runtime is a path
segment: `/container/docker`. Adding Podman adds `/container/podman` beside it,
and both can exist on one host.

A caller does not choose a package manager. The host already decided, and asking
a fleet to install a package cannot mean knowing which of them run apt. So the
tool is absent: `/package`, with the provider picking apt or anything else by OS
family. `/ntp` is the same, with chrony behind it today and room for another
driver later at the same entrypoint. `/schedule` likewise: cron now, possibly
`at` later, and the caller should not have to care which.

Getting this backwards in either direction costs something real. A tool in the
URL that the caller did not choose makes a fleet-wide call impossible. A tool
missing from the URL that the caller did choose makes two runtimes on one host
unaddressable.

## Each layer takes the name from the URL it serves

Once the URL is settled, nothing below it invents a name.

| Layer                 | Takes its name from | `/container/docker`      | `/network/dns`         |
| --------------------- | ------------------- | ------------------------ | ---------------------- |
| API handler directory | the first segment   | `api/node/container/`    | `api/node/network/`    |
| API handler files     | the second segment  | `docker_create.go`       | `dns_get.go`           |
| agent processor       | the first segment   | `processor_container.go` | `processor_network.go` |
| SDK service           | the last segment    | `client/docker.go`       | `client/dns.go`        |
| CLI command           | the path            | `node container docker`  | `node network dns`     |

The API layer is flat. A domain gets one directory named for the first segment,
and the second segment is a filename prefix inside it rather than a
subdirectory.

The provider tree is the exception, and deliberately. It nests by what
implements a thing, so a second driver is a new directory beside the first
rather than a scattering of files: `provider/container/docker` and, when it
exists, `provider/container/podman`. That tree may therefore be deeper than the
URL, which is how `provider/network/netplan/dns` serves `/network/dns`.

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

## A domain is in every layer, or it is not done

A domain is not one artifact. It is a provider, an agent processor and its
registration, a spec and the code generated from it, a handler and its route, an
SDK service, CLI commands, and the documentation pages and permission tables
that name it.

Missing one of those is not a smaller domain. It is a domain that works until
somebody reaches it the way the missing layer would have been reached, and the
gap shows up as a bug rather than as an absence.

The check is to pick a finished domain and search for its name across the
repository, then run the same search for the new one. The two lists should have
the same shape. A name that appears in eighty files and a name that appears in
sixty is the answer.

```bash
grep -rl 'sysctl\|Sysctl' --include='*.go' --include='*.yaml' --include='*.md' . \
  | grep -vE '/gen/|/node_modules/|docs/docs/gen'
```

## Where this connects

What the provider you are adding must implement, and the three boundary rules it
owes, is [providers](providers.md).

Delivery semantics, the two clocks and the four result statuses are
[the job system](job-system.md).

The generated client the combined specification also feeds is
[the embedded UI](ui.md).

______________________________________________________________________

Written from `internal/controller/api/` and `cfg.yaml`.
