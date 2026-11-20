# Commands

Partly built: the command layer, the DSL, `token`, the commands that teach the
DSL, and the output from the output type (osapi-io/osapi#901, #902 and #903).
The other local groups are not built. Each command of the `osapi` binary comes
from a definition in Go, as each endpoint and each behavior does. The definition
gives the cobra command, its flags, its help, its page, its checks and its
tests. Endpoints and behaviors get their commands from this layer. Thus one DSL
makes every command, and `cmd/` has only the root and the wiring.

The issue is osapi-io/osapi#900.

## Why

`cmd/` has 178 files. 121 of them are the commands of the node domains that are
not behaviors yet. They go as each domain moves
([the plan](behavior-migration.md)). The other 57 stay, and a person writes each
one:

| Kind                                    | Files | Examples                                                                                           |
| --------------------------------------- | ----: | -------------------------------------------------------------------------------------------------- |
| Commands that run on the local machine  |    40 | `token generate`, `config validate`, `nats server start`, `agent start`, `behavior new`, `version` |
| Code of the CLI for the endpoint groups |    17 | the renderer of `client agent list`, `client agent status`, `client nats status`                   |

A command that a person writes gets no check. Nothing tells that a required flag
is marked, that the help has an example, that a value is checked, or that the
name obeys [the CLI rules](cli.md). An endpoint and a behavior get these checks
from their definitions. A local command gets none.

The skill has the same gap. An agent learns the endpoint DSL from
`osapi controller endpoint spec` and `validate`, and the behavior DSL from
`osapi behavior spec` and `validate`. Nothing teaches it to add a local command.

The CLI layer is in the code already, in the wrong place.
`internal/controller/endpoint/command` is the runtime of each generated command,
and `internal/controller/endpoint/gen/commandgen` writes them. Behaviors use
them through the endpoint layer. No command outside the two DSLs uses them.

## Three layers

```
command DSL        internal/cli/command         a command: flags, help, checks, run, render
  endpoint DSL     internal/controller/endpoint  adds a route, a spec and auth to each method
    behavior DSL   internal/behavior             adds a target, a job and a host to each method
```

Each layer embeds the layer above it. A behavior method is an endpoint method,
and an endpoint method is a command. Thus a rule of the command layer, such as
"a value is a flag, not a positional argument", holds for each command of the
binary, and is written one time.

A local command has no route. Its method runs in the CLI process, with the deps
that the CLI gives it, such as the file system and the config. An endpoint
method sends a request to the API. A behavior method sends a job through the
API. The command layer does not know which: it decodes the flags into the input
type, calls the method, and renders the output.

## Where a DSL lives

A DSL lives under the process that runs it:

| DSL       | Runs in                                            | Lives at                        |
| --------- | -------------------------------------------------- | ------------------------------- |
| Commands  | the CLI                                            | `internal/cli/command/`         |
| Endpoints | the controller                                     | `internal/controller/endpoint/` |
| Behaviors | the controller (the route) and the agent (the job) | `internal/behavior/`            |

A behavior is top-level because it is in two processes. Its definition makes a
route of the controller, a command of the CLI and the dispatch of the agent.
Under `internal/agent/` or `internal/controller/`, it would be in one process,
and the other process would import it from there. `internal/job/` is top-level
for the same reason. Its groups follow the same rule: the endpoint groups are in
`internal/controller/endpoints/`, the behaviors in `internal/behaviors/`, and
the command groups in `internal/cli/commands/`.

## The layout

The layout is the layout of the endpoints:

```
internal/cli/
  command/                 the DSL and its runtime (from internal/controller/endpoint/command)
    gen/                   the generator of the cobra commands (from endpoint/gen/commandgen)
  commands/
    all/                   imports each group; gen/ registers each command
    token/
      gen/                 cli.go, generated
      mocks/
      deps.go              what the methods use, as interfaces
      methods.go           the functions of the methods
      methods_public_test.go
      token.go             the definition
      types.go             the inputs and outputs
    config/
    nats/
    ...
cmd/
  root.go                  the root command, the persistent flags, Execute
  commands.go              Provide for each group, and AttachLocal
```

Each group of local commands has its own directory, as each endpoint group has.
The 40 files hold these groups: `agent`, `behavior`, `config`, `controller`,
`init`, `nats`, `skill`, `start`, `token` and `version`. Three of the files are
shared code, not commands: `guide.go`, `metrics_server.go` and `shutdown.go`.
They go to `internal/cli`. `behavior` and `controller endpoint` are commands
about the DSLs. They stay beside the DSLs that they read, as now.

A group has no code for its output. Each command prints from the output type of
its method ([the CLI](cli.md#output-comes-from-the-output-type)). No command has
a renderer.

## The definition

The token group, as `internal/cli/commands/token/token.go` has it, cut short:

```go
var Group = command.Register(command.Define(
	"token", "Generate and validate API tokens",
	command.Uses[Deps](),
	command.SubDoc("roles", "Read the roles and what each grants"),
	command.Method[GenerateInput, GenerateOutput]("generate").
		Short("Generate a new token").
		Example("--subject user123 --roles=read").
		Fails("no roles", GenerateInput{Subject: "ops"}).
		Fails("an unknown role", GenerateInput{Roles: []string{"root"}, Subject: "ops"}).
		Handle(Generate),
	command.Method[RolesInput, RolesOutput]("list").
		Sub("roles").
		Short("List the roles and the permissions each grants").
		Handle(Roles),
	command.Method[ValidateInput, Claims]("validate").
		Short("Validate a token for authenticity and claims").
		Example("--token eyJhbGciOiJIUzI1NiIs...").
		Fails("no token", ValidateInput{}).
		Handle(Validate),
))
```

- **A group** is the first word of each command, such as `token`. `Under(...)`
  puts a group under a different command.
- **A method** is one command, with its input and output types. `.Sub("roles")`
  puts it under a word of its own, so `list` above is `token roles list`.
  `SubDoc("roles", "...")` is the one line of help of the `roles` command. Each
  input field is a flag, named for its json name with `_` as `-`. A field has a
  validate tag, a `doc` for its help, and an optional `short` for a one-letter
  flag. A field tagged `validate:"required"` is a required flag. The rules are
  the rules of `internal/validation/rule`, which endpoints and behaviors use. A
  value that breaks a rule is a usage error, exit code 2, before the handler
  runs.
- **`.Fails(doc, input)`** gives an input that breaks a rule of the input. Each
  rule of each field needs one, as for an endpoint and a behavior. A test runs
  each one, and expects the usage error.
- **`.Handle(fn)`** sets the function, `func(ctx, Deps, In) (Out, error)`.
- **`Uses[Deps]()`** names what the methods use, as interfaces. The CLI gives
  them with `command.Provide(token.Group, func() token.Deps {...})` in
  `cmd/commands.go`, which then calls `command.AttachLocal`. A group whose Deps
  has fields and no Provide fails when it runs. An empty Deps needs no wiring.
- **The output** prints from the output type of the method, with the tags of its
  fields. A renderer, `command.Render(Group, "method", fn).Because("...")`, is
  only for a shape that no output type gives. With `--json`, a command prints
  its output, and a renderer does not run.

In the code, a command of any layer is the interface `command.Command`, and a
group is `command.Group`. The endpoint types implement both.

## What it generates

`go generate ./internal/cli/commands/all` writes, for each group:

| File                                       | Has                                                      |
| ------------------------------------------ | -------------------------------------------------------- |
| `internal/cli/commands/<group>/gen/cli.go` | a cobra command for each method, its flags, help and run |
| `internal/cli/command/testdata/scaffold/`  | the golden files of `osapi cli command new`              |
| `internal/cli/commands/all/gen/gen.go`     | the registration of each group                           |
| `docs/docs/sidebar/usage/cli/<group>/`     | the CLI pages, from cobra                                |

The endpoint generator writes the `cli.go` of an endpoint group with the same
code.

## The commands

The commands are under the binary that they belong to:

```sh
osapi cli command list                      # the groups and their commands
osapi cli command get --name token          # the commands of a group, their flags and checks
osapi cli command spec                      # each part of the DSL, and when to use it
osapi cli command validate                  # the rules of each definition, each with its fix
osapi cli command new --name x --description "..."  # a new group that passes its tests
```

`spec` and `validate --help` come from the tables of `internal/guide`, as the
commands of endpoints and behaviors do: `command.Spec` and `command.Checks`. A
test fails on an exported option of the DSL with no term in `command.Spec`, and
on a rule of `Validate` with no check. Thus the skill learns the DSL from the
binary, and the help cannot fall behind the code.

`osapi cli command list` shows each command of the binary, also the commands of
the endpoints and the behaviors, and which layer made each one.

## The checks

`osapi cli command validate` fails a definition when:

- an input field has no validate tag, or no `doc`
- a rule of an input field has no `.Fails` that breaks it
- a command has no `Short`, or a method with input has no `Example`
- a value is a positional argument (`Args` is always `cobra.NoArgs`)
- the last word of a command is not a CRUD verb or a listed action, as
  `TestCommandShape` checks today
- a flag name is not the json name of its field
- the handler does not have the signature of the method
- a `.Sub` segment that makes a command of its own has no `SubDoc`, so its help
  would say `Roles commands`

Each check has its rule and its fix, as for endpoints.

## The order

1. **Turn the runtime over.** Built (osapi-io/osapi#901). The runtime and its
   generator worked on `*endpoint.Group` and `*endpoint.Method`, so they could
   not only move: the command layer would import the layer that embeds it. The
   command layer has its own interfaces, `command.Group` and `command.Command`,
   and the endpoint types implement them. The registry, `Attach`, the renderers,
   the output and the generator are in `internal/cli/command`. The request to
   the API (`Run`, `Build`, `Use`) stays in the endpoint layer, which hands its
   answer to the command layer's output. No command changed.
2. **One local group.** Built (osapi-io/osapi#902). `token` moves to a
   definition. Its three commands keep their names, flags and output. Their help
   as JSON is compared with the hand-written commands, as the agent group's was.
3. **The commands of the DSL, and its skill.** Built (osapi-io/osapi#902).
   `osapi cli command list`, `get`, `spec`, `validate` and `new`, with the
   tables in `internal/guide`. A dev skill, `build-a-command`, goes beside
   `build-a-behavior` and `build-an-endpoint`. It keeps only judgment, and sends
   the agent to `spec` and `validate` for each fact.
4. **The other groups**, one in each pull request: `config`, `version`, `nats`,
   `skill`, `init`, `start`, `agent` and `controller`.
5. **Output from the output type.** Built (osapi-io/osapi#903), as
   [the CLI](cli.md#output-comes-from-the-output-type) says. The behavior
   layer's `Columns` and its formats moved to the command layer, so a behavior's
   table and an endpoint's table are made in one place. A behavior registers no
   renderer: the behavior runtime adds one group printer for the result table.
   The hand-written renderers went, and five stay with their reason. Golden
   tests hold the output of each shape. The output of each command was compared
   before and after, from fixed data.
6. **The last renderers.** Built (osapi-io/osapi#904). Each response that the
   CLI reshaped changed instead: `agent list` (the API always gives `state` and
   only the true conditions), the job commands (the operation is `{type, data}`,
   the target is always set, and the responses and agent states are lists),
   `health status` (each registry entry has its sub-components, and the checks
   of NATS and KV are `checks`) and `telemetry trace get` (the controller
   answers the span tree). `client controller status`, `client nats status` and
   `client agent status` are generated from a `status` method in their endpoint
   groups. No command has a renderer.

## Not decided

- Some local commands run for a long time: `agent start`, `controller start`,
  `nats server start`. They have no output, and they stop on a signal. The DSL
  can have a method kind for a process, or these stay code in their groups.
- `cli-docs` and `help` read the whole tree. They can be methods that get the
  root as a dep, or stay in `cmd/`.

## What this page does not cover

- The rules for names, flags and output: [the CLI](cli.md).
- The endpoint and behavior DSLs: [endpoints](endpoints.md) and
  [behaviors](behaviors.md).
- The node domain commands, which go with
  [the behavior migration](behavior-migration.md).
