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

The same model makes the examples and the reference pages of the SDK. Thus the
code, the pages and the examples cannot name a method in two ways.

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
method in the definition of its group or behavior. It writes `x-osapi-group` on
each tag: the name of the group, which is the word of the path that the service
name stops at. The name of the tag for a person, `x-displayName`, is the title
of the behavior, such as "Package updates". Thus the service name does not come
from that title. The CLI command has the same name. Thus
`osapi client node network dns get` is `c.NetworkDNS.Get`. To change a name,
change it in the definition.

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
input of the behavior and the flags of its command. Thus the generator writes
each example of a behavior as an SDK call, field by field.

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

## The examples and the pages are generated

A behavior and an endpoint group declare each example as the flags of its CLI
command, such as `--target web-01 --interface-name eth0`. The endpoint layer
reads the flags of each example into the input of the command: the parameters of
the path and the query, and the properties of the body. It writes the inputs in
the `x-osapi-examples` extension of the operation, each with its doc. An example
with no doc gets the summary of the method. Two examples with the same input are
one example. An upload has no example in the spec, because the SDK has no
generated method for a multipart form.

The same `go generate` run writes a program for each service,
`examples/sdk/client/<service>.go`. The program has a function for each example,
which calls the method with the input of the example and prints the answer as
JSON. Give the name of an example to run it, such as
`go run network_dns.go update`. The target of a node is `OSAPI_TARGET`, `_any`
by default, not the host of the example. `examples-check` compiles each program.

`just sdk-docs-generate` writes a page for each service under
`docs/docs/sidebar/sdk/client`, in the folder of its area, such as
`fleet/agent.md`. The service gets the `x-osapi-area` of its operations, and the
generator fails when the operations of one service have two areas. It writes a
`_category_.json` for each area that has a service, with the label and the order
from `x-osapi-areas`. Thus the folders have the labels and the order of the tabs
of the UI ([areas](endpoints.md#areas)). A method that takes a host shows it in
its signature. The generator writes a table of the services of each area in
`client.md`, between the `osapi:sdk-services` markers. It removes a page that it
wrote before when its service is gone, and the `_category_.json` and the folder
of an area that has no service now. A page has each method that the source of
the SDK declares for the service: its signature, its doc comment and the
permission from the spec. Then it has the code of each example and the types. A
method that a person wrote is on the page too, with its doc comment.

`sdk-gen-check` writes the programs and the pages again, and fails when one
changed. Before osapi-io/osapi#1013 and osapi-io/osapi#1008, a person wrote 32
programs and 34 pages. The pages listed a `Create` method that the job service
did not have, and gave the status read the permission `node:read`, not
`status:read`. The DNS page linked a program that did not exist.

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
in their own files. `examples/sdk/client/file_upload.go` is the one program that
a person writes: it calls the three methods of the file service that the
generator does not write. The page of the file service links it.

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
spec, through a different generator. [The embedded UI](ui.md) describes it.
[The docs site](docs-site.md) tells which pages of the site are generated.

______________________________________________________________________

Written from `internal/sdk/gen/` and `pkg/sdk/client/`.
