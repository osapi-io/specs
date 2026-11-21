# Endpoints

A plan, partly built. Each group of the controller is served, and its CLI
commands are made, from its definition: its spec, routes, decoders and commands
are generated, and its handlers are typed functions. The part that is not built
is [behaviors on endpoints](#behaviors-on-endpoints), osapi#826. An endpoint is
one HTTP operation of the controller itself, such as `GET /api/agent` or
`POST /api/job/{id}/retry`. Its definition is Go. The route, the part of the
OpenAPI spec, the CLI command, its page, the permission and the HTTP tests come
from that definition, as they come from the definition of a
[behavior](behaviors.md). Thus no part of the API uses a spec that a person
writes.

The issue is osapi#744.

## Why

The controller has 25 operations, in seven groups. A person wrote each one four
times: the spec, the handler, the service of the SDK and the CLI command. Each
one comes from a definition now: agent (8), telemetry (1), audit (3), job (4),
facts (1), health (3) and file (6).

A new operation of the controller had no generator. Behaviors cover the work on
a host, and nothing covered the work on the controller.

## An endpoint and a behavior

|                       | Endpoint                                                                            | Behavior                               |
| --------------------- | ----------------------------------------------------------------------------------- | -------------------------------------- |
| Where the work occurs | on the controller, in the request                                                   | on each target host, as a job          |
| Target                | none                                                                                | a hostname, a label, `_all` or `_any`  |
| Response              | an object or a list, with totals                                                    | one result for each host               |
| What it uses          | the job client, the KV buckets, the object store, the audit store, the trace reader | the host: its filesystem, its commands |
| Who adds one          | a contributor to osapi                                                              | a contributor to osapi, with the skill |

"Behavior" keeps one meaning: a thing that osapi manages on a host. An endpoint
is a part of the platform. A user of osapi does not define one. Thus the
endpoint has its own name, its own package and its own commands. The
`build-a-behavior` skill does not make endpoints. The skill for endpoints is a
dev skill only, which `osapi skill` serves to a checkout of osapi. `osapi init`
does not install it.

Later, a behavior builds on the endpoint layer.
[Behaviors on endpoints](#behaviors-on-endpoints) tells how.

## The inventory

Each of the 25 operations is in this table, with what the DSL must say for it.
The definitions must express each row before the first group moves.

| Group     | Operations                                                 | What the DSL needs for it                                                                                                                                                                                                          |
| --------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| agent     | list, pending, get, remove, accept, reject, drain, undrain | a key in the path (`{hostname}`); a fixed sub-path beside the key (`/agent/pending`), so the order of the routes is important; actions on the key (`/agent/{hostname}/drain`); query parameters (`machine_id`, `fingerprint`); 409 |
| audit     | list, get, export                                          | pagination (`limit`, `offset`) and a total; an export of each entry                                                                                                                                                                |
| facts     | keys                                                       | a permission of a different group (`agent:read`)                                                                                                                                                                                   |
| file      | list, stale, get, upload, update, delete                   | a multipart upload; 201 with `Location`; 200 for a file that exists; 409; 503 when no Object Store is set                                                                                                                          |
| health    | liveness, ready, status                                    | no auth for liveness and ready, which probes call; 503; the permission `health:read`                                                                                                                                               |
| job       | list, get, delete, retry                                   | a filter (`status`); 204 with no body; a JSON body; 201                                                                                                                                                                            |
| telemetry | trace get                                                  | a permission with a different name (`trace:read`); 503 when the backend is not set                                                                                                                                                 |

The 94 operations under `/api/node/{hostname}` are host work. They become
behaviors, not endpoints.

The status of a node is one of them. It is the `status` behavior at
`GET /api/node/{hostname}/status`, which requires the hostname, uptime, os,
load, memory and disk behaviors (osapi-io/osapi#945).

Some things are not API operations, and stay code:

- the middleware: auth, audit, request validation, tracing
- the metrics server of each component, with its own `/health` and
  `/health/ready`
- the commands that run on the local machine: `agent start`, `controller start`,
  `nats server`, `start`, `config`, `token`, `behavior`, `skill`, `init`,
  `version`. Their pages are already generated from cobra.
  [Commands](commands.md) plans a definition for each of them, in the layer that
  the endpoint DSL embeds.
- the files of the UI

## The definition

The agent group, as `internal/controller/endpoints/agent/agent.go` has it, cut
short:

```go
var Group = endpoint.Register(endpoint.Define(
	"agent", "The agents of the fleet",
	endpoint.Title("Agent Management API"),
	endpoint.Tag("agent_operations", "Agent",
		"Operations related to agent discovery and details."),
	endpoint.Get[ListInput, ListAgentsResponse]("list").
		ID("getAgents").
		Describe("List active agents").
		Returns("List of active agents."),
	endpoint.Get[ListInput, ListPendingAgentsResponse]("pending").
		Sub("pending").
		ID("getAgentsPending"),
	endpoint.Post[DrainInput, Message]("drain").
		Action("drain").
		ID("drainAgent").
		Errors(
			endpoint.NotFound(ErrNotFound, "Agent not found."),
			endpoint.Conflict(ErrState, "Agent already in requested state."),
		),
))
```

- **A group** is one name, such as `agent`. It is the first segment of each
  path, the CLI group, and the default permissions `agent:read` and
  `agent:write`. `Title` and `Tag` keep the title and the tag of the
  hand-written spec. The joined spec puts the title in front of each tag, and
  the UI's client files get their names from the result. Thus the move does not
  rename them.

- **A method** is `Get`, `Post`, `Put` or `Delete`, with its input and output
  types. A field of the input tagged `in:"path"` is the key, and a field tagged
  `in:"query"` is a query parameter. The other fields are the JSON body, or one
  field tagged `in:"body"` is the whole body. The path is
  `/api/<group>[/<sub>][/{key}][/<action>]`.

- **The output type** is the response. A named struct is a schema in the
  components, with its name. A struct with no name, such as `Message`, is in
  place. A field is required when its json tag has no `omitempty`. `time.Time`
  is a `date-time`. A `float64` is a `number` of format `double`, and a
  `float32` a `number` with no format, as oapi-codegen maps them back. A
  `pattern:"..."` tag gives a string a regular expression, and the route answers
  400 for a value that does not match. `validate:"oneof=..."` gives an enum. In
  the input, a field is required when it is tagged `validate:"required"`. Each
  input field has a validate tag, and the spec carries the whole tag in
  `x-oapi-codegen-extra-tags`. The rules are the behavior DSL's, from
  `internal/validation/rule`; [behaviors](behaviors.md) has them. Each rule of
  each input field has a `.Fails(doc, input)` that breaks it, as a behavior's
  refusals do, and `controller endpoint validate` names a rule that has none.

- An optional field of a write's body, with `omitempty` in its validate tag, has
  `omitempty` in its `json` tag too, also inside the type that `in:"body"`
  names. Otherwise a client sends `""` or `0`, and the field's other rules
  refuse it. The `optional` rule fails it, and the behavior DSL asks the same
  check of its writes. admission's `reason` was the one field that broke it.

- The rules after `dive` are each item's: `max=10,dive,max=255` is at most 10
  items of at most 255 characters, in the server and in the spec. A field tagged
  `secret:"true"` is write-only, with the password format, in the spec.
  `TestRefusals`, in `internal/controller/endpoints/all`, sends each one through
  the routes and expects 400 with `{"error": "..."}`. The route is the only
  place a handler runs, so the route's check holds for every call.
  `TestHandlersRunFromRoutes`, in the same package, fails a call of a handler
  from other code, as `behaviortest` fails a direct call of a behavior's method.

- **`ID`** keeps the operationId of the hand-written spec. The generated Go SDK
  and the UI client get their names from it. Thus the move does not change a
  name that a program calls. When the SDK services are generated (osapi#732),
  the IDs can follow a rule. Without `ID`, the operationId is the verb, the
  group, the sub-path and the method name, in Pascal case, as
  [the API conventions](api.md) require.

- **`Errors`** maps the errors of a method to status codes. An error that is not
  in the list is a 500. Each method also gets 400 when it has an input, 401 and
  403 when it is not public, and 500.

- **`Permission`** and **`Public`** change the default auth. `Public` is only
  for the health probes.

- **`Uses[Deps]()`** names the struct of what the handlers use, such as the job
  client and the admission store, as interfaces. The controller gives one at
  startup, in `internal/controller/handlers.go`. A test gives the mockgen mocks
  of the group's `mocks/`, never a fake written by hand. It is the place of the
  host in a behavior. `controller endpoint spec get` lists each service that a
  `Deps` takes now (`Jobs`, `Store`, `Objects`, `States`, `Health`, `Traces`)
  under "What a Deps takes". A test fails on a field of a `Deps` that has no
  entry there.

- **`.Handle(fn)`** sets the function of a method,
  `func(ctx, Deps, In) (Out, error)`. `Validate` checks the signature. A handler
  answers 404 or 409 with `endpoint.Errorf(sentinel, "...")`, so the message
  names what it was called with. Any other error is a 500, and is logged.

- **`Doc[T]("...")`** describes a named type, and **`example:"..."`** gives a
  field an example. The join fails when two specs define one schema in different
  words, so a group that shares a schema with another spec copies them.

- **`.Command(short, long)`** and **`.Example("--flag value")`** give the CLI
  command its own help, for a person at a shell, and its examples. Each input
  field is a flag, named for its json name with `_` as `-`.

- **The output** of each command comes from the output type of its method, with
  the tags of its fields ([the CLI](cli.md#output-comes-from-the-output-type)).
  No command has a renderer.

- **The help of the group's commands** comes from the definition, so a group has
  no file in `cmd/`. The group's one line is the help of its command, and
  `CommandLong("...")` adds more. `SubDoc("segment", "...")` is the one line of
  the command that a `.Sub` segment makes, such as `trace` in
  `osapi client telemetry trace get`. `validate` fails a `.Sub` segment that
  makes a command of its own and has no `SubDoc`. The page of each names the
  permission that covers each command under it. A parent that has flags or
  hooks, such as `client` and `client node`, stays in `cmd/`. So does
  `client controller`, while its `key` command is hand-written.

## What it generates

`go generate ./internal/controller/endpoints/all` runs the generator,
`internal/controller/endpoint/gen`. It is in Go, with jen, as the generator of
behaviors is. For each group that Uses a type, it writes `gen/api.yaml` from
kin-openapi, `gen/api.go` with the routes, `gen/decode.go` with one decoder for
each method, and `gen/cli.go` with one cobra command for each method under
`osapi client <group>`. `internal/controller/endpoints/all/gen` registers the
routes and the commands of each group. The controller imports it. Each generated
route calls `Serve` of `internal/controller/endpoint/server`: it decodes and
validates the input, runs the handler, and writes the output, or the error with
the status that `Errors` maps it to. Auth is the same `ScopeMiddleware` as each
route has.

It writes these:

| File                                                  | Has                                                           |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| `internal/controller/endpoints/<group>/gen/api.yaml`  | the part of the spec for the group                            |
| `internal/controller/endpoints/<group>/gen/api.go`    | the routes: verb, path, permission and handler                |
| `internal/controller/endpoints/<group>/gen/decode.go` | a decoder for each method: path, query, body and validation   |
| `internal/controller/endpoints/<group>/gen/cli.go`    | a CLI command for each method, its flags, help and permission |
| `docs/docs/sidebar/usage/cli/client/<group>/`         | the CLI pages, from cobra                                     |
| `ui/src/lib/permissions.gen.ts`                       | the permissions of the group                                  |

The joined spec then has the endpoints and the behaviors, and no hand-written
part.

`just generate` runs this generator and the generator of behaviors first. Then
it joins the spec. Then it runs the rest of `go generate`. The SDK client is
generated from the joined spec, in the same `go generate` pass as the specs of
the groups. If the join came first, it would read the old specs of the groups.
Then one run would leave the joined spec and the SDK stale, and a second run
would be necessary (osapi#829).

## The commands

The commands are under the process that the endpoints belong to:

```sh
osapi controller endpoint list                                 # the groups and their methods
osapi controller endpoint get --name agent                     # the routes, permissions and operationIds
osapi controller endpoint openapi get --name agent             # the group's part of the spec, as YAML
osapi controller endpoint spec get                             # each part of the DSL, and when to use it
osapi controller endpoint validate                             # the rules of each definition, each with its fix
osapi controller endpoint create --name x --description "..."  # a new group that passes its tests
```

`spec` and `validate --help` come from the tables of the `internal/guide`
package, as the commands of behaviors do: `endpoint.Spec` and `endpoint.Checks`.
A test fails on an exported option of the DSL that has no term in
`endpoint.Spec`, and on a rule of `Validate` that has no check. Thus the help
cannot fall behind the code. `spec` also lists what is not built yet, so an
agent stops there.

`new` writes a group with a list and a get, an empty `Deps`, its types and the
tests of its methods, and registers it, as `osapi behavior create` does for a
behavior. An empty `Deps` needs no wiring in the controller, so the group works
once it is generated. Its first field makes the controller give it, in
`internal/controller/handlers.go`. `just endpoint-scaffold-check` writes a group
in a copy of the checkout, generates it, and runs its tests and the
controller's.

## How we know that the output is correct

No group moves until its generated output agrees with what is there now. The
hand-written specs stay, and keep serving the API, until then.

1. **The spec first, and nothing served.** Built for the agent group. The group
   has its types and IDs, and no methods that run. The controller does not serve
   its spec.
2. **A parity test for the contract.** Built. `TestEndpointParity`, in
   `internal/controller/endpoints/all`, has one row for each group that moves.
   It reduces the two specs to their contract with `internal/apicontract`, and
   compares them. The contract has one line for each tag, each operation and
   each schema property: the path, the verb, the operationId, the tags, the
   auth, each parameter, the request body and each response with its schema. A
   difference fails the test, unless the row accepts it with its reason.
3. **The prose.** `osapi controller endpoint openapi get --name agent` prints
   the generated spec, to read next to the hand-written spec. A person reads the
   descriptions and the examples. The test does not compare them.
4. **The CLI.** Built for the agent group. The help of each generated command,
   as JSON (`--help --json`), was compared with the help of the hand-written
   command: the same flags, the same types and the same required flags. The flag
   help has the words of the input field's `doc`. `agent list --pending` called
   two methods; it is now `agent pending list`, a resource and a verb, which
   `.Use("list")` names apart from the group's own `list`. The CLI pages gained
   the permission of each command.
5. **Golden files.** The generated files of the first group have golden copies,
   as the files of `osapi behavior create` have. A change to the generator shows
   as a diff of what it writes.
6. **The handlers last.** Built for the agent group. The methods are written.
   Each case of the hand-written handler tests moved into a test of the method,
   on mocks of `Deps`, or into an HTTP test through the generated routes, for
   auth, 400 and each status. Then the controller serves the generated routes,
   and the hand-written spec and handler of the group are deleted. The commands
   come from the definition too.
7. **The whole spec, at each step.** Built.
   `internal/apicontract/testdata/joined.golden` is the contract of the joined
   spec, and a test holds the joined spec to it. Each pull request that moves a
   group must leave the joined spec equal to that file. Thus a difference that
   falls between the groups also fails, such as a shared schema that changes
   shape. A change to the API that is wanted, such as a new endpoint, writes the
   file again in the same pull request (`-update`), so the diff shows it. When
   the last group moves, the file stays as the contract of the API.

The agent group agrees with its hand-written spec on each line. The first run
found two that did not: drain and undrain listed no 500, because their handlers
answered 409 when the controller failed, and 409 says that the agent is already
in that state. They answer 500 now (osapi#788). A row of the parity test can
accept a line that differs on purpose, with its reason. The agent row accepts
none, and it went when the hand-written agent spec was deleted.

When the agent group switched, `TestJoinedSpec` passed without `-update`: the
contract of the API did not change. The Go SDK made from the joined spec is the
same, byte for byte. The UI client has the same exports, with its fields in the
order of kin-openapi. The prose of the agent group's API pages changed: the
generated 400 and 500 have one description each, not one for each operation.

`redocly join` takes the title and the description of the joined spec from the
first file that it reads. The join reads the components spec first, so the API
has its own title, "osapi", and its tagline, whatever the order of the groups
(osapi#798). Before, the API had the title of the first group, "Agent Management
API".

## The order

The agent group is served from its definition. It was first because its eight
operations have most of the hard cases: a key, a fixed sub-path beside the key,
actions, query parameters and 409. The DSL gets its shape there.

Then each group moves in its own pull request, from the easiest:

1. agent
2. telemetry: one GET, a permission with a different name, and 503. Moved. Its
   command stays `osapi client telemetry trace get`: a method whose `Sub` is not
   its name is under a command of that name. `--all` is the query parameter
   `all`, and a backend that fails is `endpoint.Internal`, so the caller does
   not get the backend's error.
3. audit: pagination and an export. It is served from its definition. Its CLI
   paths stay `audit list`, `audit get` and `audit export`; `export`'s
   `--output` and `--type` are `.StringFlag`s, and an input field's `default`
   tag is its flag's value too. With no `nats.audit.stream`, each audit endpoint
   answers 503, where the controller had no route before. The DSL gained
   `Example[T]` for an example with a double quote, because the formatters drop
   the backslash of a quote in a struct tag
4. job: a filter, 204, and a JSON body with 201. It is served from its
   definition. `job list --json` prints the API's answer, as each generated
   command does. A field of an `in:"body"` struct is a flag, and the `flag` and
   `short` tags keep retry's `-T/--target`. `endpoint.Invalid` maps an error to
   400, for a retry of a job with no operation data
5. facts: a permission of a different group. It is served from its definition,
   and gains `osapi client facts keys list`: the method is `list` under `keys`,
   as `telemetry trace get` is, so the command is a resource and a verb
6. file: a multipart upload. It is served from its definition. A field tagged
   `in:"form"` makes the body `multipart/form-data`, and a `[]byte` field is the
   file. In the CLI, the flag of a `[]byte` field is the path of a local file,
   and the command sends a multipart body. `endpoint.Forbidden` maps a write to
   an osapi file to 403. With no Object Store, each file endpoint answers 503,
   and `file stale list` answers 503 with no state bucket. `file list --stale`
   is now `file stale list`, one command for each operation
7. health: no auth, and the probes depend on it. It went before file, because
   file needed a multipart body, which the DSL did not have then. It is served
   from its definition. The readiness probe answers 503 with its own body, which
   `.Answers(code, doc)` declares and `endpoint.Answer(code)` sends; the CLI
   prints that body, as the SDK's `APIError` keeps it. `health status` answers
   200 with the overall status `degraded`: it is a report, not a probe, so a
   non-2xx answer means only a failed request, as at each other endpoint. The
   checker, the metrics and the status builder are the controller's, in
   `internal/controller/health`

No cutover of a behavior (osapi#731) occurs before the DSL is settled.

## Behaviors on endpoints

The issue is osapi#826. Each method of a behavior becomes a method of an
endpoint group, and the endpoint layer serves it. The endpoint layer writes the
spec, the route, the decoder, the validation and the CLI command. The behavior
layer adds only the host work: the job, the result for each host, the providers,
and the examples on a fake host. Thus each rule of the API, such as the error
body or `TestConventions`, holds for a behavior with no second copy. The
validation rules showed the cost of two copies: osapi#827, #828 and #837 built
each one twice.

### What a behavior method becomes

| Part of the endpoint method | What the behavior generator writes                                                                                                                                                                    |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The group                   | one group for each behavior, under the prefix `next/node/{hostname}`, then `node/{hostname}` at the cutover (osapi#731)                                                                               |
| The input type              | a request type in `gen/`: a `hostname` path field, tagged `validate:"required,min=1,valid_target"` and `flag:"target" short:"T"`, then the method's input fields                                      |
| The key                     | the method's key field, as an `in:"path"` field of the request type                                                                                                                                   |
| The body                    | for a write, the other input fields as an `in:"body"` struct with the name `<Behavior><Method>Request`; for a read, `in:"query"` fields                                                               |
| The output type             | `<Behavior>CollectionResponse` for a list and `<Behavior><Method>Response` for each other method: `job_id`, and `results` with one row for each host, such as `SysctlEntry` or `SysctlMutationResult` |
| The handler                 | one generic handler of the behavior package. It sends the job to one host or to each host of the target, and makes the result rows                                                                    |
| The permission              | `<behavior>:read` or `<behavior>:write`, with `.Permission`                                                                                                                                           |
| The errors                  | 404 for a keyed method when the host does not have the item, from a sentinel of the behavior package                                                                                                  |
| The refusals                | each `.Fails` of the method whose input breaks a validate rule                                                                                                                                        |

The handler keeps the behavior's own checks: the agent checks the input again
with `Method.Check`, and `behavior.Call` checks the input of a call between
behaviors. The endpoint route is the check at the API.

### What the endpoint DSL gains

Only general parts. The endpoint DSL does not learn about hosts, targets or
jobs.

- A group prefix with path fields, such as `Prefix("next/node/{hostname}")`. The
  rule of one path field becomes one key, besides the fields of the prefix.
- A shared path parameter: a path field tagged `param:"Hostname"` is a reference
  to that parameter in the components of the spec, not a parameter in place.

A behavior that needs more than these, or a part of the endpoint DSL that knows
about a host, is a sign that the design is wrong. Stop and decide it again.

### What the behavior layer loses

The spec writer (`internal/behavior/openapi`), the server runtime
(`internal/behavior/server`) and most of the command runtime
(`internal/behavior/command`). The behavior generator stays, and writes the
definition of the endpoint group, the generated HTTP tests on the fake job
client, and the pages of each behavior. The result table for each host stays:
the behavior runtime prints it through `command.PrintsGroups`, the one printer
that a kind of group adds.

### How we know that the output is correct

The API that sysctl serves must not change: its paths, operationIds, parameters,
schemas, status codes and permissions. A golden file of these, in the form of
`TestJoinedSpec`, holds them. The wording of the spec moves to the wording of
the endpoint layer. For example, a 400 of a behavior says "The request is not
valid." and not "Bad request - validation error.". Thus a byte for byte copy of
the old spec is not the test. It would make the endpoint layer copy the wording
that the change removes.

The generated HTTP tests of sysctl must pass with no change, against the
endpoint routes. `osapi client next node sysctl ... --help`, as sysctl was
before its cutover, and the pages of the commands must not change, but for one
line: `--target` is a flag of each command, not a global flag of `next node`.

### The order

Each step is one pull request, with its own specs change.

1. The spec. The endpoint builder makes the spec of each behavior, and
   `internal/behavior/openapi` goes. The endpoint DSL gains the prefix and the
   shared parameter.
2. The routes. The endpoint server serves each behavior, and
   `internal/behavior/server` goes. The generic handler of a behavior,
   `internal/behavior/dispatch`, replaces it. Built: the route and decoder
   writer of the endpoint generator moved to
   `internal/controller/endpoint/gen/routegen`, which the behavior generator
   uses too. A write with only a key, such as a delete, has no body in its spec,
   and its route reads none, so its generated tests have no case for a body that
   is not JSON.
3. The commands. The endpoint command runtime makes the behavior commands, with
   the result table as a renderer, and the rest of `internal/behavior/command`
   goes. Built: the endpoint generator's command writer is
   `internal/controller/endpoint/gen/commandgen`, beside `routegen`, with their
   shared helpers in `gen/genutil`. The behavior generator writes each group's
   `gen/cli.go` with it. The endpoint DSL gained an example's doc,
   `CommandNotes` and the command path of a prefix. The endpoint command runtime
   gives a renderer the trace ID of its call. The two generators also share
   their file writer, `gen/genfile`, which cleans, writes, groups imports,
   formats and writes the registry of blank imports, and their spec writer,
   `gen/specgen`, with one encoding and one reference to the shared
   `ErrorResponse`.

After step 3, a node domain that moves to a behavior (osapi#731, osapi#838) is
an endpoint group too.

## Not decided

- The rule for the operationIds after osapi#732.

## What this page does not cover

The middleware and the auth model are in [permissions](permissions.md). The
generator of behaviors is in [behaviors](behaviors.md). The order of the domains
that become behaviors is in [the migration](behavior-migration.md).
