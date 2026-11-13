# Behaviors

A behavior is one area of a host that osapi manages, such as kernel parameters,
declared once as a typed definition. The route, the permission, the agent's
dispatch, the CLI command, the OpenAPI spec, the docs pages and the telemetry of
every method are built from that definition rather than written by hand in each
layer.

Behaviors are replacing [providers](providers.md) one domain at a time. sysctl
is the first. The order of the rest, and the parts not built yet, are in
[the migration plan](behavior-migration.md).

## Why

Adding a domain is slow because most of the code is glue, not logic. Measured on
`main` on 12 November 2026, before sysctl moved:

- `sysctl get` is 59 lines of logic in `debian.go` and 312 hand-written lines
  around it: handler 153, validator 10, agent processor 28, SDK 56, CLI 63,
  operation constants 2. Its spec is another 104 lines of hand-written YAML.
- Across the repository, the handlers, agent processors, SDK and CLI are 47,792
  hand-written lines against 15,189 lines of provider.
- The last three domain additions touched 130 files (`service`), 75
  (`certificate`) and 47 (the SSH key operations).

The glue is the same every time, and it is retyped every time. The `key`
argument to `sysctl get` is declared by hand in eight places. Its pattern,
`^[a-zA-Z0-9][a-zA-Z0-9._-]*$`, is written three times. The handler sends the
job payload as a `map[string]string`, and the agent reads it back into an
anonymous `struct{ Key string }`. Nothing checks that the two agree.

The same shapes repeat across the codebase:

- 40 anonymous payload structs in `internal/agent`.
- 90 copies of the `ok`/`failed`/`skipped`/`timeout` switch in the handlers.
- 94 handlers that branch on `IsBroadcastTarget`.
- 136 hand-written SDK result types, with 127 functions that copy generated
  types into them.

The cost is the obvious one, and it also blocks agents. An agent asked to add a
domain has to reproduce all of it from convention. An agent asked to use osapi
had nothing to discover operations from until `osapi init`, `help --json` and
`behavior get` existed, and those read the definitions.

## What a definition is

A behavior lives under `pkg/behavior/<name>/`. Its definition is one call:

```go
var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters managed under /etc/sysctl.d",
    behavior.Node,
    behavior.API,
    behavior.CLI,
    behavior.Read("list", List).Describe("List the kernel parameters osapi manages"),
    behavior.Read("get", Get).Key("key").Describe("Get a kernel parameter's current value"),
    behavior.Write("create", Create).Describe("Manage a kernel parameter and apply it"),
    ...
))

type GetInput struct {
    Key string `json:"key" validate:"required,min=1,sysctl_key" doc:"Parameter name, such as net.ipv4.ip_forward"`
}

func Get(ctx context.Context, p Provider, in GetInput) (Entry, error)
```

A method is a function taking a context, the platform's provider and one typed
input, and returning one typed output or an error. `Read` and `Write` are
generic over those three types, so the definition carries the Go types and
nothing restates them.

The package registers itself when imported, and `pkg/behavior/all` imports every
behavior. Adding one is a directory and a line in `all.go`.

Every behavior's directory has the same files: `behavior.go` for the definition,
`types.go` for the input and output types, `methods.go`, `provider.go`, an
optional `telemetry.go`, and `gen/` for what is generated from them. The layout
and the tags are written for authors in osapi's
`docs/docs/sidebar/development/behaviors.md`; this page records why it is built
the way it is.

## What the definition decides

| Declared                    | Decides                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| `behavior.Node`             | The work runs on a host, through the job system. It is the only placement                   |
| `behavior.Under("network")` | Nests the behavior: `/api/node/{hostname}/network/dns`, `osapi client node network dns`     |
| `Read`                      | `GET`, the `<group>:read` permission, no `changed` in the result                            |
| `Write`                     | `POST`, or `PUT` for `update` and `DELETE` for `delete`, and the `<group>:write` permission |
| `.Key("key")`               | The input field addressed in the path, `/{key}`                                             |
| `behavior.API`              | Routes, its part of the OpenAPI spec, and the API reference pages                           |
| `behavior.CLI`              | Generated commands and CLI docs pages. It needs `API`, because the commands call the API    |
| `.Describe`, `.Explain`     | The one-line description, and the longer help a command and its docs page carry             |
| `.Example`                  | Sample calls. The docs pages are these, run through the CLI's renderer                      |

The permission prefix is the group when there is one and the behavior's name
otherwise, so `dns` under `network` needs `network:read`, as it does today.

What the controller answers itself, audit, jobs, agent enrollment and health, is
not a behavior and has no placement. It never reaches a host.

`API` and `CLI` are separate because not every behavior is called from outside.
One that only other behaviors use has neither, and is reachable through the job
system alone.

`pkg/behavior/behavior.go` holds `Path`, `HTTPMethod`, `Permission` and
`Command`, which turn a definition into those four. For sysctl they give the
same routes and permissions the hand-written API serves today.

## Types become JSON Schema

`behavior.SchemaFor` reads a Go type's tags: `json` names the field, `doc`
describes it, and `validate` gives the constraints. Standard tags map directly:
`required`, `min`, `max` and `len` by the field's type, `oneof` to an enum, and
`ip`, `url`, `email`, `hostname`, `uuid` and `cidr` to formats.

A custom validator is a Go function, and nothing can read a schema out of one.
So each custom tag is registered with the schema it means, beside the validator,
in `internal/validation`:

```go
behavior.ValidatorSchema("sysctl_key", behavior.Pattern(sysctlKeyPattern.String()))
```

`SchemaFor` fails on a tag that is neither standard nor registered. A spec that
silently dropped a constraint would validate less than the server does, and
nothing would report it.

An output may be a struct or a slice of structs. A slice becomes one result row
per element, each carrying the host's name, which is how sysctl `list` answers
today.

Two more tags are read by the platform rather than the schema. `render` says how
an output field shows in a table (`-` hides it, `bytes`, `age`, `status`), so
every behavior's output renders through one layout instead of per-command
formatting. `telemetry:"attr"` records an input field on the method's span;
nothing untagged is recorded, so a password or a file's contents cannot reach a
trace by default.

## Served beside the hand-written domains

A behavior runs through three generic pieces, each written once:

- **The API.** `internal/controller/api/behavior` registers every method of
  every behavior with `API` on one handler. It sets the permission, validates
  the target and the input's tags, queues the job, and shapes the
  `{job_id, results[]}` envelope.
- **The agent.** `internal/agent/processor_behavior.go` runs any behavior. It
  finds the provider for a method by the method's provider interface among the
  providers the agent already builds, so a new behavior needs no agent wiring.
- **The CLI.** `internal/behaviorcmd` holds the one helper every generated
  command calls, and the one table layout every behavior renders in.

Until the cutover these are served beside the hand-written domains rather than
replacing them: routes under `/api/next`, commands under `osapi client next`,
and jobs in their own `behavior` category, whose operations are
`behavior.<name>.<method>`. The existing routes, commands, spec and docs are not
touched, so a behavior can be compared with the domain it will replace on the
same server.

## Generated, and committed

`go generate ./pkg/behavior/all` runs `internal/behaviorcmd/gen`, which writes:

| File                                              | Holds                                                |
| ------------------------------------------------- | ---------------------------------------------------- |
| `pkg/behavior/<name>/gen/cli.go`                  | the behavior's commands, flags bound to input fields |
| `pkg/behavior/<name>/gen/api.yaml`                | the behavior's part of the spec, for review          |
| `pkg/behavior/all/cli/cli.go`                     | the import of every behavior's commands              |
| `internal/controller/api/next/gen/api.yaml`       | one spec for every behavior with `API`               |
| `docs/docs/sidebar/usage/cli/client/next/<name>/` | a page per method, and an index                      |

The commands are generated into files rather than built when osapi starts, so a
reviewer reads and diffs exactly what a command does, the way oapi-codegen's
output is read today. They live in the behavior's own `gen/`, keeping everything
about a behavior in its directory.

The spec for every behavior is joined by the generator itself rather than by
`redocly join`, the start of dropping that tool. The docs site builds an "API
(next)" reference from it alongside the existing one.

A docs page's examples are the definition's `Example`s run through the CLI's
real renderer, captured with color by `cli.Capture` and turned into HTML, so a
page shows exactly what the terminal prints. Heading colors come from the
palette's fixed order while capturing rather than the run's shuffle, which keeps
the pages byte-for-byte stable between runs.

`just behavior-gen-check`, run by `just test`, regenerates and fails if any of
these files changed, so a behavior edited without `go generate` fails CI rather
than shipping commands and pages that describe its old shape. It compares only
the generated files, so other uncommitted work does not trip it.

## Telemetry every method gets

`Method.Invoke` is the one call every behavior method passes through on the
agent, so the telemetry is there rather than in each behavior: a
`behavior.<name>.<method>` span under the agent's `job.process` span carrying
the behavior, method, verb, outcome and `changed`, and three metrics,
`osapi_behavior_calls_total`, `osapi_behavior_duration_seconds` and
`osapi_behavior_changes_total`. They are created on the agent's meter provider,
so they export wherever the agent's metrics already go. The API request's span
records the behavior, method and target it ran.

## Inspecting behaviors from the CLI

Three commands read the registry. They need no config file and no controller,
because they describe the binary rather than a fleet:

```sh
osapi behavior list                                    # the behaviors and their methods
osapi behavior get --name sysctl                  # surfaces, methods, schemas
osapi behavior get --name sysctl --method update  # one method in full
osapi behavior validate                                # every definition against the rules
```

Each takes `--json`, and values arrive as flags, as everywhere in the
[CLI](cli.md). `get` shows whether the behavior has an API and a CLI and where
they are served today, what it uses (empty until behaviors can require one
another), and for each method its verb, route, permission, command, input and
output fields and examples. `--json` gives the input and output as JSON Schema,
which is what an agent reads before building a request. Tables render through
[the CLI's output style](cli.md#output-style).

## The rules validate checks

`behavior validate`, from `pkg/behavior/validate.go`, fails a definition the
platform could not build from. Each problem names its rule:

| Rule        | Fails when                                                                                                                               |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `name`      | a behavior, group or method name is not lowercase letters, digits and dashes                                                             |
| `placement` | the behavior has no placement                                                                                                            |
| `doc`       | the behavior or a method has no description                                                                                              |
| `methods`   | the behavior has no methods                                                                                                              |
| `duplicate` | two behaviors share a name, or a method is declared twice                                                                                |
| `key`       | `.Key` names a field the input does not have                                                                                             |
| `schema`    | an input or output type has no JSON Schema, such as an unregistered tag                                                                  |
| `output`    | the output is not a struct or slice of structs, or declares `hostname`, `status` or `error`, which every per-host result already carries |
| `changed`   | a write's output has no `changed` boolean                                                                                                |
| `surface`   | the behavior has `CLI` without `API`                                                                                                     |
| `example`   | an example's input or output is not the method's type, an example has no description, or a CLI behavior's method has no example          |

It exits 1 when any rule fails. It is the check an agent runs after writing a
behavior, before the tests.

## Not built yet

The cutover: routes moving from `/api/next` to `/api`, commands from
`client next` to `client`, the generated spec joining the main one, and sysctl's
hand-written handler, processor and commands being deleted. Until then sysctl's
definition wraps the provider interface in `internal/provider/node/sysctl`,
which the hand-written domain still uses; its implementations move into the
behavior's directory as `provider_<platform>.go` at the cutover.

The SDK has one generic call, `Client.Behavior`, and `client.Rows` to decode
results into a behavior's own types. Typed wrappers per behavior, `Requires` and
`Internal` are later steps in [the migration plan](behavior-migration.md).
