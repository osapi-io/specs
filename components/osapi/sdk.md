# The Go SDK

`pkg/sdk/client` is the public API of osapi for programs. `internal/sdk/gen`
writes its typed services and their types from the full spec of the API. A small
layer that a person writes sends the requests and makes the errors. It is the
contract that [osapi-orchestrator](../osapi-orchestrator/README.md) depends on.

It has 40 services and 123 generated methods. Each group of the API is a
service, and each operation of the spec is a method.

## How it is made

`go generate` runs `internal/sdk/gen` in `pkg/sdk/client`, after it writes the
full spec in `internal/behaviors/all`. Thus `just generate` makes the spec and
the SDK in one run, and `go-generate-check` fails on a stale file.

The generator reads the spec into a model, `internal/sdk/gen/sdkmodel`: each
service, its methods with their parameters, body and result, and each type. It
writes the model to Go with jen:

```
pkg/sdk/client/
  <service>.gen.go         the service, its methods, the struct of its query
  <service>_types.gen.go   the types that only that service has
  types.gen.go             the types that more than one service has
  services.gen.go          the struct of the services, which Client embeds
  osapi.go, transport.go   by hand: New, the options, the token
  request.go               by hand: Send, Request, and send, which each method calls
  response.go              by hand: Response[T]
  collection.go            by hand: Collection[T]
  errors.go, check_error.go   by hand: the error types
  file_upload.go           by hand: the multipart upload of a file
```

The SDK does not use oapi-codegen. Before osapi#732, oapi-codegen wrote a client
in `pkg/sdk/client/gen`, and 32 hand-written services copied each of its types
into an SDK type, a pointer at a time. An audit on 21 November 2026 found four
operations with no method, and 18 methods that dropped the 404 of the spec. A
generated method cannot miss an operation, and each status goes through one
function. `spec-client-check` still builds a client that oapi-codegen writes
from the spec, in a module of its own, as a person outside osapi would.

The model is the hook for the next two generators: the reference pages of the
SDK (osapi-io/osapi#1008) and its examples from the examples of each behavior
(osapi-io/osapi#1013). Each reads the same model. Thus the code, the pages and
the examples cannot name a method in two ways.

## Names come from the spec

The generator keeps no list of names. It takes each one from the spec:

| Name    | From                                                   | Example                           |
| ------- | ------------------------------------------------------ | --------------------------------- |
| service | the words of the group's path, to the group's own word | `NetworkDNS` for `/network/dns`   |
| method  | the operation's `x-osapi-method` extension             | `Get`, `Drain`, `Liveness`        |
| type    | the schema of an answer                                | `NetworkDnsEntry`                 |
| input   | the service and the method                             | `NetworkDNSUpdateInput`           |
| field   | the property, with Go initialisms                      | `SearchDomains`, `JobID`, `Min15` |

The endpoint layer writes `x-osapi-method` on each operation: the name of the
method in the definition of its group or behavior. The CLI command has the same
name. Thus `osapi client node network dns get` is `c.NetworkDNS.Get`. To change
a name, change it in the definition.

A group of a node that has the name of a group of the controller gets `Node` in
front: the file behavior is `NodeFile`, next to `File`, the Object Store.

This replaces the five naming rules and the seven renames that this page had
before. Those rules came from the methods that people wrote. Some generated
names differ: `Health.GetLiveness` is `Health.Liveness` again, and
`Docker.RemoveImage` is `ContainerImage.Delete`. The definition is the one place
that names an operation, and nobody else uses the SDK, so the change has no
shim.

## Every method has the same shape

A method with a JSON body takes `ctx`, the target `hostname`, and one input
struct, `<Service><Method>Input`. The input has a field for each other key of
the path, with the `json` tag `-`, then a field for each property of the body.

```go
func (s *NetworkDNSService) Update(
    ctx context.Context,
    hostname string,
    input NetworkDNSUpdateInput,
) (*Response[Collection[NetworkDnsResult]], error)
```

One struct, not a list of arguments, because a write has many optional fields
and a call must not depend on their order. The input has the same fields as the
input of the behavior and the flags of its command. Thus an example of a
behavior can become an SDK call field by field (osapi-io/osapi#1013).

A method with no body takes `ctx`, then each parameter of the path, then each
parameter of the query that the request must have, then `params`: a struct of
the parameters of the query that a request can leave out.

It returns `*Response[T]`. `Data` is the typed result. `RawJSON()` is the body
as it came, for the `--json` mode of the CLI, which must print what the server
said. A `{job_id, results}` answer is `Collection[T]` of its item, so one host
and a broadcast have one shape.
[Behaviors](behaviors.md#how-a-behavior-is-served) gives the reason for that
envelope. An answer with no body, such as a 204, returns only `error`.

## Types are values

A type has a field for each property, with a `json` tag. A property that the
schema does not require has `omitempty`, or `omitzero` for a struct or a time. A
field is a value, not a pointer. The server decodes a property that is not in
the request as its zero value, so a pointer cannot send more than a value can. A
`uuid` is a `string`, and a `date-time` is a `time.Time`.

The method decodes the body of the answer straight into the type. There is no
copy from a second type.

A type that a person wrote in the package wins: the generator does not write a
type with its name. `Step`, in `job_steps.go`, has a `*bool` `Changed`, because
a step of a method with no changed field leaves it out. osapi's own job code
uses that type.

## Errors

Each method sends through `Client.Send`. An answer outside 2xx becomes a typed
error, with the message and the reason of its body: 400 is a `ValidationError`,
401 and 403 an `AuthError`, 404 a `NotFoundError`, 409 a `ConflictError` and 500
a `ServerError`. Any other status is an `UnexpectedStatusError`. A body that
does not decode into the method's type is an error that names the method and the
path.

## What is still written by hand

`File.Upload` and `File.Update` send a multipart form, and the generator writes
a method only for a JSON body. `File.GetChanged` compares a SHA-256 on the
caller's side and calls no operation of its own. Constants that osapi's own
packages use, such as the job states, the content types and the permissions, are
in their own files.

The SDK imports nothing from `internal/`. `go-pkg-check` fails when it does. For
a route with no typed method, use the generic call:

```go
resp, err := c.Request(ctx, http.MethodGet, "/api/node/_all/sysctl/vm.swappiness", nil)
```

It returns the body as the API sent it, with the same error types. The generated
commands of the CLI call it, through the CLI runtime that makes the path of a
behavior from its definition.

## Coverage

The hand-written files have 100% coverage. `.coverignore` leaves out each
`*.gen.go` file. `send_public_test.go` sends a request through a generated
method of each shape: a parameter of the path, a body, a query, and an answer
with no body. The model and the generator have their own tests.

## Where this connects

[Endpoints](endpoints.md#the-full-spec) tells what writes the full spec, and the
checks that hold it to the server. The client of the UI comes from the same
spec, through a different generator. [The embedded UI](ui.md) describes it. The
SDK pages of the site are still written by hand: [the docs site](docs-site.md)
tracks them.

______________________________________________________________________

Written from `internal/sdk/gen/` and `pkg/sdk/client/`.
