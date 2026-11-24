# The Go SDK

`pkg/sdk` is the public SDK of osapi: each package that code outside the osapi
repository imports. The client is one part of it:

```
pkg/sdk/
  client/      calls the API over HTTP
  types/       the shared vocabulary: the job states, the permissions and roles,
               the error reasons, the content types, the admission states,
               Step, the targets
  extension/   later: what an extension imports to register itself (osapi#1319)
```

`go-pkg-check` fails when a package of `pkg/` imports `internal/`, and when
`pkg/sdk/types` imports any other package of osapi. Thus osapi's own packages,
the client and an extension can each import `types`, and each value has one
definition.

## The shared vocabulary

`pkg/sdk/types` holds the words that cross the API: `JobStatus` (the status of a
job), `AgentJobStatus` (the status of a job on one host), the agent states and
conditions, `Permission`, `Role` and the `Perm` constants, `Reason`,
`ContentType`, `AdmissionState`, `Step`, `JobType`, the job operations, and
`TargetAny` and `TargetAll`. osapi's packages use the type from `types`, not a
copy. A closed set, such as `ContentType`, `Reason`, `AgentJobStatus` or
`Permission`, has the methods `Values()` and `Valid()`. Thus the spec has a
schema with its values, and the rule `validate:"enum"` calls `Valid()`. `Role`
has no `Values()`, because the config can add custom roles. A generator writes
only `permissions.gen.go`, from the registry of permissions.

Before osapi-io/osapi#1318, these types were in `pkg/sdk/client`, and
`internal/job` and the catalog endpoint imported them from the client. The
client is not their owner, and an extension that only registers a behavior does
not call the API.

## The client

`pkg/sdk/client` is the public API of osapi for programs that call it.
`internal/sdk/gen` writes its typed services and their types from the full spec
of the API. A small layer that a person writes sends the requests and makes the
errors. It is the contract that
[osapi-orchestrator](../osapi-orchestrator/README.md) depends on.

It has 40 services and 123 generated methods. Each group of the API is a
service, and each operation of the spec is a method.

## How it is made

`just sdk-generate` runs `internal/sdk/gen`, after `go generate` writes the full
spec in `internal/behaviors/all`. Thus `just generate` makes the spec and the
SDK in one run, and `sdk-gen-check` fails on a stale file of the SDK, its
examples or its pages.

The generator is not a `go:generate` directive. `go generate` lists the files of
each package before it runs any directive, so a run that removed the file of a
group that is gone made `go generate` fail on that file, and only a second run
passed (osapi-io/osapi#1261).

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

**The rule for generated code.** Generated code that a caller imports is in the
package that the caller imports, as a `*.gen.go` file. `gen/` is for generated
code that no caller imports, such as the routes of a behavior. A schema of the
spec that `pkg/sdk/types` declares is not written again: the generator reads the
types of `pkg/sdk/types` and writes a reference, such as `types.Step`. The
schema and the Go type must agree. The generator compares the properties of an
object schema with the JSON names of the fields of the struct. It compares the
values of an enum with the constants of the type. If they are different, or if
only one of the two is a struct, the generator stops with an error and writes no
file (osapi-io/osapi#1335). Before that check, the generator used only the name
to bind a schema to a type of `pkg/sdk/types`. For each other enum of the spec,
it writes the type and a constant for each value, such as
`NetworkInterfaceResponseFamilyInet`. A hand-written file in `pkg/sdk/client` is
plumbing that each method uses, or a method that the generator cannot write.

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

| Name    | From                                                   | Example                                 |
| ------- | ------------------------------------------------------ | --------------------------------------- |
| service | the words of the group's path, to the group's own word | `PackageUpdates` for `/package/updates` |
| method  | the operation's `x-osapi-method` extension             | `Get`, `Drain`, `Liveness`              |
| type    | the schema of an answer                                | `DnsEntry`                              |
| input   | the service and the method                             | `DNSUpdateInput`                        |
| field   | the property, with Go initialisms                      | `SearchDomains`, `JobID`, `Min15`       |

The endpoint layer writes `x-osapi-method` on each operation: the name of the
method in the definition of its group or behavior. It writes `x-osapi-group` on
each tag: the name of the group, which is the word of the path that the service
name stops at. The name of the tag for a person, `x-displayName`, is the title
of the behavior, such as "Package updates". Thus the service name does not come
from that title. The CLI command has the same name. Thus
`osapi client node dns get` is `c.DNS.Get`. To change a name, change it in the
definition.

A group of a node that has the name of a group of the controller gets `Node` in
front: the file behavior is `NodeFile`, next to `File`, the Object Store.

This replaces the five naming rules and the seven renames that this page had
before. Those rules came from the methods that people wrote. Some generated
names differ: `Health.GetLiveness` is `Health.Liveness` again, and
`Docker.RemoveImage` is `Image.Delete`. The definition is the one place that
names an operation, and nobody else uses the SDK, so the change has no shim.

## Every method has the same shape

A method with a JSON body takes `ctx`, the target `hostname`, and one input
struct, `<Service><Method>Input`. The input has a field for each other key of
the path, with the `json` tag `-`, then a field for each property of the body.

```go
func (s *DNSService) Update(
    ctx context.Context,
    hostname string,
    input DNSUpdateInput,
) (*Response[Collection[DnsResult]], error)
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

An enum of the spec is a named string type with a constant for each value, so a
caller does not type a value as a string. A schema that is a string with an
enum, such as `OperationID`, is `type OperationID string`. An enum that a
property or a query parameter defines inline is a named type too, with the name
that the generator of the UI gives it (osapi-io/osapi#1329):

- `<Schema><Property>` for a property, such as `NetworkInterfaceResponseFamily`;
- `<operationId><Parameter>` for a parameter of the query, such as
  `GetJobsStatus`;
- `<Schema><Property>Item` for an item of an inline list, such as
  `JobDetailResponseTimelineItem`.

A constant is the type's name and the value, such as
`NetworkInterfaceResponseFamilyInet`. A field that refers to a named enum schema
does not list the values in its comment, because the type has them. A field
whose enum is inline still lists them, such as
`Family NetworkInterfaceResponseFamily` (It is one of: inet, inet6, dual). The
page of each type lists them. A closed set of Go, a type with `Values()`, makes
the named schemas ([Endpoints](endpoints.md#the-definition)).

A type that `pkg/sdk/types` declares is not written again: the client refers to
it. `types.Permission` is one, so the `Permission` schema of the catalog uses
it. `types.AgentState` and `types.ConditionType` are others, so `AgentInfo` has
a `types.AgentState` and `NodeCondition` has a `types.ConditionType`
(osapi-io/osapi#1332). `types.Step` has a `*bool` `Changed`, because a step of a
method with no changed field leaves it out. osapi's own job code uses that type.

## The examples and the pages are generated

A behavior and an endpoint group declare each example as the flags of its CLI
command, such as `--target web-01 --interface-name eth0`. The endpoint layer
reads the flags of each example into the input of the command: the parameters of
the path and the query, and the properties of the body. It writes the inputs in
the `x-osapi-examples` extension of the operation, each with its doc. An example
with no doc gets the summary of the method. Two examples with the same input are
one example. The file of a multipart form, such as an upload, is the path that
its flag names.

The same `go generate` run writes a program for each service,
`examples/sdk/client/<service>.go`. The program has a function for each example,
which calls the method with the input of the example and prints the answer as
JSON. Give the name of an example to run it, such as `go run dns.go update`. The
target of a node is `OSAPI_TARGET`, `_any` by default, not the host of the
example. `examples-check` compiles each program.

A method that sends a multipart form is written by hand, but its examples are
generated. The program reads the file with `os.ReadFile`, then calls the method
with the arguments in a fixed order: the keys of the path, the required fields
of the form, the optional fields, and then the file as an `io.Reader`. Each part
is in the order of the field names. A field that an example does not set gets
its default from the spec. Thus the person who writes the method must use this
order. `examples-check` fails when the method has a different one. Before
osapi-io/osapi#1294, a person wrote `examples/sdk/client/file_upload.go`, and
nothing reported when it went stale.

`just sdk-docs-generate` writes a page for each service under
`docs/docs/sidebar/sdk`, in the folder of its area, such as `fleet/agent.md`.
The service gets the `x-osapi-area` of its operations, and the generator fails
when the operations of one service have two areas. It writes a `_category_.json`
for each area that has a service, with the label and the order from
`x-osapi-areas`. Thus the folders have the labels and the order of the tabs of
the UI ([areas](endpoints.md#areas)). A method that takes a host shows it in its
signature. The generator writes a table of the services of each area in
`library/client.md`, between the `osapi:sdk-services` markers. It removes a page
that it wrote before when its service is gone, and the `_category_.json` and the
folder of an area that has no service now. A page has each method that the
source of the SDK declares for the service: its signature, its doc comment and
the permission from the spec. Then it has the code of each example and the
types. A method that a person wrote is on the page too, with its doc comment.

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
caller's side and calls no operation of its own, so it has no example. The
vocabulary is in `pkg/sdk/types`, not in the client. Each program under
`examples/sdk/client/` is generated.

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
