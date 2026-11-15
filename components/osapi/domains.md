# Building a domain

A domain is one area of system operation that osapi exposes as API endpoints. A
new domain touches each layer. The obligation is **consistency**: a domain must
be in each location where an existing domain is.

Thus the completeness check is mechanical. It does not need judgment. Select a
finished domain, `sysctl` or `cron`, and search the codebase for its name. If
something exists for it and not for your domain, it is missing.

## Node-targeted or controller-only

This decides where the code goes. **The directory is the result, not the rule.**

An operation is **node-targeted** when the work occurs on a managed machine. It
goes to a host, through the job system, and a provider on an agent does it.
These operations are under `internal/controller/api/node/{domain}/`.

An operation is **controller-only** when the controller answers it itself. These
operations are directly under `internal/controller/api/{domain}/`.

If a contributor selects the directory first and reasons from it, the result is
incorrect.

## The request path

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

The provider runs on the agent, not on the controller. Thus a handler has
nothing to call: the work is on a different machine. Everything that a domain
must give the job system comes from that.

## What the build order forces, and what is habit

Code generation forces part of the order. A rule for the rest makes a preference
permanent. Thus this page does not state one.

**The tools force this order:**

1. The OpenAPI specification comes before generation, because generation reads
   it.
2. Generation comes before the handler, because the handler implements a
   generated interface.
3. The **combined** specification comes before the SDK client, because the SDK
   is generated from the combined file.

The third has an important result. `redocly join` makes
`internal/controller/api/gen/api.yaml` from the `gen/api.yaml` of each domain,
in `just generate`. **The SDK cannot see a domain that is not in the combined
file, also if its own specification is complete.** This failure gives no signal,
because nothing reports a domain that is not there.

The rest is convention. A new area of a host is now a [behavior](behaviors.md),
not a hand-written domain.
`docs/docs/sidebar/development/your-first-behavior.md` in osapi builds one from
the start. This page stays for the domains that have not moved yet.

## Validation

The OpenAPI specification is the source of truth for input validation. A tag
goes in three locations, and does nothing in a fourth.

| Where                                    | What                                |
| ---------------------------------------- | ----------------------------------- |
| request body properties                  | `x-oapi-codegen-extra-tags`         |
| query parameters, at **parameter** level | not inside `schema:`                |
| UUID path parameters                     | `format: uuid`                      |
| path parameters                          | **nothing. No tags are generated.** |

The last row comes from the configuration of the generator. `cfg.yaml` sets
`strict-server: true`. With it, oapi-codegen makes an interface that takes typed
parameters, not raw request objects. In that mode, it makes no validation tags
on path parameters.

Thus the handler validates a path parameter by hand, when it needs more than
`format: uuid`. There is **no shared helper** for it. `validateHostname` is
unexported, and each domain has its own. Thus a handler writes its own check, or
calls `internal/validation` where a registered validator fits.

A custom validation rule goes in `internal/validation`, with a hint in
`customHints`. Thus a 400 tells the caller what shape was expected, and does not
only name a tag. `sysctl_key` and `cron_schedule` are the pattern.

## Verbs

A domain that changes things uses **separate verbs for create and update**.

- `POST` creates, with the name in the body.
- `PUT /{name}` updates, with the name from the path.

A combined set or upsert endpoint is forbidden, because the split gives 404 a
meaning. If one endpoint creates and updates, a caller cannot learn that the
thing that it wanted to change does not exist.

## Design guidelines

- Endpoints are in groups by functional domain, under their own top-level
  prefix.
- Paths are about resources. Sub-resources go under their parent.
- If an area will become larger, split it into its own category early, not after
  it becomes full.
- Each endpoint that targets a managed machine is under `/node/{hostname}`.
- Path parameters identify. Query parameters filter.

`{hostname}` accepts a literal hostname, the reserved values `_any` and `_all`,
or a `key:value` label selector. `IsBroadcastTarget` in
`internal/job/subjects.go` decides which, and **it has one implementation.** A
domain must not write its own target parser.

## Whether the driver is in the URL

A tool implements most domains. `package` runs apt, `ntp` runs chrony,
`container` runs Docker, and `schedule` writes crontab entries. One question
decides if the tool is in the URL.

**Does the caller select it, or does the host?**

A caller selects a container runtime. A person decided to run Docker and not
Podman, and wants to address it directly. Thus the runtime is a path segment:
`/container/docker`. Podman adds `/container/podman` next to it, and the two can
exist on one host.

A caller does not select a package manager. The host already decided. A request
to a fleet to install a package cannot depend on which hosts run apt. Thus the
tool is not in the URL. The path is `/package`, and the provider selects apt or
a different tool by OS family.

`/ntp` is the same. chrony is behind it now, and a different driver can use the
same entry point later. `/schedule` is also the same. It uses cron now, and
possibly `at` later. The caller does not need to know which.

An error in either direction has a real cost:

- If the URL has a tool that the caller did not select, a call to the full fleet
  is not possible.
- If the URL does not have a tool that the caller did select, the caller cannot
  address two runtimes on one host.

## Each layer takes the name from the URL it serves

After you decide the URL, no layer below it invents a name.

| Layer                 | Takes its name from | `/container/docker`      | `/network/dns`         |
| --------------------- | ------------------- | ------------------------ | ---------------------- |
| API handler directory | the first segment   | `api/node/container/`    | `api/node/network/`    |
| API handler files     | the second segment  | `docker_create.go`       | `dns_get.go`           |
| agent processor       | the first segment   | `processor_container.go` | `processor_network.go` |
| SDK service           | the last segment    | `client/docker.go`       | `client/dns.go`        |
| CLI command           | the path            | `node container docker`  | `node network dns`     |

The API layer is flat. A domain gets one directory with the name of the first
segment. The second segment is a filename prefix in that directory, not a
subdirectory.

The provider tree is the exception, and this is deliberate. It nests by what
implements a thing. Thus a second driver is a new directory next to the first,
not a set of files in many places: `provider/container/docker` and, when it
exists, `provider/container/podman`. Thus that tree can be deeper than the URL.
For example, `provider/network/netplan/dns` serves `/network/dns`.

## Broadcast is not optional

Each operation under `/node/{hostname}/...` supports broadcast targets, and
**the two paths return the same collection shape.** A single target returns one
result. A broadcast returns one result for each agent. Each result item has
`hostname` and `error`.

Thus a caller writes one parser, not two. A partial failure is a row, not an
exception.

## The job client needs nothing added

`JobClient` has four generic methods: `Query`, `QueryBroadcast`, `Modify` and
`ModifyBroadcast`. A new operation adds **none**. A handler gives a category
string and an operation constant. It does not call a method for each operation.

## Wiring

A domain package exports `Handler()`, which returns route-registration closures.
The package wraps the handler in scope middleware itself. **The `Server` struct
does not change.** The startup wiring is one added line in
`registerControllerHandlers` in `cmd/controller_setup.go`.

On the agent side, two files connect a provider: a processor under
`internal/agent/`, and the registration in `cmd/agent_setup.go`. These do
**not** change: `agent/types.go`, `agent/agent.go` and the `JobClient`
interface. The registry handles the dispatch and the facts.

## Permissions

[Permissions](permissions.md) tells how to select one, in one sentence about the
possible damage. This page has the mechanics.

You must add a new permission in four places. [Permissions](permissions.md)
tells the cost if you forget each one. **If a permission is in the specification
and in no role, nobody gets it**, and nothing reports it.

## One name, and it is the URL's

A domain has the same name in its provider directory, its agent processor, its
URL segment, its SDK service and its CLI command. The URL decides that name. A
consumer depends on the URL, and you cannot change the URL without a major
version.

The name is the concept, never the tool that implements it. A container domain
is `container`, with a Docker implementation in it. The NTP domain is `ntp`,
with a chrony implementation in it. If you name the directory `docker`, the name
becomes untrue when osapi supports a second runtime. A rename then is the
expensive form of this change.

Abbreviations are also not names. Use `memory`, not `mem`.

Two shapes can break the one-to-one mapping, because they are real and not
accidental:

- A provider can serve more than one URL segment, when it collects facts that
  are really separate resources. The host provider answers `hostname`, `os` and
  `uptime`. One endpoint for all three is worse.
- More than one provider can serve one URL segment, when they implement one
  concept. The providers for interfaces, routes and reachability serve
  `network`.

The same concept with a different name in each layer is not permitted. The only
check for completeness across layers is a search for the name of a domain. That
check cannot work if the name changes between layers.

## What a domain's tests owe

If nothing tests a declared rule, nobody knows when it breaks. The specification
has the validation tags. The generator changes them into struct tags.
`validation.Struct()` runs them. Nothing in that chain fails clearly if a tag is
lost. Thus the tests must hold it.

**Prove that validation runs, not only that it exists.** Each endpoint gets a
`TestXxxValidationHTTP`. It sends a request through the full middleware stack
with a missing or malformed field. It asserts 400, and it asserts that the body
names the rule that refused the request. The name of the rule is the important
part. A test that asserts only the status code also passes when the handler
refuses for a different reason.

```go
name: "when missing key returns 400",
body: `{"value":"1"}`,
    s.Contains(rec.Body.String(), "Key")

name: "when target agent not found",
    s.Contains(rec.Body.String(), "valid_target")
```

**Prove the permission in three ways.** Each endpoint has a `TestXxxRBACHTTP`:

- no token gives 401
- a token without the permission gives 403
- a token with the permission succeeds

The third case finds a permission with a different spelling in the specification
and in the table.

**Each status that the specification declares has a path through the tests.** A
declared 404 that nothing makes is an undocumented operation or an error in the
specification. Both are worth finding.

**A broadcast returns the same shape for one host and for forty.** Assert the
collection in the two directions, because code often has a special case for a
single host.

**The integration tests cover what unit tests cannot.** The coverage gate does
not include `cmd/`. Thus only `test/integration/{domain}_test.go`, against a
real binary, runs the path from CLI flag to HTTP request to agent.

A measurement in October 2026 found 75 validation suites and 80 RBAC suites in
the domains. 21 of 22 domains have an integration test. The exceptions are on a
list of gaps. They are not accepted.

## A domain is in every layer, or it is not done

A domain is not one artifact. It has these parts:

- a provider
- an agent processor and its registration
- a spec and the code generated from it
- a handler and its route
- an SDK service
- CLI commands
- the documentation pages and permission tables that name it

If one part is missing, the domain is not smaller. It works until somebody uses
the missing layer. Then the gap shows as a bug, not as a missing part.

To check, select a finished domain and search the repository for its name. Then
do the same search for the new domain. The two lists must have the same shape. A
name in eighty files and a name in sixty files is the answer.

```bash
grep -rl 'sysctl\|Sysctl' --include='*.go' --include='*.yaml' --include='*.md' . \
  | grep -vE '/gen/|/node_modules/|docs/docs/gen'
```

## Where this connects

[Providers](providers.md) tells what the new provider must implement, and the
three boundary rules that it must obey.

[The job system](job-system.md) has the delivery rules, the two clocks and the
four result statuses.

[The embedded UI](ui.md) has the generated client that the combined
specification also supplies.

______________________________________________________________________

Written from `internal/controller/api/` and `cfg.yaml`.
