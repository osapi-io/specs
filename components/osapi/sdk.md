# The Go SDK

`pkg/sdk/client` is the public API of osapi for programs. It comes from the
combined OpenAPI specification, and hand-written services wrap it. It is the
contract that [osapi-orchestrator](../osapi-orchestrator/README.md) depends on.

It has 32 services and 119 exported methods. The `Client` struct has one field
for each service.

## What a service owes

A service needs five things. A domain is not complete until all five exist.

| Artifact                       | Where                      |
| ------------------------------ | -------------------------- |
| four files per service         | `pkg/sdk/client/`          |
| a field on the `Client` struct | `pkg/sdk/client/client.go` |
| a runnable example             | `examples/sdk/client/`     |
| a documentation page           | the matching site category |
| a navbar entry                 | the site config            |

## Method naming

There are five rules. They **come from the methods that already exist**. Nobody
invented them, because nobody wrote a convention before. The document that found
them said 110 methods. The count is now 118. The rules come from the full set in
each case.

**1. The five CRUD verbs are exactly `List`, `Get`, `Create`, `Update`,
`Delete`.** For the resource of the service, never use `GetAll`, `Fetch`, `Set`,
`Put` or `Remove`. Eleven services use some or all of them, and none is
different.

**2. A method on the resource of the service uses only the verb, with no
object.** `Service.Start`, not `Service.StartService`. Also `Power.Reboot`,
`Agent.Accept`, `Job.Retry`, `Package.Install`, `Docker.Pull`.

**3. A method on a sub-resource uses the verb, then the object.** `User.AddKey`,
`User.ListKeys`, `User.RemoveKey`, `User.ChangePassword`, `Agent.ListPending`,
`Package.ListUpdates`, `Log.QueryUnit`.

**4. A single getter has the name `Get` and no other name.** Six services have
one read each: `Disk`, `Load`, `Memory`, `OS`, `Status` and `Uptime`. Each names
it `Get`. The service gives the subject.

**5. When a service has more than one read, each uses the verb, then the
object.** The `Get` of rule 4 applies only when there is exactly one read.

`Docker.Pull` is deliberately **not** `PullImage`. `PullImage` is more
symmetrical with `RemoveImage`. But in Docker, pull applies only to images. Thus
the object makes the name longer, and it does not make it more clear.

## Seven methods do not conform, and are to be renamed

These are not permitted exceptions. They get new names.

| Current              | Becomes             | Which rule                                                                    |
| -------------------- | ------------------- | ----------------------------------------------------------------------------- |
| `Docker.ImageRemove` | `RemoveImage`       | 3. The only object-then-verb method in the SDK                                |
| `Ping.Do`            | `Connectivity.Ping` | 2. `Do` names no action; the behavior names the service (osapi-io/osapi#1110) |
| `File.Stale`         | `ListStale`         | 3. Returns `StaleList`, a list of a sub-resource                              |
| `File.Changed`       | `GetChanged`        | 3. Returns `FileChanged` for a path                                           |
| `Health.Liveness`    | `GetLiveness`       | 5. Three distinct reads on one service                                        |
| `Health.Ready`       | `GetReady`          | 5.                                                                            |
| `Health.Status`      | `GetStatus`         | 5.                                                                            |

**Why a rename and not an exception.** The cost of a rename becomes larger with
each release. osapi has released tags, and the orchestrator pins one. Thus each
rename is now a breaking change for the next pin update. There are twenty-six
call sites here and three in the orchestrator, and that number only increases.

## How the package is laid out

There is one file for each domain service, and four files that are not a
service.

```
pkg/sdk/client/
  gen/            generated from the combined specification, never edited
  osapi.go        the constructor and the service wiring
  response.go     Response[T], Collection[T], the error helpers
  errors.go       the typed error hierarchy
  <domain>.go     one per service: its methods
  <domain>_types.go   its result types, and the conversions from gen
```

The split between `<domain>.go` and `<domain>_types.go` keeps the conversion
from generated types in one location for each domain. A service that returns a
generated type directly did not make that file. The rule below forbids that.

`pkg/sdk/` had the orchestrator engine before. The engine is now in the
`internal/engine/` of [osapi-orchestrator](../osapi-orchestrator/README.md). It
is the only thing that ever left this package.

## Every method returns the same envelope

```go
type Response[T any] struct {
    Data    T
    rawJSON []byte
}
```

`Data` is the typed result. `RawJSON()` is the response body as it came. It
exists for one caller: the `--json` mode of the CLI. That mode must print what
the server said, not what the SDK parsed.

Thus a method cannot return a bare value, also where a bare value is sufficient.
The envelope makes `--json` possible without a second code path. A collection
returns `Response[Collection[T]]`, not `Response[[]T]`.
[Building a domain](domains.md) gives the same reason for the shape that a
broadcast returns.

## The SDK knows routes, not behaviors

The SDK connects to the HTTP API. Thus it needs the spec, never the Go
definition of a [behavior](behaviors.md). `pkg/sdk` imports nothing from
`internal/`. For a route with no typed method, use one generic call:

```go
resp, err := c.Request(ctx, http.MethodGet, "/api/node/_all/sysctl/vm.swappiness", nil)
```

It returns the body as the API sent it. An answer outside 2xx becomes the same
error types that each typed method returns. The generated commands of osapi call
it, through the CLI runtime that makes the path of a behavior from its
definition.

Before the cutover of a behavior, its routes have no typed SDK method. After the
cutover, its spec joins the main spec. Thus the client that oapi-codegen
generates covers it like each other domain. Then the typed services above can
come from the spec, and nobody needs to write them by hand.

## The rest of the conventions

**Type exposure, JSON tags on result fields, and error wrapping.** The SDK
guidelines page of the site states these, and shows each one in use. An example
of a rule in use is not a second statement of the rule. Thus this page links to
them and does not repeat them.

## Where this connects

[Building a domain](domains.md) tells what generates the specification of the
SDK. It also tells why the SDK cannot see a domain that is not in the combined
file.

The client of the UI comes from **the same** combined specification, through a
different generator. [The embedded UI](ui.md) describes it.

______________________________________________________________________

Written from `pkg/sdk/client/`.
