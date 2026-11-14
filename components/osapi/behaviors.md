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

A behavior lives under `internal/behaviors/<name>/`. Its definition is one call:

```go
var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters managed under /etc/sysctl.d",
    behavior.Node,
    behavior.API,
    behavior.CLI,
    behavior.Read("list", List).Describe("List the kernel's parameters and which osapi manages"),
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

The package registers itself when imported, and `internal/behaviors/all` imports
every behavior. Adding one is a directory and a line in `all.go`.

Every behavior's directory has the same files: `behavior.go` for the definition,
`types.go` for the input and output types, `methods.go`, `provider.go`, one
`<platform>.go` per platform such as `debian.go`, an optional `settings.go`,
`mocks/` for the provider's double, and `gen/` for what is generated from them.
Every file with code has a test named for it, the house rule for the rest of the
repository: `methods_public_test.go` calls each method on the mocked provider,
and `debian_public_test.go` tests the Debian provider. The platform files sit
beside the definition rather than in a subdirectory, as the hand-written
providers' `debian.go`, `darwin.go` and `linux.go` do. The layout and the tags
are written for authors in osapi's `docs/docs/sidebar/development/behaviors.md`;
this page records why it is built the way it is.

## What the definition decides

| Declared                    | Decides                                                                                                                                                          |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `behavior.Node`             | The work runs on a host, through the job system. It is the only placement                                                                                        |
| `behavior.Under("network")` | Nests the behavior: `/api/node/{hostname}/network/dns`, `osapi client node network dns`                                                                          |
| `Read`                      | `GET`, the `<group>:read` permission, no `changed` in the result                                                                                                 |
| `Write`                     | `POST`, or `PUT` for `update` and `DELETE` for `delete`, and the `<group>:write` permission                                                                      |
| `.Key("key")`               | The input field addressed in the path, `/{key}`                                                                                                                  |
| `behavior.API`              | Routes, its part of the OpenAPI spec, and the API reference pages                                                                                                |
| `behavior.CLI`              | Generated commands and CLI docs pages. It needs `API`, because the commands call the API                                                                         |
| `.Describe`, `.Explain`     | The one-line description, and the longer text a command's help, its docs page and the spec carry                                                                 |
| `.Example`                  | Sample calls. The docs pages are these, run through the CLI's renderer, and so are the tests                                                                     |
| `behavior.Config(v)`        | Settings under `behaviors.<name>`, with `v` as their defaults                                                                                                    |
| `behavior.Platform(p, f)`   | How the provider is built on platform `p`: a distribution, `darwin`, or `linux` for every Linux host without its own. On any other, the methods report `skipped` |
| `behavior.Sudo("prog")`     | A program the provider runs with sudo, which the agent's preflight checks                                                                                        |
| `behavior.Runs("prog")`     | A program the provider runs without sudo; the agent warns at startup when it is missing                                                                          |
| `behavior.Validator(...)`   | A `validate` tag of the behavior's own: its check, its schema and its message                                                                                    |

The permission prefix is the group when there is one and the behavior's name
otherwise, so `dns` under `network` needs `network:read`, as it does today.

What the controller answers itself, audit, jobs, agent enrollment and health, is
not a behavior and has no placement. It never reaches a host.

`API` and `CLI` are separate because not every behavior is called from outside.
One that only other behaviors use has neither, and is reachable through the job
system alone.

`internal/behaviors/behavior.go` holds `Path`, `HTTPMethod`, `Permission` and
`Command`, which turn a definition into those four. For sysctl they give the
same routes and permissions the hand-written API serves today.

## Types become JSON Schema

`behavior.SchemaFor` reads a Go type's tags: `json` names the field, `doc`
describes it, and `validate` gives the constraints. Standard tags map directly:
`required`, `min`, `max` and `len` by the field's type, `oneof` to an enum, and
`ip`, `url`, `email`, `hostname`, `uuid` and `cidr` to formats.

A custom validator is a Go function, and nothing can read a schema out of one.
So each custom tag is registered with the schema it means. A behavior declares
its own in its definition, check, schema and message together:

```go
behavior.Validator("motd_text", noEscapes, behavior.Pattern(`^[^\x1b]*$`),
    "is not a valid message: it has an escape sequence")
```

`internal/validation` registers each one with the validator the server uses,
through `behavior.OnRule`, whichever package initialises first. The tags the
hand-written domains use, `sysctl_key` among them, stay in `internal/validation`
with `behavior.ValidatorSchema` beside each, because those domains use them too;
`sysctl_key` moves to the behavior at its cutover.

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

- **The API.** Each behavior with `API` gets generated code in its `gen/`:
  `api_<method>.go` holds the method's handler and the decoder that builds its
  typed input from the path, query and body and checks its tags, and `api.go`
  holds the route table, each route's HTTP method, path and permission, which
  its `init` registers. The runtime they call,
  `internal/controller/api/behavior`, is written once: it checks the token
  against the route's permission, validates the target, queues the job and
  shapes the `{job_id, results[]}` envelope. An earlier version served every
  method through one handler that read the definition when osapi started. It
  worked, but nothing per endpoint could be opened, debugged or tested on its
  own, and the HTTP tests were a loop no file named. Generating a handler per
  method gives each endpoint a file and a test file, the shape of the
  hand-written domains.
- **The agent.** `internal/agent/processor_behavior.go` builds each behavior's
  provider once at startup, for the agent's platform, from what the definition
  declares with `behavior.Platform`, and runs any behavior's methods with it. A
  platform matches exactly first. Failing that, any host but macOS gets the
  provider declared for `linux`, since the agent runs on Linux and macOS only:
  `platform.Detect` names the Debian family `debian` and other distributions by
  their own name, so without the fallback a behavior that works the same on
  every distribution would need a line per distribution. The builder gets a
  `host.Host`, from `internal/behavior/host`: the platform, the filesystem, the
  command runner, the file state store, the hostname and the behavior's
  settings. A behavior with no provider on the platform, or whose builder
  returns `provider.ErrUnsupported`, has its methods reported as `skipped`, and
  the agent logs which it built. The built providers go in the agent's registry,
  which wires facts into them as into every other provider.
- **The CLI.** `internal/cli/behavior` holds the one helper every generated
  command calls, and the one table layout every behavior renders in. It sits
  under `internal/cli` as the API runtime sits under `internal/controller/api`,
  and generated code imports the two as `behaviorcli` and `behaviorapi`.

Behaviors live under `internal/`: the framework in `internal/behavior/`, with
what builds or tests a definition in subdirectories (`host`, `behaviortest`,
`openapi`, `gen`), and the behaviors themselves in `internal/behaviors/<name>/`,
a grouped one under its group as its routes are, so a behavior's directory
mirrors its URL. Each runtime's test helper sits beside the runtime it drives:
`internal/controller/api/behavior/apitest` and `internal/cli/behavior/clitest`.
`behavior validate` refuses a behavior or group named `all`, which is the
registration index in `internal/behaviors/all`. Nothing outside osapi imports a
behavior: the SDK talks to the HTTP API, and the spec describes everything a
client needs, so `pkg/` holds only the SDK and imports nothing from `internal/`.
`just go-pkg-check`, run by `just test`, fails when it does. An earlier version
kept behaviors in `pkg/behavior` because the SDK's generic call took a
behavior's definition; that call is now a plain `Client.Request` to an API path,
and the CLI runtime, which knows behaviors, builds the path.

Inside, the same habits hold. `host.Exec` is the part of the command runner a
provider calls, declared in `host` where providers use it, so the agent's runner
and the fake host's generated mock both satisfy it. The errors a provider
returns that the API answers differently, `ErrUnsupported`, `ErrNotFound`,
`ErrNotManaged` and `ErrNotInstalled`, are `internal/behavior`'s, and
`internal/provider` gives the hand-written providers the same values under its
own names. The file-state record, `managedfile.State` and its key
`managedfile.StateKey`, belongs to `managedfile`, the behavior that owns managed
files, and the hand-written providers and the controller read it from there.

Permissions and sudo come from the definitions too. `internal/authtoken` builds
the known permissions and each built-in role's from the hand-written lists plus
every registered behavior's methods: `admin` and `write` get a behavior's read
and write, `read` gets its read. The agent's preflight checks every program a
behavior declares with `Sudo`, beside its own list, and the agent warns at
startup about any program declared with `Runs` that is not installed: a missing
one fails only that behavior, so it does not stop the agent. Neither is a list
anyone edits for a behavior. The fake host fails an example that runs a program
without its declaration, counting the programs the behaviors it requires
declare, and the integration test fails when its image lacks a declared program.

A behavior is served under `/api` and `osapi client node`, and its jobs are in
their own `behavior` category, whose operations are `behavior.<name>.<method>`.
Its `gen/api.yaml` joins the main spec, so the SDK client, the UI client and the
API docs cover it. One that replaces a hand-written domain is marked
`behavior.Next` while both exist: its routes are under `/api/next`, its commands
under `osapi client next`, its spec is `gen/api.next.yaml`, which the join does
not read, and the combined `internal/controller/api/next/gen/api.yaml` holds
every `Next` behavior. The hand-written routes, commands, spec and docs are not
touched, so the behavior can be compared with the domain it will replace on the
same server. sysctl is marked so until its cutover.

The cutover is removing the mark and following what fails. A test in
`internal/behaviors/all` fails while a behavior that is not `Next` shares a
route with a hand-written spec, and names that domain's directory; the CLI
refuses to start while a hand-written command has a behavior command's name; the
compiler finds the processor case; and `behavior-gen-check` fails until
`just generate` has joined the spec and regenerated the clients from it.

A test holds that comparison for every domain being migrated.
`TestOpenAPIParity` in `internal/behavior/openapi/openapi_public_test.go`,
beside the code that builds the spec, has one row per behavior that replaces a
hand-written domain, naming that domain's spec. For each row it generates the
behavior's spec and compares it with the hand-written one: every operation's
path without `/next`, verb, operationId, scopes, parameters, request body and
response codes, and every schema property's type, format, enum and whether it is
required. Prose and constraints are left out, because the generated spec words
things differently and carries constraints the old one omitted.

A domain's row is added when its behavior is built and deleted with its
hand-written spec at the cutover. The table is the list of domains still
mid-migration, and when it is empty the test is deleted.

## Generated, and committed

`go generate ./internal/behaviors/all` runs `internal/behavior/gen`, which
writes:

| File                                             | Holds                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `internal/behaviors/<name>/gen/api.go`           | the route table, registered from `init`                                                                   |
| `internal/behaviors/<name>/gen/api_<method>.go`  | the method's handler and the decoder for its typed input                                                  |
| `internal/behaviors/<name>/gen/cli.go`           | the behavior's commands, flags bound to input fields                                                      |
| `internal/behaviors/<name>/gen/*_public_test.go` | a test for each of those files, described under the tests below                                           |
| `internal/behaviors/<name>/gen/api.yaml`         | the behavior's spec, which `just generate` joins into the main one; `api.next.yaml` for a `Next` behavior |
| `internal/behaviors/all/gen/gen.go`              | the import of every behavior's generated code: its routes and commands                                    |
| `internal/controller/api/next/gen/api.yaml`      | one spec for the behaviors marked `Next`, while any is                                                    |
| `docs/docs/sidebar/behaviors/<name>/`            | the behavior's page, with its settings, and a page per method                                             |

The code is generated into files rather than built when osapi starts, so a
reviewer reads and diffs exactly what a route or command does, the way
oapi-codegen's output is read today. It lives in the behavior's own `gen/`,
keeping everything about a behavior in its directory, and `gen/` holds nothing
written by hand.

The generator builds Go with jen (`github.com/dave/jennifer`) rather than text
templates. Templates splice strings, so a template that renders code that does
not parse, or forgets an import, fails only when the output is compiled; jen
builds the code as statements and manages the imports. The output then goes
through goimports, gofumpt and golines, so it reads, and passes the format
check, like the rest of the repository. Kubernetes' code-generator was the other
candidate and was left: it reads comment markers on type declarations, and a
behavior's examples and refusals are values no marker can carry.

The spec is built with kin-openapi's `openapi3` types, the library oapi-codegen
reads specs with, rather than as ordered maps, and a test loads the written spec
back and validates it. Keys come out in kin-openapi's order, alphabetical,
rather than the order a person would write them.

`osapi behavior new` still writes its starting files from templates. Those are
not generated code: they are a person's to edit from the first minute, so they
are kept as the Go source they produce, where a reader can see the result.

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
`just behavior-cover-check`, also in `just test`, holds each behavior package to
100% coverage on its own, since the repository's 99.9% is a total that one short
behavior can pass.

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
osapi behavior list                               # the behaviors and their methods
osapi behavior get --name sysctl                  # surfaces, methods, types, settings, telemetry
osapi behavior get --name sysctl --method update  # one method in full
osapi behavior validate                           # every definition against the rules
osapi behavior new --name motd --description "x"  # write a new behavior's layout
osapi behavior new --group network --name neighbors --description "x"  # under a group
```

Each takes `--json`, and values arrive as flags, as everywhere in the
[CLI](cli.md). `get` shows whether the behavior has an API and a CLI and where
they are served today, what it uses (empty until behaviors can require one
another), and for each method its verb, route, permission, command, input and
output fields and examples, its settings with the `agent start` flag for each,
the platforms it has a provider for, the programs it runs with sudo, its
refusals, and the span and metrics its calls record.

`behavior new` writes `internal/behaviors/<name>/` as a working behavior that
keeps a value in a file, with every standard file, and adds its import to
`internal/behaviors/all`. It builds, validates, lints and passes every test with
100% coverage before anything is changed, so the layout is stated once, in code,
and an agent starts from a correct skeleton rather than a description of one.
`osapi token roles` lists every permission and which roles grant it, behaviors'
included, as the binary has them. `--json` gives the input and output as JSON
Schema, which is what an agent reads before building a request. Tables render
through [the CLI's output style](cli.md#output-style).

## The rules validate checks

`behavior validate`, from `internal/behaviors/validate.go`, fails a definition
the platform could not build from. Each problem names its rule:

| Rule        | Fails when                                                                                                                                                        |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`      | a behavior, group or method name is not lowercase letters, digits and dashes                                                                                      |
| `placement` | the behavior has no placement                                                                                                                                     |
| `doc`       | the behavior or a method has no description                                                                                                                       |
| `methods`   | the behavior has no methods                                                                                                                                       |
| `duplicate` | two behaviors share a name, or a method is declared twice                                                                                                         |
| `key`       | `.Key` names a field the input does not have                                                                                                                      |
| `schema`    | an input or output type has no JSON Schema, such as an unregistered tag, or an input is not a struct                                                              |
| `output`    | the output is not a struct or slice of structs, or declares `hostname`, `status` or `error`, which every per-host result already carries                          |
| `changed`   | a write's output has no `changed` boolean                                                                                                                         |
| `surface`   | the behavior has `CLI` without `API`, is `Internal` and served, or a CLI behavior's input has a field no flag can hold, such as a list                            |
| `platform`  | the behavior declares no provider, declares a platform twice, or a platform's provider does not implement a method's provider type                                |
| `example`   | an example or refusal is not the method's types or has no description, a refusal has no error text or declares effects, or a CLI behavior's method has no example |
| `verb`      | a method is named with a synonym, such as `remove` or `add`, rather than the verb it stands for                                                                   |
| `route`     | two methods would be served at the same route and HTTP method                                                                                                     |
| `settings`  | settings declared with `Config` are not a struct, or a field has no `mapstructure` name or no `doc`                                                               |
| `secret`    | an input field is tagged both `secret:"true"` and `telemetry:"attr"`, which would record a secret on a span                                                       |
| `requires`  | a required behavior is not registered, or behaviors require each other in a cycle                                                                                 |

It exits 1 when any rule fails. It is the check an agent runs after writing a
behavior, before the tests.

## Settings a behavior declares

Some behaviors need configuration and most do not, so settings are optional and
belong to the behavior that reads them:

```go
type Settings struct {
    Dir string `mapstructure:"dir" doc:"..." validate:"required,startswith=/"`
}

var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters managed under /etc/sysctl.d",
    behavior.Node,
    behavior.Config(Settings{Dir: "/etc/sysctl.d"}),
    ...
))
```

The struct carries the same `mapstructure`, `doc` and `validate` tags as osapi's
own config, and the value passed is the defaults. From that one declaration:

| Where                    | What appears                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| The config               | keys under `behaviors.<name>`, with defaults and `OSAPI_BEHAVIORS_<NAME>_*`               |
| `osapi agent start`      | a flag per setting, `--<name>-<field>`, bound to its key the way `agent.go` binds its own |
| `config list` and `get`  | each setting with its value, source and description                                       |
| `config validate`, start | its `validate` tags, checked with the rest of the config                                  |
| `behavior get`           | a Settings block: key, flag, env var, type, default                                       |
| The docs site            | a settings table on the behavior's page                                                   |
| The agent                | `behavior.Settings[T](Behavior)`, the decoded struct                                      |

There is no ordering problem in this. Behaviors register in package `init`,
before `main`, so the flags exist when cobra parses the command line, and
`initConfig` runs after that and walks the same registry. `BindPFlag` only
records the mapping; viper resolves flag, then environment, then file, then
default when the config is decoded.

Settings are not inputs. A method's input is per call, a flag on the client
command that is never bound to the config, so a value in a file can never pick
what a write acts on. A setting is standing configuration of the process that
reads it, and the agent is the process that runs a behavior's methods, so the
flags go on `agent start`. A flag on a client command would change nothing on
the host.

sysctl's one setting is `behaviors.sysctl.dir`, the directory its conf files are
written to, which was a constant in the Debian provider before. A provider
builder reads settings from the host it is given, `host.Settings[Settings](h)`,
because the behavior's own variable cannot be named inside its initialiser. The
hand-written sysctl domain's provider, built in `createSysctlProvider`, reads
the same setting, so both write to the same directory.

## Tests a behavior gets from its definition

A behavior's examples are its tests at every layer above the provider. An
example can say what the host looks like before the call, with `After` (another
method run first), `Prints` (a command's output), `PrintsAfter` (its output once
another command has run) and `Exists` (a file), and what the call changes, with
`Wrote`, `Removed` and `Ran`. `PrintsAfter` is for state a program keeps rather
than a file: a package query prints "not installed" until the install runs and
"installed" after it, which the second-run check needs to see. The skill's
`aptpkg` eval found the gap: without it, a package behavior's install example
could not pass that check honestly, and the session stopped and said so.

| Layer       | Where                                              | Checks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Provider    | `behaviortest.Run`, from `behavior_public_test.go` | each example on a fake host per platform gives its output and effects; a write declares effects and reports `changed: false` run twice; each command and store call failing in turn never panics                                                                                                                                                                                                                                                                                                                                     |
| API         | `gen/api_<method>_public_test.go`, generated       | a table of literal requests through the real handler and middleware with the job client mocked, every response validated against the generated spec with kin-openapi: each example on one host and broadcast, with its body; the host skipping, failing or timing out; the job client failing (500); a missing item (404); a bad target, each missing required field, a body that is not JSON, a field of the wrong type and each refusal the API can see (400, no job queued); a missing token (401) and a missing permission (403) |
| Routes      | `gen/api_public_test.go`, generated                | every method's HTTP method, path and permission                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| CLI         | `gen/cli_public_test.go`, generated                | each example's flags, given to the generated command, send the example's input                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Wiring      | `internal/behaviors/all/all_public_test.go`        | every registered behavior validates, every route is mounted and every command attached                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Live server | `test/integration/behavior_test.go`                | every unkeyed read against a real agent; the write examples with `OSAPI_INTEGRATION_WRITE_BEHAVIORS=1`, each reporting the example's `changed` and then `false`; `just behavior-int-linux` runs them on Debian in a container, since the CI agent cannot write `/etc`                                                                                                                                                                                                                                                                |

The generated HTTP tests split each method's cases the way the hand-written
domains' handler tests do: `Test<Method>` for the answers,
`Test<Method>ValidationHTTP` for the 400s and `Test<Method>RBACHTTP` for the
tokens. `internal/controller/api/behavior/apitest` runs the rows. A failing
generated test is fixed in the definition or the generator, never in `gen/`.

The fake host is `internal/behavior/behaviortest`: an in-memory filesystem, a
command runner that records each command line and prints what `Prints` gives,
and an in-memory file state store. The command runner and the store are the
repository's generated mocks, configured by the harness, and a call they have no
answer for is reported rather than faked. Coverage is measured per package, so
the harness runs from the behavior's own test, one line `behavior new` writes.
The methods and each platform's provider also have their own tests, so every
file with code has one, the repository's rule.

Every string input field of every example is also probed, one at a time, with a
path that climbs out of its directory, a value that starts a new line, and a
value that reads as an option. A probe passes when the field's `validate` tags
refuse it, as the API would, when the method fails, or when it changes nothing
it should not; it fails when it writes outside the directories the example
writes, puts its line in a file beside other content, reaches a command as an
option with no `--` before it, or reaches a `sh -c` script. Declared refusals
only cover the inputs an author thought of; the probes cover the three ways a
string most often becomes an injection, for every behavior, without the author
thinking of them. An internal behavior is not probed: its input comes from other
behaviors. The free-text case is allowed: a file whose whole content is the
value, as a message of the day is, may hold any line.

A method declares what it refuses with `.Fails(doc, input, errorText)`, with the
same host options: bad input, or state it cannot act on, such as a parameter
osapi stopped managing. The provider test checks each fails with that text, the
API test checks one whose input breaks a `validate` tag gets a 400 with no job
queued, and the docs page lists them. On the fake host every filesystem, command
and store call fails in turn, and every store read returns a damaged record in
turn: not JSON, empty JSON, and a file state record with empty metadata.

sysctl's examples and refusals reach 150 of the 152 statements of its Debian
provider, against 152 for its 1,820 lines of hand-written tests. The two left
are a JSON encoding error that a struct of strings cannot produce, reachable
only through the test seam the hand-written tests use.

```sh
go test ./internal/behaviors/sysctl -run TestBehaviorPublicTestSuite/TestExamples -coverprofile=c.out && go tool cover -func=c.out | grep debian.go
```

## Behaviors built on other behaviors

A behavior that needs another's work declares it with `behavior.Requires`, and
calls the other's methods as Go calls on the same host, inside the same job:
there is no second job, no API call and no round trip.

```go
var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters, written to sysctl.d files and applied",
    behavior.Node,
    behavior.Requires(managedfile.Behavior),
    behavior.Platform("debian", newDebian),
    ...
))
```

- **Building.** `host.Build` builds each required behavior's provider first, for
  the same host, and puts it in the host the requiring builder gets; the builder
  reads it with `host.Require[P](h, managedfile.Behavior)`. The agent and the
  fake host in `behaviortest` both build through it, so a behavior's examples
  run through its requirements exactly as they do on an agent.
- **Unsupported spreads.** A required behavior with no provider on a platform,
  or one that declines the host, leaves the requiring builder without it; the
  builder answers `provider.ErrUnsupported`, and its methods report `skipped`. A
  required builder that fails fails the requiring one, with both names in the
  error.
- **Internal.** `behavior.Internal` marks a behavior that only other behaviors
  use. It has no route, no command, no spec and no permissions, and
  `behavior validate` fails one that also declares `API` or `CLI`. It still has
  examples, refusals, tests and a docs page, and `behavior list` marks it.
- **Checks.** `behavior validate` fails a requirement that is not registered,
  and a cycle, under the rule `requires`. `behavior get` lists what a behavior
  uses and what uses it, and the Behaviors section's landing page carries a
  table of every behavior with both, generated from the registry.

`managedfile` is the first internal behavior: files osapi writes on a host and
keeps a record of in `file-state`. A caller sets the file's mode, owner and
group, and marks content that is a secret, whose record then keeps no checksum
of it: a short secret's SHA-256 can be recovered by guessing. Ownership is read
with `stat` and set with `chown` through sudo, which `managedfile` declares, so
the fake host tests it like any other command. The `apptoken` eval found it
missing: a token written through `managedfile` would have been readable by every
user on the host, and the session stopped rather than write it. sysctl's Debian
provider writes and removes its conf files through it, and the hand-written
sysctl domain builds its own `managedfile` provider, so both write the same
files with the same records. The code moved out of sysctl unchanged, which the
hand-written sysctl provider tests, untouched apart from two marshal-failure
cases that moved with the code, confirm.

Shared work becomes an internal behavior at its second use: one behavior doing
something is its own code, and a second that needs the same thing is when it
becomes a behavior both require. The build-a-behavior skill asks the question
before a behavior is written, and
[the migration plan](behavior-migration.md#internal-behaviors-the-migration-extracts)
lists the candidates the hand-written domains share.

Chaining across hosts or steps, the output of one method feeding the input of
the next, is a workflow, and stays osapi-orchestrator's.

## Secret inputs

An input field that carries a secret, such as a password or an API key, is
tagged `secret:"true"`. The tag does three things, so a behavior's secret is
kept out of everything that records or publishes it without editing anything
outside the behavior's directory:

- **Audit.** The audit summary redacts every field name tagged secret in any
  registered behavior, beside the fixed denylist in `internal/audit`. Without
  the tag, a field called `passphrase` would be stored as sent, because the
  denylist matches names and does not have that one.
- **Spec.** The field's schema has `format: password` and `writeOnly: true`, so
  a generated client and the API reference treat it as a secret.
- **Telemetry.** It is never recorded on a span. `behavior validate` fails a
  field tagged both `secret` and `telemetry:"attr"`, under the rule `secret`.

Redaction matches names, the way the denylist does: tagging a field `value`
secret redacts every request field called `value`, in every behavior. A secret
field gets a name that says what it holds.

The value still arrives as a CLI flag, as a hand-written domain's `--password`
does. Reading it from standard input or a prompt instead is not built.

## Not built yet

The cutover: routes moving from `/api/next` to `/api`, commands from
`client next` to `client`, the generated spec joining the main one, and sysctl's
hand-written handler, processor and commands being deleted. sysctl's provider
already lives in the behavior's directory, as `debian.go`, `darwin.go` and
`linux.go` with their tests moved unchanged, and the hand-written domain imports
it from there until the cutover.

The SDK knows routes, not behaviors: it has a generic `Client.Request` to any
API path, and its typed services, such as `client.Sysctl`, are hand-written over
the client oapi-codegen generates from the spec. Generating those typed services
from the spec too, once every behavior's spec has joined the main one, is a
later step in [the migration plan](behavior-migration.md).
