# The Go SDK

`pkg/sdk/client` is osapi's public API for programs. It is generated from the
combined OpenAPI specification, wrapped in hand-written services, and it is the
contract [osapi-orchestrator](../osapi-orchestrator/README.md) depends on.

31 services, 117 exported methods, one field per service on the `Client` struct.

```sh
grep -hcE '^type [A-Za-z]+Service struct' pkg/sdk/client/*.go | paste -sd+ - | bc  # 31
grep -hE '^func \(s \*[A-Za-z]+Service\)' pkg/sdk/client/*.go | wc -l            # 117
```

## What a service owes

Five things, and a domain is not finished until all five exist.

| Artifact                       | Where                      |
| ------------------------------ | -------------------------- |
| four files per service         | `pkg/sdk/client/`          |
| a field on the `Client` struct | `pkg/sdk/client/client.go` |
| a runnable example             | `examples/sdk/client/`     |
| a documentation page           | the matching site category |
| a navbar entry                 | the site config            |

## Method naming

Five rules. They were **derived from the methods that already exist** rather
than decided in the abstract, because no convention had ever been written down.
The document that derived them said 110; the count is 117, and the rules were
read off the whole set either way.

**1. The five CRUD verbs are exactly `List`, `Get`, `Create`, `Update`,
`Delete`.** Never `GetAll`, `Fetch`, `Set`, `Put` or `Remove` for the service's
own resource. Eleven services use some or all of them and none deviates.

**2. A method acting on the service's own resource takes the bare verb, no
object.** `Service.Start`, not `Service.StartService`. Also `Power.Reboot`,
`Agent.Accept`, `Job.Retry`, `Package.Install`, `Docker.Pull`.

**3. A method acting on a sub-resource takes verb then object.** `User.AddKey`,
`User.ListKeys`, `User.RemoveKey`, `User.ChangePassword`, `Agent.ListPending`,
`Package.ListUpdates`, `Log.QueryUnit`.

**4. A single getter is named `Get` and nothing else.** Six services expose one
read each, `Disk`, `Load`, `Memory`, `OS`, `Status` and `Uptime`, and each names
it `Get`, taking its subject from the service.

**5. Where a service exposes several distinct reads, each takes verb then
object.** Rule 4's bare `Get` applies only where there is exactly one read.

`Docker.Pull` is deliberately **not** `PullImage`. It would be more symmetric
with `RemoveImage`, but pull applies to nothing but images in Docker, so the
object adds length without removing ambiguity.

## Seven methods do not conform, and are to be renamed

Not recorded as permitted exceptions. Renamed.

| Current              | Becomes       | Which rule                                         |
| -------------------- | ------------- | -------------------------------------------------- |
| `Docker.ImageRemove` | `RemoveImage` | 3. The only object-then-verb method in the SDK     |
| `Ping.Do`            | `Send`        | 2. `Do` names no action; `Ping.Ping` would stutter |
| `File.Stale`         | `ListStale`   | 3. Returns `StaleList`, a list of a sub-resource   |
| `File.Changed`       | `GetChanged`  | 3. Returns `FileChanged` for a path                |
| `Health.Liveness`    | `GetLiveness` | 5. Three distinct reads on one service             |
| `Health.Ready`       | `GetReady`    | 5.                                                 |
| `Health.Status`      | `GetStatus`   | 5.                                                 |

**Why renaming rather than excepting.** The SDK has no released version. osapi
carries no `v*` tag and the orchestrator pins a pseudo-version commit, so these
are renames today and breaking changes after the first tag. Twenty-six call
sites here and three there is the whole cost, and it only grows.

## How the package is laid out

One file per domain service, and four files that are not a service.

```
pkg/sdk/client/
  gen/            generated from the combined specification, never edited
  osapi.go        the constructor and the service wiring
  response.go     Response[T], Collection[T], the error helpers
  errors.go       the typed error hierarchy
  <domain>.go     one per service: its methods
  <domain>_types.go   its result types, and the conversions from gen
pkg/sdk/platform/   platform detection, not a service
```

The split between `<domain>.go` and `<domain>_types.go` is what keeps the
conversion from generated types in one place per domain. A service that returns
a generated type directly has skipped that file, which is the rule below.

`pkg/sdk/` held the orchestrator engine once. It now lives in
[osapi-orchestrator](../osapi-orchestrator/README.md)'s `internal/engine/`, and
that is the only thing that has ever left this package.

## Every method returns the same envelope

```go
type Response[T any] struct {
    Data    T
    rawJSON []byte
}
```

`Data` is the typed result. `RawJSON()` is the response body as it arrived, and
it exists for one caller: the CLI's `--json` mode, which has to print what the
server said rather than what the SDK parsed.

So a method cannot return a bare value even where a bare value would do, because
the envelope is what makes `--json` possible without a second code path. A
collection returns `Response[Collection[T]]` rather than `Response[[]T]`, which
is the same reason stated for the shape a broadcast returns in
[building a domain](domains.md).

## The rest of the conventions

**Type exposure, JSON tags on result fields, and error wrapping** are stated
where the site's SDK guidelines page demonstrates each one working. Showing a
rule working is not stating it twice, so those are cited rather than repeated
here.

## What was deferred to nothing

Worth keeping, because it is the failure mode that produced this document.

Three separate documents said the same thing: the site's SDK guidelines page,
the domain-building page, and the `add-a-domain` skill's SDK reference. All
three said that method naming, type exposure, result-field tags and error
handling "are specified in the `sdk-standards` capability in osapi-io/specs",
and that where the two disagree the specification wins.

**There is no `sdk-standards` capability.** There never was. Three documents
deferred to an authority nobody had written, which reads as settled and is not.

Of its four named subjects, three were real and stated elsewhere. **Method
naming was stated nowhere at all.** Not in those pages, whose sections are
package structure, generated types, result types, the response pattern and error
handling. Not in the capability that does not exist. It was named only in the
deferral.

So the missing authority was not a document that would have collected existing
rules. For one of its four subjects there was nothing to collect, which is why
the five rules above had to be derived from the code.

## Where this connects

What generates the specification the SDK is built from, and why a domain absent
from the combined file is invisible to it, is [building a domain](domains.md).

The UI's client is generated from **the same** combined specification, by a
different generator, and is [the embedded UI](ui.md).

______________________________________________________________________

Traced to `../../history/osapi-005-building-a-domain/`, which derived the naming
rules from the existing surface after establishing that no convention had been
written down.
