# Behaviors

A behavior is one area of a host that osapi manages, such as kernel parameters,
declared once as a typed definition. The route, the permission, the CLI command
and the JSON Schema of every method are worked out from that definition rather
than written by hand in each layer.

Behaviors are replacing [providers](providers.md) one domain at a time. sysctl
is the first. The order of the rest, and the parts not built yet, are in
[the pivot plan](pivot.md).

## What a definition is

A behavior lives under `pkg/behavior/<name>/`. Its definition is one call:

```go
var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters managed under /etc/sysctl.d",
    behavior.Node,
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

## What the definition decides

| Declared                    | Decides                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| `behavior.Node`             | The work runs on a host, through the job system. It is the only placement                   |
| `behavior.Under("network")` | Nests the behavior: `/api/node/{hostname}/network/dns`, `osapi client node network dns`     |
| `Read`                      | `GET`, the `<group>:read` permission, no `changed` in the result                            |
| `Write`                     | `POST`, or `PUT` for `update` and `DELETE` for `delete`, and the `<group>:write` permission |
| `.Key("key")`               | The input field addressed in the path, `/{key}`                                             |
| `.Describe`, `.Example`     | The one-line description, and sample calls for the generated docs                           |

The permission prefix is the group when there is one and the behavior's name
otherwise, so `dns` under `network` needs `network:read`, as it does today.

What the controller answers itself, audit, jobs, agent enrollment and health, is
not a behavior and has no placement. It never reaches a host.

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

## Inspecting behaviors from the CLI

Three commands read the registry. They need no config file and no controller,
because they describe the binary rather than a fleet:

```sh
osapi behavior list                     # the behaviors and their methods
osapi behavior describe sysctl          # each method's verb, route, permission
osapi behavior describe sysctl update   # one method's input and output fields
osapi behavior validate                 # every definition against the rules
```

Each takes `--json`. `describe --json` prints each method's route, permission,
CLI command, and input and output as JSON Schema, which is what an agent reads
before building a request. Tables render through
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

It exits 1 when any rule fails. It is the check an agent runs after writing a
behavior, before the tests.

## Not built yet

The registry is read by the three commands above, and by nothing else yet. The
API still serves sysctl through the hand-written handlers in
`internal/controller/api/node/sysctl/`, the agent still dispatches it through
`internal/agent/processor_sysctl.go`, and the CLI's `client node sysctl`
commands are still the files in `cmd/`. Building those from the registry is the
next step in [the pivot plan](pivot.md).

sysctl's definition wraps the existing provider interface in
`internal/provider/node/sysctl`. The provider's code moves into the behavior's
directory when the agent dispatches through the registry.
