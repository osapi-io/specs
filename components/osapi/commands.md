# Commands

A plan, not built. Each command of the `osapi` binary comes from a definition in
Go, as each endpoint and each behavior does. The definition gives the cobra
command, its flags, its help, its page, its checks and its tests. Endpoints and
behaviors get their commands from this layer. Thus one DSL makes every command,
and `cmd/` has only the root and the wiring.

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
      render.go            how each output prints without --json
      token.go             the definition
      types.go             the inputs and outputs
    config/
    nats/
    ...
cmd/
  root.go                  the root command, the persistent flags, Execute
```

Each group of local commands has its own directory, as each endpoint group has.
The 40 files hold these groups: `agent`, `behavior`, `config`, `controller`,
`init`, `nats`, `skill`, `start`, `token` and `version`. Three of the files are
shared code, not commands: `guide.go`, `metrics_server.go` and `shutdown.go`.
They go to `internal/cli`. `behavior` and `controller endpoint` are commands
about the DSLs. They stay beside the DSLs that they read, as now.

The renderer of an endpoint group goes in the group's directory, as
`internal/controller/endpoints/<group>/render.go`. It is in
`cmd/client_<group>.go` today. The renderer prints what the group answers, so
the group owns it.

## The definition

The token group, as it would be:

```go
var Group = command.Register(command.Define(
	"token", "Signed tokens for the API",
	command.Uses[Deps](),
	command.Method[GenerateInput, GenerateOutput]("generate").
		Short("Make a signed token").
		Long("The signing key comes from controller.api.security.signing_key.").
		Example("--roles admin --subject ops@example.com").
		Fails("an unknown role", GenerateInput{Roles: []string{"root"}}).
		Handle(Generate),
	command.Method[ValidateInput, Claims]("validate").
		Short("Check a token, and show its claims").
		Fails("no token", ValidateInput{}).
		Handle(Validate),
))
```

- **A group** is the first word of each command, such as `token`. A group can go
  under a different command, such as `controller endpoint` under `controller`.
- **A method** is one command, with its input and output types. Each input field
  is a flag, named for its json name with `_` as `-`. A field has a validate
  tag, a `doc` for its help, and an optional `short` for a one-letter flag. A
  field tagged `validate:"required"` is a required flag. The rules are the rules
  of `internal/validation/rule`, which endpoints and behaviors use.
- **`.Fails(doc, input)`** gives an input that breaks a rule of the input. Each
  rule of each field needs one, as for an endpoint and a behavior.
  `TestRefusals` runs each one, and expects the usage error, exit code 2.
- **`.Handle(fn)`** sets the function, `func(ctx, Deps, In) (Out, error)`.
- **`Uses[Deps]()`** names what the methods use, as interfaces: the file system,
  the config, the clock. A test gives fakes. Thus a local command is tested
  without a shell, as a handler is.
- **A renderer**, `command.Render(Group, "method", fn)` in `render.go`, prints
  the output without `--json`. A method without one prints its output as JSON.
  With `--json`, a command prints its output, and the renderer does not run.

An endpoint method gets all of these from the command layer, and adds its route.
Thus `.Command(short, long)` and `.Example` on an endpoint are the command
layer's `Short`, `Long` and `Example`.

## What it generates

`go generate ./internal/cli/commands/all` writes, for each group:

| File                                       | Has                                                      |
| ------------------------------------------ | -------------------------------------------------------- |
| `internal/cli/commands/<group>/gen/cli.go` | a cobra command for each method, its flags, help and run |
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

Each check has its rule and its fix, as for endpoints.

## The order

1. **Move the runtime.** `internal/controller/endpoint/command` and `commandgen`
   go to `internal/cli/command`. The endpoint DSL embeds them. The commands that
   it makes do not change: `TestCommandShape`, the help as JSON and the CLI
   pages show no difference.
2. **One local group.** `token` moves to a definition. Its three commands keep
   their names, flags and output. Their help as JSON is compared with the
   hand-written commands, as the agent group's was.
3. **The commands of the DSL.** `osapi cli command list`, `get`, `spec`,
   `validate` and `new`, with the tables in `internal/guide`.
4. **The other groups**, one in each pull request: `config`, `version`, `nats`,
   `skill`, `init`, `start`, `agent` and `controller`.
5. **The renderers.** Each `cmd/client_<group>.go` moves to the group's
   `render.go`.

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
