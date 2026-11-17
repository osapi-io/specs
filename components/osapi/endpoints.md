# Endpoints

A plan, with its first step built: the DSL, the spec of the agent group, the
commands that read it, and the tests that compare it with the hand-written spec.
The controller still serves the hand-written specs. An endpoint is one HTTP
operation of the controller itself, such as `GET /api/agent` or
`POST /api/job/{id}/retry`. Its definition is Go. The route, the part of the
OpenAPI spec, the CLI command, its page, the permission and the HTTP tests come
from that definition, as they come from the definition of a
[behavior](behaviors.md). Thus no part of the API uses a spec that a person
writes.

The issue is osapi#744.

## Why

The controller has 25 operations, in seven groups, that a person writes four
times each: the spec, the handler, the service of the SDK and the CLI command.

```sh
ls internal/controller/api/*/gen/api.yaml | grep -v -e /node/ -e /next/ -e /components/ | xargs cat | grep -cE '^    (get|post|put|delete|patch):'   # 25
```

A new operation of the controller, such as `osapi client telemetry trace get`
(osapi#741), has no generator. Behaviors cover the work on a host. Nothing
covers the work on the controller.

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
| file      | list, stale, get, upload, delete                           | a multipart upload; a query option (`force`); 201 and 409                                                                                                                                                                          |
| health    | liveness, ready, status                                    | no auth for liveness and ready, which probes call; 503; the permission `health:read`                                                                                                                                               |
| job       | list, get, delete, retry                                   | a filter (`status`); 204 with no body; a JSON body; 201                                                                                                                                                                            |
| telemetry | trace get                                                  | a permission with a different name (`trace:read`); 503 when the backend is not set                                                                                                                                                 |

The 94 operations under `/api/node/{hostname}` are host work. They become
behaviors, not endpoints:

```sh
find internal/controller/api/node -path '*/gen/api.yaml' | xargs cat | grep -cE '^    (get|post|put|delete|patch):'   # 94
```

One of them is not decided: `GET /api/node/{hostname}`, the status of a node. It
runs on the agent, so it is host work. But its path is the root of the node, not
the name of a behavior. When hostname, disk, memory and load are behaviors, it
can be a behavior that requires them.

Some things are not API operations, and stay code:

- the middleware: auth, audit, request validation, tracing
- the metrics server of each component, with its own `/health` and
  `/health/ready`
- the commands that run on the local machine: `agent start`, `controller start`,
  `nats server`, `start`, `config`, `token`, `behavior`, `skill`, `init`,
  `version`. Their pages are already generated from cobra.
- the files of the UI

## The definition

The agent group, as `internal/endpoints/agent/agent.go` has it, cut short:

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
  is a `date-time`. `validate:"oneof=..."` gives an enum. In the input, a field
  is required when it is tagged `validate:"required"`.
- **`ID`** keeps the operationId of the hand-written spec. The generated Go SDK
  and the UI client get their names from it. Thus the move does not change a
  name that a program calls. When the SDK services are generated (osapi#732),
  the IDs can follow a rule. Without `ID`, the operationId is the verb, the
  group, the sub-path and the method name.
- **`Errors`** maps the errors of a method to status codes. An error that is not
  in the list is a 500. Each method also gets 400 when it has an input, 401 and
  403 when it is not public, and 500.
- **`Permission`** and **`Public`** change the default auth. `Public` is only
  for the health probes.

Not built yet:

- **`Uses[Deps]`** will name a struct of the things that the methods use, such
  as the job client and the KV buckets. The controller fills it at startup. A
  test gives fakes. This is the place of the host in a behavior. It comes with
  the handlers.
- **A renderer** is the one part of the CLI that a group can write. The command
  is generated. The output of `trace get` is a tree, and the output of
  `agent get` is a detail view. A method that needs more than the shared table
  and key value renderers names a renderer.

## What it generates

The first step makes the spec of a group in memory, with kin-openapi. It writes
no file yet. The rest comes with the handlers. The generator is in Go, with jen,
as the generator of behaviors is. Each file that it writes is under the `gen/`
of the group, or in the generated pages:

| File                                          | Has                                                                |
| --------------------------------------------- | ------------------------------------------------------------------ |
| `internal/endpoints/<group>/gen/api.yaml`     | the part of the spec for the group                                 |
| `internal/endpoints/<group>/gen/*.gen.go`     | the routes, the handlers, the request validation, the CLI commands |
| `internal/endpoints/<group>/gen/*_test.go`    | the HTTP tests: each method, each error, each code, auth           |
| `docs/docs/sidebar/usage/cli/client/<group>/` | the CLI pages, from cobra                                          |
| `ui/src/lib/permissions.gen.ts`               | the permissions of the group                                       |

The joined spec then has the endpoints and the behaviors, and no hand-written
part.

## The commands

```sh
osapi endpoint list                      # the groups and their methods
osapi endpoint get --name agent          # the routes, permissions and operationIds
osapi endpoint get --name agent --openapi  # the group's part of the spec, as YAML
osapi endpoint validate                  # the rules of each definition, each with its fix
```

`osapi endpoint spec` and `osapi endpoint new` come later, as `osapi behavior`
has them. `spec` and `validate --help` will come from the tables of the
`internal/guide` package.

## How we know that the output is correct

No group moves until its generated output agrees with what is there now. The
hand-written specs stay, and keep serving the API, until then.

1. **The spec first, and nothing served.** Built for the agent group. The group
   has its types and IDs, and no methods that run. The controller does not serve
   its spec.
2. **A parity test for the contract.** Built. `TestEndpointParity`, in
   `internal/endpoints/all`, has one row for each group that moves. It reduces
   the two specs to their contract with `internal/apicontract`, and compares
   them. The contract has one line for each tag, each operation and each schema
   property: the path, the verb, the operationId, the tags, the auth, each
   parameter, the request body and each response with its schema. A difference
   fails the test, unless the row accepts it with its reason.
3. **The prose.** `osapi endpoint get --name agent --openapi` prints the
   generated spec, to read next to the hand-written spec. A person reads the
   descriptions and the examples. The test does not compare them.
4. **The CLI.** The help of each generated command, as JSON (`--help --json`),
   is compared with the help of the hand-written command: the same flags, the
   same types, the same defaults.
5. **Golden files.** The generated files of the first group have golden copies,
   as the files of `osapi behavior new` have. A change to the generator shows as
   a diff of what it writes.
6. **The handlers last.** The methods are written. Each case of the hand-written
   handler tests moves into the generated HTTP tests, or into a test of the
   method. Then the controller serves the generated routes, and the hand-written
   spec, handler and command of the group are deleted.
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
none.

## The order

The first step, which is built, makes the package, the commands and the spec
only, against the agent group. Agent comes first because its eight operations
have most of the hard cases: a key, a fixed sub-path beside the key, actions,
query parameters and 409. The DSL gets its shape there.

Then each group moves in its own pull request, from the easiest:

1. agent
2. telemetry: one GET, a permission with a different name, and 503
3. audit: pagination and an export
4. job: a filter, 204, and a JSON body with 201
5. facts: a permission of a different group
6. file: a multipart upload
7. health, last: no auth, and the probes depend on it

No cutover of a behavior (osapi#731) occurs before the DSL is settled.

## Behaviors on endpoints

When the endpoints are built, each method of a behavior makes an endpoint. The
endpoint layer writes the route, the spec, the CLI command and the permission.
The behavior adds only what host work needs: the job, the targets, the result
for each host, the providers and the examples on a fake host.

The test of that change is the output of sysctl. Each file that the generator
writes for it must be the same, byte for byte. Then nothing that a user sees
changes.

## Not decided

- The place of `GET /api/node/{hostname}`. It is host work, but its path is not
  under a behavior.
- The rule for the operationIds after osapi#732.

## What this page does not cover

The middleware and the auth model are in [permissions](permissions.md). The
generator of behaviors is in [behaviors](behaviors.md). The order of the domains
that become behaviors is in [the migration](behavior-migration.md).
