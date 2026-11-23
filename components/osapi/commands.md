# Commands

Built (osapi-io/osapi#901 to #904, #914 to #918 and #934). Each command of the
`osapi` binary comes from a definition in Go, as each endpoint and each behavior
does. The definition gives the cobra command, its flags, its help, its page, its
checks and its tests. Endpoints and behaviors get their commands from this
layer. Thus one DSL makes every command, and `cmd/` has only the root and the
wiring.

The issue is osapi-io/osapi#900.

## Why

When this plan was written, `cmd/` had 178 files. 121 of them were the commands
of the node domains, which went as each domain became a
[behavior](behaviors.md). A person wrote each of the other 57:

| Kind                                    | Files | Examples                                                                                           |
| --------------------------------------- | ----: | -------------------------------------------------------------------------------------------------- |
| Commands that run on the local machine  |    40 | `token generate`, `config validate`, `nats server start`, `agent start`, `behavior new`, `version` |
| Code of the CLI for the endpoint groups |    17 | the renderer of `client agent list`, `client agent status`, `client nats status`                   |

Now `cmd/` has 14 files. Each local command is a group under
`internal/cli/commands/`, and each node command comes from a behavior. `cmd/`
keeps the root, the parents `agent`, `cli`, `client`, `client node`,
`client node network`, `controller` and `nats`, and the wiring that gives each
local group its deps in `commands.go` and `process_deps.go`. It also keeps
`reference.go`, which makes the reference pages of the docs site from the output
of the list and get commands, the build version, and two tests of the command
tree.

The rest of this section tells why the layer was built.

A command that a person wrote got no check. Nothing told that a required flag
was marked, that the help had an example, that a value was checked, or that the
name obeyed [the CLI rules](cli.md). An endpoint and a behavior got these checks
from their definitions. A local command got none.

The skill had the same gap. An agent learned the endpoint DSL from
`osapi controller endpoint spec` and `validate`, and the behavior DSL from
`osapi behavior spec` and `validate`. Nothing taught it to add a local command.

The CLI layer was in the code already, in the wrong place.
`internal/controller/endpoint/command` was the runtime of each generated
command, and `internal/controller/endpoint/gen/commandgen` wrote them. Behaviors
used them through the endpoint layer. No command outside the two DSLs used them.

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

- **A group** is the first word of each command, such as `token`.
  `Under(command.ParentController)` puts a group under a different command. A
  parent is a `command.Parent` constant. Attach makes a word that has no
  command, so a misspelled parent was a new command at the root, and
  `osapi cli command validate` refuses a word outside `KnownParents()`. `Flat()`
  makes the group add no word: each method is a command under the group's
  parent, the root or the words of `Under`. Thus `version` is a flat group at
  the root, and its method `version` is `osapi version`. A command that stands
  alone under a parent that holds other things, such as
  `osapi controller start`, is a flat group `Under` `controller`. The group's
  name stays its identity, for its package and for `cli command get --name`.
  Where the command goes, `Under`, and whether the group adds a word, `Flat`,
  are two settings, so nothing is inferred from a name.
- **An example** names the flags of its command. `osapi cli command validate`
  refuses a flag that the command does not have, under the rule `help`: the flag
  of a field of the input (its `flag` tag, else its json name), its `short`
  letter, a field of the struct that `in:"body"` names, a config key that `Flag`
  names, or `--json`, `--debug` or `--osapi-file`. `command.InputFlags` lists
  the flags of an input, as the command generator declares them. A misspelled
  flag made a docs page show a command that fails.
- **A method** is one command, with its input and output types. `.Sub("roles")`
  puts it under a word of its own, so `list` above is `token roles list`. A
  method is its `Sub` and its name, so a group can have `get` and `spec get`.
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
- **`.Prints(sample)`** gives the example before it an output: a value of the
  output type of the method, in `samples.go` of the group, with each time in
  UTC. The CLI page of the command shows the sample as the CLI prints it, and as
  JSON for `--json`. A method that prints a body needs one, and validate fails a
  method without one. A method with no body needs none. Its page shows the one
  line, such as `web-01 draining`, for the key flag of each example.
- **`.Logs(lines...)`** gives the example of a process the lines that the
  process writes at the info level when it starts. Each line is a
  `command.LogLine`: a level, a message and its attributes. The lines are in
  `samples.go` of the group, and come from a real start with the default config.
  The generator writes them through `cli.LogHandler`, the handler that the root
  logs through, with color on. Thus the CLI page shows the lines as a terminal
  shows them, and then as JSON for `--json`. Validate fails a process with no
  `.Logs`, and `.Logs` on a method (osapi-io/osapi#1206).
- **`.Handle(fn)`** sets the function, `func(ctx, Deps, In) (Out, error)`.
- **`Uses[Deps]()`** names what the methods use, as interfaces. The CLI gives
  them with `command.Provide(token.Group, func() token.Deps {...})` in
  `cmd/commands.go`, which then calls `command.AttachLocal`. A group whose Deps
  has fields and no Provide fails when it runs. An empty Deps needs no wiring.
  `cli command spec get` lists each type that a `Deps` field has, under "What a
  Deps takes", with how a test replaces it: `memfs.New()` for `avfs.VFS`,
  `fstest.MapFS` for `fs.FS`, a value for the config, a function for a
  `func(...)` field, and a mockgen mock for an interface. A test fails on a
  field whose type has no entry. On 21 November 2026, three groups (agent,
  controller and NATS server) and the process tests of the DSL tested with fakes
  written by hand. They now use mockgen mocks.
- **The output** prints from the output type of the method, with the tags of its
  fields. A renderer, `command.Render(Group, "method", fn).Because("...")`, is
  only for a shape that no output type gives. With `--json`, a command prints
  its output, and a renderer does not run.

In the code, a command of any layer is the interface `command.Command`, and a
group is `command.Group`. The endpoint types implement both.

## What it generates

`go generate ./internal/cli/commands/all` writes, for each group:

| File                                       | Has                                                        |
| ------------------------------------------ | ---------------------------------------------------------- |
| `internal/cli/commands/<group>/gen/cli.go` | a cobra command for each method, its flags, help and run   |
| `internal/cli/command/testdata/scaffold/`  | the golden files of `osapi cli command new`                |
| `internal/cli/commands/all/gen/gen.go`     | the registration of each group                             |
| `docs/docs/sidebar/usage/cli/<group>/`     | the CLI pages, from cobra, with the output of each example |

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
  `TestCommandShape` checks today; a command of the root is a word of
  `command.Roots` instead
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
   `skill`, `init`, `start`, `agent` and `controller`. `version` is built
   (osapi-io/osapi#914): a flat group at the root, with the build of the binary
   as its output type. `osapi version --json` has snake_case keys, such as
   `version`, as the rest of the API does. `config` is built
   (osapi-io/osapi#915). Its `validate` returns its report with
   `command.Fail()`: the report prints, then the command exits 1. `command.Long`
   is the help of a group's command, as `CommandLong` is for an endpoint group.
   `skill` and `init` are built (osapi-io/osapi#916). `init` is a flat group at
   the root, and its path is `--path`, since each value is a flag. `skill get`
   prints a skill's file as it is: its `content` field is tagged
   `render:"body"`, which makes a field the whole output. `guide.go` holds the
   helpers of the commands that teach the DSLs, and moves with them. The long
   running commands are [processes](#processes). `controller key fingerprint` is
   built (osapi-io/osapi#918). It was `osapi client controller key fingerprint`,
   but it reads the key pair on the disk of the host and calls no API.
   `osapi client` is the commands that call the API, so the command is a local
   group under `osapi controller`. `nats setup` and `agent admission get` are
   built. `setup` is an action in `command.Actions`. `admission` is a noun, so
   its command is `agent admission get`, as each noun has a verb under it. The
   `cli command` commands are built (osapi-io/osapi#934): `list`, `get`,
   `create`, `spec get` and `validate`. Two of them are named by the rules.
   `spec` is a noun, so its command is `spec get`, as `node hostname get` is.
   `new` wrote a new group, which `create` says, so it is `create`; an action is
   only for what a CRUD verb does not say. `controller endpoint` and `behavior`
   have the same names. The `controller endpoint` commands are built:
   `get --openapi` printed a different thing from `get`, so it is a command of
   its own, `controller endpoint openapi get`. The `behavior` commands are
   built, and the commands that teach the DSLs are done (osapi-io/osapi#934).
   `get --method` printed one method in full where `get` prints the behavior, so
   it is a command of its own, `behavior method get`. The last local command,
   `cli-docs`, is `osapi cli docs generate`: a group under `cli` that gets the
   root command as a dep and writes the CLI reference pages. Thus each local
   command comes from a definition. `cmd/` keeps the root, the wiring and the
   parents of hand-written commands. The `client node` commands come from
   [behaviors](behaviors.md).
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

## Processes

A process is a command that runs until a signal, such as
`osapi nats server start`. It has no input and no output type. It writes log
lines, which `.Logs` puts on its page. The DSL declares it with
`command.Process("start").Setup(fn)`, and the generated command calls
`command.Serve`, in `internal/cli/command/process.go`.

One context goes through each command. `cmd.Execute` makes it, cancels it on the
first `SIGINT` or `SIGTERM`, and gives it to cobra. A command reads it as
`cmd.Context()`. A process uses it in three steps:

1. **Setup.** `fn` gets the context and the deps, and returns `command.Running`:
   the components, each with `Start()` and `Stop(ctx)`, and a `Cleanup`. `fn`
   makes the components and starts none of them. A signal during setup cancels
   the context, so a setup that waits, such as for NATS, stops. An error from
   `fn` is the error of the command, and it exits 1.
2. **Run.** `Serve` starts each component, then waits until the context ends.
3. **Stop.** The context is cancelled, so the stop cannot use it. `Serve` makes
   `context.WithoutCancel(ctx)` with `command.ShutdownTimeout`, 10 seconds. That
   context keeps the values of the first, such as the trace, but not its cancel.
   `Serve` stops the components together with it, then runs `Cleanup` with it.

A process never makes a context of its own. A second signal does nothing: the
timeout of the stop limits the shutdown.

A component that keeps the setup context for its goroutines stops them on the
signal, before its `Stop` runs. A component whose goroutines must run until
`Stop` makes their context itself, and cancels it in `Stop`.

Each process is built (osapi-io/osapi#917): `nats server start`, `agent start`,
`controller start` and `start`. A process's flags are config keys:
`.Flag("agent.max_jobs")` makes `--agent-max-jobs`, with the type, the default
and the doc of the key, and binds it to the key. The DSL package cannot read the
config, because the config imports the CLI through the behaviors. Thus the
generated command calls `config.BindFlags`.

Each start has a `Components` function, which makes its parts and starts none.
`osapi start` calls the three of them, with one tracer and the job namespace of
the controller, and adds the stop of the tracer with `command.Then`. Each debug
log of the config is still written in its setup.

## What this page does not cover

- The rules for names, flags and output: [the CLI](cli.md).
- The endpoint and behavior DSLs: [endpoints](endpoints.md) and
  [behaviors](behaviors.md).
- The node commands, which come from [behaviors](behaviors.md).
