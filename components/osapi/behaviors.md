# Behaviors

A behavior is one area of a host that osapi manages, for example kernel
parameters. You declare it one time, as a typed definition. osapi builds these
parts of each method from that definition:

- the route
- the permission
- the dispatch on the agent
- the CLI command
- the OpenAPI spec
- the docs pages
- the telemetry

Nobody writes these by hand in each layer.

Behaviors replace [providers](providers.md), one domain at a time. sysctl is the
first. [The migration plan](behavior-migration.md) has the order of the others,
and the parts that are not built yet.

## Why

A new domain is slow to add, because most of the code connects layers and has no
logic. A measurement on `main` on 12 November 2026, before sysctl moved, found:

- `sysctl get` has 59 lines of logic in `debian.go`, and 312 hand-written lines
  around it: handler 153, validator 10, agent processor 28, SDK 56, CLI 63,
  operation constants 2. Its spec is 104 more lines of hand-written YAML.
- In the full repository, the handlers, agent processors, SDK and CLI are 47,792
  hand-written lines, against 15,189 lines of provider.
- The last three domain additions changed 130 files (`service`), 75
  (`certificate`) and 47 (the SSH key operations).

The connecting code is the same each time, and somebody types it again each
time. The `key` argument to `sysctl get` is declared by hand in eight locations.
Its pattern, `^[a-zA-Z0-9][a-zA-Z0-9._-]*$`, is written three times. The handler
sends the job payload as a `map[string]string`. The agent reads it back into an
anonymous `struct{ Key string }`. Nothing checks that the two agree.

The same shapes occur again and again in the codebase:

- 40 anonymous payload structs in `internal/agent`.
- 90 copies of the `ok`/`failed`/`skipped`/`timeout` switch in the handlers.
- 94 handlers that branch on `IsBroadcastTarget`.
- 136 hand-written SDK result types, with 127 functions that copy generated
  types into them.

The cost is clear, and it also blocks agents. An agent that must add a domain
must copy all of it from convention. An agent that must use osapi had nothing to
learn operations from, until `osapi init`, `help --json` and `behavior get`
existed. Those read the definitions.

## What a definition is

A behavior is under `internal/behaviors/<name>/`. Its definition is one call:

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

A method is a function. It takes a context, the provider of the platform and one
typed input. It returns one typed output or an error. `Read` and `Write` are
generic over those three types. Thus the definition has the Go types, and
nothing states them again.

The package registers itself when it is imported. `internal/behaviors/all`
imports each behavior. To add one, add a directory and a line in `all.go`.

The directory of each behavior has the same files:

- `behavior.go` for the definition
- `types.go` for the input and output types
- `methods.go`
- `provider.go`
- one `<platform>.go` for each platform, for example `debian.go`
- an optional `settings.go`
- `mocks/` for the test double of the provider
- `gen/` for the generated files

Each file with code has a test with its name. This is the rule for the rest of
the repository too. `methods_public_test.go` calls each method on the mocked
provider. `debian_public_test.go` tests the Debian provider. The platform files
are next to the definition, not in a subdirectory, as the `debian.go`,
`darwin.go` and `linux.go` of the hand-written providers are.

`docs/docs/sidebar/development/behaviors.md` in osapi describes the layout and
the tags for authors. This page records why the design is as it is.

## What the definition decides

| Declared                    | Decides                                                                                                                                                          |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `behavior.Node`             | The work runs on a host, through the job system. It is the only placement                                                                                        |
| `behavior.Under("network")` | Nests the behavior: `/api/node/{hostname}/network/dns`, `osapi client node network dns`                                                                          |
| `Read`                      | `GET`, the `<group>:read` permission, no `changed` in the result                                                                                                 |
| `Write`                     | `POST`, or `PUT` for `update` and `DELETE` for `delete`, and the `<group>:write` permission                                                                      |
| `.Key("key")`               | The input field addressed in the path, `/{key}`                                                                                                                  |
| `behavior.API`              | Routes, its part of the OpenAPI spec, and the API reference pages                                                                                                |
| `behavior.CLI`              | Generated commands, with their pages in the CLI reference. It needs `API`, because the commands call the API                                                     |
| `.Describe`, `.Explain`     | The one-line description, and the longer text that the help and the CLI page of a command, and the spec, carry                                                   |
| `.Example`                  | Sample calls. They are the examples of a command, and the tests                                                                                                  |
| `behavior.Config(v)`        | Settings under `behaviors.<name>`, with `v` as their defaults                                                                                                    |
| `behavior.Platform(p, f)`   | How the provider is built on platform `p`: a distribution, `darwin`, or `linux` for every Linux host without its own. On any other, the methods report `skipped` |
| `behavior.Sudo("prog")`     | A program the provider runs with sudo, which the agent's preflight checks                                                                                        |
| `behavior.Runs("prog")`     | A program the provider runs without sudo; the agent warns at startup when it is missing                                                                          |
| `behavior.Writes("...")`    | The paths the provider writes, removes or changes the mode of, as `path.Match` patterns; `"*"` is any path                                                       |
| `behavior.KeepsState`       | The provider keeps a record in the `file-state` bucket                                                                                                           |
| `behavior.Validator(...)`   | A `validate` tag of the behavior's own: its check, its schema and its message                                                                                    |

The permission prefix is the group when there is one, and the name of the
behavior when there is no group. Thus `dns` under `network` needs
`network:read`, as it does now.

The things that the controller answers itself (audit, jobs, agent enrollment and
health) are not behaviors, and have no placement. They never go to a host.

`API` and `CLI` are separate, because not each behavior is called from outside.
A behavior that only other behaviors use has neither. Only the job system can
get to it.

`internal/behaviors/behavior.go` has `Path`, `HTTPMethod`, `Permission` and
`Command`. They change a definition into those four values. For sysctl, they
give the same routes and permissions that the hand-written API serves now.

## Types become JSON Schema

`behavior.SchemaFor` reads the tags of a Go type. `json` names the field. `doc`
describes it. `validate` gives the constraints. The standard tags map directly:

- `required`, `min`, `max` and `len`, by the type of the field
- `oneof` to an enum
- `ip`, `url`, `email`, `hostname`, `uuid` and `cidr` to formats

A custom validator is a Go function, and nothing can read a schema from it. Thus
each custom tag is registered with the schema that it means. A behavior declares
its own tags in its definition, with the check, the schema and the message
together:

```go
behavior.Validator("motd_text", noEscapes, rule.Pattern(`^[^\x1b]*$`),
    "is not a valid message: it has an escape sequence")
```

`internal/validation` registers each one with the validator of the server,
through `rule.OnDeclare`, in either order of package initialization. The tags of
the hand-written domains, for example `sysctl_key`, stay in
`internal/validation`, with `rule.Register` next to each, because those domains
also use them. `sysctl_key` moves to the behavior at its cutover.

The behavior DSL and the endpoint DSL read a validate tag through the same
package, `internal/validation/rule`. Thus they give the same constraints, and
each fails on a tag that is not standard and not registered. A spec that loses a
constraint without a signal validates less than the server does, and nothing
reports it. A rule that the spec cannot show, such as `valid_target`, registers
`rule.None`.

`validation.Struct` and `validation.Var` take the request's context, and
`server.Valid` gives it from the echo context. `valid_target` reads the agent
registry through NATS, so its lookup is in the trace of the request, and a
cancelled request stops it. Before osapi-io/osapi#868 the lookup used
`context.Background()`, and no trace showed it. A caller with no request, such
as the generator or a config check, passes `context.Background()`.

A refresh of the target checks' cache of agents opens `validate.target`, or
`target.resolve` when a hostname is resolved to a machine ID, with the target as
its DETAIL. The `agent.list` of the refresh is under it, so a trace tells it
from the `agent.list` of `job.publish`. A read from the cache calls nothing and
opens no span.

Each input field has a validate tag. A field with no limit has
`validate:"omitempty"`. `behavior validate` and `controller endpoint validate`
refuse an input field with no tag, with the same words. The spec carries the
whole tag in `x-oapi-codegen-extra-tags`, on a parameter and on each property of
a body, so a Go client made from the spec validates as the server does.

An output can be a struct or a slice of structs. A slice becomes one result row
for each element, and each row has the name of the host. sysctl `list` answers
in this way now.

The platform, not the schema, reads two more tags:

- `render` tells how an output field shows in a table (`-` hides it, `bytes`,
  `age`, `status`). Thus the output of each behavior renders through one layout,
  not through formatting for each command.
- `telemetry:"attr"` records an input field on the span of the method. The span
  also records the field that the method names with `.Key`, without the tag.
  Thus a trace shows the item that each call changed, such as
  `key=vm.swappiness`. osapi records no other field. Thus by default, a password
  or the content of a file cannot get into a trace. A field with the tag
  `secret:"true"` is never recorded, also when it is the key.
- `template:"vars"` marks a string input as a Go template. Its `.Vars` are in
  the input field `vars`, a `map[string]string`, which the CLI takes as
  `--vars key=value`. A template reads `.Facts`, `.Vars` and `.Hostname`, the
  fields of `behavior.TemplateData`, and the provider renders it with
  `behavior.Render`. Before osapi queues a job, `server.Valid` parses each
  template and refuses one that reads a different field, or a var that the
  request does not give. Thus an error in a template is a 400, not a failure on
  each host. Facts are known only on each host, so the API does not check them.
  `behavior spec` lists the fact keys from `job.FactsRegistration`. The
  `template` rule of `validate` checks the types, and the generated API tests of
  each such method send a template with a missing var and expect a 400. File
  deploy uses it when it moves to a behavior. A template that reads a fact that
  a host does not have fails on that host, with the error in its result. osapi
  does not check facts before it sends the job: that would change how it sends
  jobs to hosts, for a small gain (osapi-io/osapi#768, not planned).

## Served beside the hand-written domains

A behavior runs through three generic parts. Each is written one time.

**The API.** Each behavior with `API` gets generated code in its `gen/`:

- `group.go` has the behavior as an endpoint group, and a handler for each
  method.
- `api.go` has the route table: the HTTP method, path and permission of each
  route. Its `init` registers them with the endpoint server. `decode.go` has the
  decoder of each method, which makes its typed request from the path, query and
  body and checks its tags. Both come from the group, with the endpoint layer's
  route writer, `internal/controller/endpoint/gen/routegen`. Thus a behavior's
  route is the same code as an endpoint's.

The endpoint server checks the token against the permission of the route. The
target is a field of the request, so the route checks it with the other tags.
The handler of each method calls `internal/behavior/dispatch`, which is written
one time. It queues the job, on one host or each host of the target, and makes
the `{job_id, results[]}` envelope.

An earlier version served each method through one handler that read the
definition when osapi started. It worked. But you could not open, debug or test
one endpoint alone, and the HTTP tests were a loop that no file named. A
generated handler for each method gives each endpoint a file and a test file,
which is the shape of the hand-written domains.

**The agent.** `internal/agent/processor_behavior.go` builds the provider of
each behavior one time at startup, for the platform of the agent. It uses what
the definition declares with `behavior.Platform`, and runs the methods of any
behavior with it.

A platform matches exactly first. If no platform matches, a host that is not
macOS gets the provider declared for `linux`, because the agent runs only on
Linux and macOS. `platform.Detect` names the Debian family `debian`, and names
other distributions by their own names. Without the fallback, a behavior that
works the same on each distribution needs a line for each distribution.

The builder gets a `host.Host` from `internal/behavior/host`: the platform, the
filesystem, the command runner, the file state store, the hostname and the
settings of the behavior. If a behavior has no provider on the platform, or its
builder returns `provider.ErrUnsupported`, its methods report `skipped`. The
agent logs which providers it built. The built providers go into the registry of
the agent, which gives them facts as it does for each other provider.

**The CLI.** The commands of a behavior come from its endpoint group, as the
commands of an endpoint do. `internal/controller/endpoint/gen/commandgen`, the
endpoint layer's command writer, writes `gen/cli.go`. The endpoint command
runtime runs each command: it reads the flags into the request, sends it, and
prints `--json` as the API sent it. `--target` is the flag of the request's
`hostname` field, with the default `_all`. The commands attach under the fixed
segments of the group's prefix, such as `next node`. `internal/behavior/command`
keeps the one table layout that each behavior renders in, as the renderer of
each method, and the pages of each behavior.

Behaviors are under `internal/`:

- the framework in `internal/behavior/`, with the parts that build or test a
  definition in subdirectories (`host`, `behaviortest`, `openapi`, `gen`)
- the behaviors in `internal/behaviors/<name>/`. A grouped behavior is under its
  group, as its routes are. Thus the directory of a behavior matches its URL.

The test helper of each runtime is next to the runtime that it drives:
`internal/behavior/dispatch/servertest` and
`internal/behavior/command/commandtest`. `behavior validate` refuses a behavior
or group with the name `all`, which is the registration index in
`internal/behaviors/all`.

Nothing outside osapi imports a behavior. The SDK connects to the HTTP API, and
the spec describes all that a client needs. Thus `pkg/` has only the SDK, and
imports nothing from `internal/`. `just go-pkg-check`, which `just test` runs,
fails if it does. An earlier version kept behaviors in `pkg/behavior`, because
the generic call of the SDK took the definition of a behavior. That call is now
a plain `Client.Request` to an API path. The CLI runtime knows behaviors, and
makes the path.

Inside, the same conventions apply:

- `host.Exec` is the part of the command runner that a provider calls. It is
  declared in `host`, where providers use it. Thus the runner of the agent and
  the generated mock of the fake host both satisfy it.
- The errors that a provider returns and that the API answers differently are in
  `internal/behavior`: `ErrUnsupported`, `ErrNotFound`, `ErrNotManaged` and
  `ErrNotInstalled`. `internal/provider` gives the hand-written providers the
  same values under its own names.
- The file-state record, `managedfile.State`, and its key,
  `managedfile.StateKey`, belong to `managedfile`, the behavior that owns
  managed files. The hand-written providers and the controller read them from
  there.

Permissions and sudo also come from the definitions. `internal/authtoken` makes
the known permissions, and those of each built-in role, from the hand-written
lists and the methods of each registered behavior. `admin` and `write` get the
read and write of a behavior. `read` gets its read.

The preflight of the agent checks each program that a behavior declares with
`Sudo`, together with its own list. At startup, the agent warns about each
program declared with `Runs` that is not installed. A missing program fails only
that behavior, so it does not stop the agent. Nobody edits either list for a
behavior. The fake host fails an example that runs a program without its
declaration, and counts the programs that the required behaviors declare. The
integration test fails when its image does not have a declared program.

The paths and the records that a behavior changes are declared the same way. The
fake host fails an example that writes, removes or changes the mode of a path
that `Writes` does not cover, or uses the `file-state` bucket without
`KeepsState`. A behavior's own `Writes` counts, and the `Writes` of the
behaviors it requires does not. Thus each behavior declares the paths that it
changes, also through `managedfile`. `managedfile` writes the path that its
caller names, so it declares `"*"`, and sysctl declares
`/etc/sysctl.d/osapi-*.conf`. `KeepsState` counts from a required behavior,
because the record belongs to it. `behavior validate` fails a `Writes` pattern
that is not `"*"` or an absolute path. The least-privilege plan uses the same
paths for the write access of a privileged step.

osapi serves a behavior under `/api` and `osapi client node`. Its jobs are in
their own `behavior` category, with operations `behavior.<name>.<method>`. Its
`gen/api.yaml` joins the main spec. Thus the SDK client, the UI client and the
API docs cover it.

A behavior that replaces a hand-written domain has the mark `behavior.Next`
while the two exist:

- Its routes are under `/api/next`.
- Its commands are under `osapi client next`.
- Its spec is `gen/api.next.yaml`, which the join does not read.
- The combined `internal/controller/api/next/gen/api.yaml` has each `Next`
  behavior.

The hand-written routes, commands, spec and docs do not change. Thus you can
compare the behavior with the domain that it will replace, on the same server.
sysctl has the mark until its cutover.

For the cutover, remove the mark and fix what fails:

- A test in `internal/behaviors/all` fails while a behavior that is not `Next`
  has the same route as a hand-written spec. It names the directory of that
  domain.
- The CLI does not start while a hand-written command has the name of a behavior
  command.
- The compiler finds the processor case.
- `behavior-gen-check` fails until `just generate` has joined the spec and made
  the clients from it again.

A test holds that comparison for each domain in migration. `TestParity` in
`internal/behaviors/all/spec_public_test.go` has one row for each behavior that
replaces a hand-written domain. The row names the generated spec of the behavior
and the spec of that domain. For each row, the test compares the two. It
compares:

- for each operation: the path without `/next`, the verb, the operationId, the
  scopes, the parameters, the request body and the response codes
- for each schema property: the type, the format, the enum, and if it is
  required

It does not compare prose and constraints. The generated spec uses different
words, and has constraints that the old spec did not have.

The row of a domain is added when its behavior is built. It is deleted with the
hand-written spec at the cutover. The table is the list of domains that are
still in migration. When it is empty, the test is deleted.

## Generated, and committed

`go generate ./internal/behaviors/all` runs `internal/behavior/gen`, which
writes:

| File                                             | Holds                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `internal/behaviors/<name>/gen/api.go`           | the route table, registered from `init`                                                                   |
| `internal/behaviors/<name>/gen/api_<method>.go`  | the method's handler and the decoder for its typed input                                                  |
| `internal/behaviors/<name>/gen/cli.go`           | the behavior's commands, from its group, by the endpoint layer's command writer                           |
| `internal/behaviors/<name>/gen/*_public_test.go` | a test for each of those files, described under the tests below                                           |
| `internal/behaviors/<name>/gen/api.yaml`         | the behavior's spec, which `just generate` joins into the main one; `api.next.yaml` for a `Next` behavior |
| `internal/behaviors/all/gen/gen.go`              | the import of every behavior's generated code: its routes and commands                                    |
| `internal/controller/api/next/gen/api.yaml`      | one spec for the behaviors marked `Next`, while any is                                                    |
| `docs/docs/sidebar/behaviors/<name>/<name>.md`   | the behavior's page, with its platforms and its settings                                                  |

osapi generates the code into files. It does not build it when it starts. Thus a
reviewer reads and diffs exactly what a route or a command does, as people read
the output of oapi-codegen now. The code is in the `gen/` of the behavior. Thus
all of a behavior is in its directory, and `gen/` has nothing written by hand.

The generator makes Go with jen (`github.com/dave/jennifer`), not with text
templates. Templates join strings. A template can render code that does not
parse, or forget an import, and that fails only when the output compiles. jen
makes the code as statements and manages the imports. goimports puts the imports
in their groups, and the output gets no other format. Each generated file starts
with a `Code generated` line, so golangci-lint skips it in the format check and
in the lint. golangci-lint keys on that line, not on the directory: the
generators themselves are in directories named `gen` (`internal/behavior/gen`,
`internal/controller/endpoint/gen`), and a person writes them, so they get the
format check and the lint.

The other candidate was the code-generator of Kubernetes. It was not used. It
reads comment markers on type declarations, and the examples and refusals of a
behavior are values that no marker can hold.

The spec of a behavior comes from the endpoint layer. The generator writes
`gen/group.go`: the behavior as an endpoint group, with a request type and a
response type for each method. Then `internal/behavior/gen/spec`, the second
`go:generate` step, builds the spec of each group with the endpoint layer's
builder. Thus the wording, the error responses and the validate tags of a
behavior's spec are the same as an endpoint's, from the same code
([endpoints](endpoints.md#behaviors-on-endpoints)). The builder uses the
`openapi3` types of kin-openapi, the library that oapi-codegen uses to read
specs. A test loads each written spec back and validates it. The keys are in the
order of kin-openapi, which is alphabetical, not the order that a person uses.
`TestNextSpec`, in `internal/apicontract`, holds the API contract of the
behaviors under `/api/next` to a golden file.

`osapi behavior new` also writes its first files with jen, in
`internal/behavior/scaffold_files.go`. Those files are not generated code. A
person edits them from the first minute, so they do not go in `gen/`. But the
rule is the same for each Go file that osapi writes: jen builds it, not a
template. The move from templates did not change the output. For a behavior with
no group and for a behavior under a group, each file was the same, byte for
byte.

The generator joins the spec of each behavior itself, not through
`redocly join`. This is the start of the removal of that tool. The docs site
builds an "API (next)" reference from it, next to the current reference.

`gen/cli.go` puts the docs of each method on its cobra command, as a person puts
them on a hand-written command. `.Describe` is the `Short`, `.Explain` is the
`Long`, and the `Example`s are the command lines of the `Example`, each under
its doc as a `#` line: the group's `.Example(flags, doc)`. The
`reference.Permission` annotation has the permission of the method, and the
`reference.Result` annotation has what each example does on the host and the
refusals. Thus `just cli-docs-generate` writes the CLI page of a behavior
command as it writes the page of a hand-written command, and a behavior has no
page of its own for each method. The output of a command is not on the page: the
same renderer prints each result, and the `output.md` page of the CLI reference
shows it one time.

`just behavior-gen-check`, which `just test` runs, generates the files again. It
fails if any of them changed. Thus a behavior that somebody edits without
`go generate` fails CI. It does not ship commands and pages that describe its
old shape. It compares only the generated files, so other uncommitted work does
not make it fail.

`just behavior-cover-check`, also in `just test`, holds each behavior package to
100% coverage alone. The target for the total of the repository is also 100%.
This check names the behavior package that is below the target.

`just behavior-scaffold-check`, also in `just test`, runs `osapi behavior new`
in a copy of the checkout, generates the new behavior and runs its tests. Thus
the scaffold cannot fall behind the checks that each behavior must pass. A new
check in `behaviortest` that the scaffold does not obey fails CI. Before this
check, the scaffold wrote a file through `h.FS`, and did not declare it with
`behavior.Writes`. Thus a new behavior failed its own tests (osapi#781).

## Telemetry every method gets

Each behavior method goes through `Method.Invoke` on the agent. Thus the
telemetry is there, not in each behavior. It makes:

- a `behavior.<name>.<method>` span under the `job.process` span of the agent,
  with the behavior, method, verb, outcome and `changed`
- three metrics: `osapi_behavior_calls_total`, `osapi_behavior_duration_seconds`
  and `osapi_behavior_changes_total`

They are made on the meter provider of the agent. Thus they export to the same
location as the other metrics of the agent. The span of the API request records
the behavior, method and target that it ran.

The work inside a method is traced by the shared code that it goes through, not
by the behavior: `exec <program>` from the executor, `file.write`, `file.remove`
and `file.chmod` from `internal/atomicfile`, and `kv.get` and `kv.put` from
nats-client. A new kind of work on a host gets its span in the shared code,
once, never in each behavior. The declarations above tell which of these spans a
behavior can make, and `behavior get` lists them as its child spans.

## Inspecting behaviors from the CLI

These commands read the registry. They need no config file and no controller,
because they describe the binary, not a fleet:

```sh
osapi behavior list                               # the behaviors and their methods
osapi behavior get --name sysctl                  # surfaces, methods, types, settings, telemetry
osapi behavior get --name sysctl --method update  # one method in full
osapi behavior spec                               # each part of the DSL, and when to use it
osapi behavior validate                           # every definition against the rules, each with its fix
osapi behavior new --name motd --description "x"  # write a new behavior's layout
osapi behavior new --group network --name neighbors --description "x"  # under a group
```

Each one takes `--json`. Values come as flags, as in all of the [CLI](cli.md).
`get` shows these things:

- if the behavior has an API and a CLI, and where osapi serves them now
- the behaviors that it uses, and the behaviors that use it
- for each method: its verb, route, permission, command, input and output fields
  and examples
- its settings, with the `agent start` flag for each
- the platforms that it has a provider for
- the programs that it runs with sudo
- its refusals
- the span and metrics that its calls record, the spans under it, and the paths
  that it writes

`behavior spec` lists each option, method, refinement, part of an example, call
in a provider and field tag, with what it does and when to use it. It also lists
how to build on other behaviors, the building blocks in the binary, the
generated paths, and what the platform cannot do yet. The table is `Spec` in
`internal/behavior/spec.go`. The building blocks come from the registry. A test
fails on an option, method, part of an example or field tag of the package
without a term.

`behavior new` writes `internal/behaviors/<name>/` as a working behavior that
keeps a value in a file, with each standard file. It adds its import to
`internal/behaviors/all`. Before you change anything, it builds, validates,
lints and passes each test with 100% coverage. Thus the layout is stated one
time, in code. An agent starts from a correct skeleton, not from a description
of one.

`osapi token roles` lists each permission, and which roles give it, with the
permissions of behaviors, as the binary has them. `--json` gives the input and
output as JSON Schema. An agent reads that before it makes a request. Tables
render through [the output style of the CLI](cli.md#output-style).

## The rules validate checks

`behavior validate` fails a definition that the platform cannot build from, or
that hides what it does. Each problem has its behavior, its method, its rule, a
message and the fix of the rule. The rules are the table `Checks`, in
`internal/behavior/checks.go`. `behavior validate --help` prints each rule with
what it requires and its fix. Thus an agent reads the rules before it breaks
one. A test fails on a `Rule` constant without a check.

The rules cover the names, the placement, the descriptions, the methods, the
verbs, the routes, the keys, the schemas, the outputs, `changed`, the surfaces,
the examples, the settings, the platforms, the requirements, internal behaviors,
`Writes` and secrets. The `span` rule fails a write that records nothing on its
span: no `.Key`, and no field tagged `telemetry:"attr"`. Thus a trace always
tells what a write changed. A write whose input has no field that a span can
record is exempt.

It exits 1 when any rule fails. An agent runs this check after it writes a
behavior, before the tests.

## Settings a behavior declares

Some behaviors need configuration, and most do not. Thus settings are optional,
and they belong to the behavior that reads them:

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

The struct has the same `mapstructure`, `doc` and `validate` tags as the config
of osapi. The value that you give is the defaults. That one declaration gives:

| Where                    | What appears                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| The config               | keys under `behaviors.<name>`, with defaults and `OSAPI_BEHAVIORS_<NAME>_*`               |
| `osapi agent start`      | a flag per setting, `--<name>-<field>`, bound to its key the way `agent.go` binds its own |
| `config list` and `get`  | each setting with its value, source and description                                       |
| `config validate`, start | its `validate` tags, checked with the rest of the config                                  |
| `behavior get`           | a Settings block: key, flag, env var, type, default                                       |
| The docs site            | a settings table on the behavior's page                                                   |
| The agent                | `behavior.Settings[T](Behavior)`, the decoded struct                                      |

The order causes no problem. Behaviors register in the package `init`, before
`main`. Thus the flags exist when cobra parses the command line. `initConfig`
runs after that, and reads the same registry. `BindPFlag` only records the
mapping. When the config is decoded, viper resolves the flag, then the
environment, then the file, then the default.

Settings are not inputs. The input of a method applies to each call. It is a
flag on the client command, and is never bound to the config. Thus a value in a
file can never select what a write acts on.

A setting is permanent configuration of the process that reads it. The agent is
the process that runs the methods of a behavior. Thus the flags go on
`agent start`. A flag on a client command does not change the host.

The one setting of sysctl is `behaviors.sysctl.dir`, the directory where it
writes its conf files. Before, this was a constant in the Debian provider. A
provider builder reads settings from the host that it gets,
`host.Settings[Settings](h)`, because the builder cannot name the variable of
the behavior in its own initializer. The provider of the hand-written sysctl
domain, built in `createSysctlProvider`, reads the same setting. Thus the two
write to the same directory.

## Tests a behavior gets from its definition

The examples of a behavior are its tests at each layer above the provider. An
example can tell how the host is before the call:

- `After`: a different method runs first
- `Prints`: the output of a command
- `PrintsAfter`: the output of a command after a different command ran
- `Exists`: a file

It can also tell what the call changes, with `Wrote`, `Removed` and `Ran`.

`PrintsAfter` is for state that a program keeps, not a file. A package query
prints "not installed" until the install runs, and "installed" after it. The
second-run check needs to see that. The `aptpkg` eval of the skill found the
gap. Without it, the install example of a package behavior could not pass that
check correctly, and the session stopped and said so.

| Layer       | Where                                              | Checks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Provider    | `behaviortest.Run`, from `behavior_public_test.go` | each example on a fake host per platform gives its output and effects; a write declares effects and reports `changed: false` run twice; each command and store call failing in turn never panics                                                                                                                                                                                                                                                                                                                                     |
| API         | `gen/api_<method>_public_test.go`, generated       | a table of literal requests through the real handler and middleware with the job client mocked, every response validated against the generated spec with kin-openapi: each example on one host and broadcast, with its body; the host skipping, failing or timing out; the job client failing (500); a missing item (404); a bad target, each missing required field, a body that is not JSON, a field of the wrong type and each refusal the API can see (400, no job queued); a missing token (401) and a missing permission (403) |
| Routes      | `gen/api_public_test.go`, generated                | every method's HTTP method, path and permission                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| CLI         | `gen/cli_public_test.go`, generated                | each example's flags, given to the generated command, send the example's input                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Wiring      | `internal/behaviors/all/all_public_test.go`        | every registered behavior validates, every route is mounted and every command attached                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Live server | `test/integration/behavior_test.go`                | every unkeyed read against a real agent; the write examples with `OSAPI_INTEGRATION_WRITE_BEHAVIORS=1`, each reporting the example's `changed` and then `false`; `just behavior-int-linux` runs them on Debian in a container, since the CI agent cannot write `/etc`                                                                                                                                                                                                                                                                |

Each failure of `behaviortest.Run` ends with the fix of its check. The checks
are the table `TestChecks`, in `internal/behavior/checks.go`, and
`behavior validate --help` prints them after the rules. The `file-span` check
fails a change to a file that does not go through `atomicfile`: a write, a
removal or a mode change through `h.FS`. Such a change has no `file.write`,
`file.remove` or `file.chmod` span, and is not atomic. The fake host finds it
from the stack of the call. The fix sends a behavior that manages a file to
managedfile, and a building block to `atomicfile.Write`, `Remove` or `Chmod`.

The generated HTTP tests split the cases of each method as the handler tests of
the hand-written domains do: `Test<Method>` for the answers,
`Test<Method>ValidationHTTP` for the 400s and `Test<Method>RBACHTTP` for the
tokens. `internal/behavior/dispatch/servertest` runs the rows. Fix a failed
generated test in the definition or the generator, never in `gen/`.

The fake host is `internal/behavior/behaviortest`. It has:

- an in-memory filesystem
- a command runner that records each command line and prints what `Prints` gives
- an in-memory file state store

The command runner and the store are the generated mocks of the repository, and
the harness configures them. If they have no answer for a call, they report it.
They do not make a false answer. Coverage is measured for each package. Thus the
harness runs from the test of the behavior, which is one line that
`behavior new` writes. The methods and the provider of each platform also have
their own tests. Thus each file with code has one, as the rule of the repository
requires.

The harness also probes each string input field of each example, one at a time,
with three values:

- a path that goes out of its directory
- a value that starts a new line
- a value that reads as an option

A probe passes in three cases. The `validate` tags of the field refuse it, as
the API does. Or the method fails. Or it changes nothing that it must not
change. It fails when it:

- writes outside the directories that the example writes
- puts its line in a file next to other content
- gets to a command as an option with no `--` before it
- gets to a `sh -c` script

Declared refusals cover only the inputs that an author thought of. The probes
cover the three most common ways that a string becomes an injection, for each
behavior, and the author does not need to think of them. An internal behavior
gets no probes, because its input comes from other behaviors. The free-text case
is permitted. A file whose full content is the value, as a message of the day
is, can have any line.

A method declares what it refuses with `.Fails(doc, input, errorText)`, with the
same host options: bad input, or state that it cannot act on, for example a
parameter that osapi stopped managing. The provider test checks that each one
fails with that text. The API test checks that a refusal whose input breaks a
`validate` tag gets a 400, and that no job is queued. The docs page lists them.

Each rule of each input field needs a refusal that breaks it, such as a key with
a slash for `sysctl_key`. `behavior validate` names a rule that has none. The
validator reports the field and the rule that an input breaks, so the check is
exact. A behavior's `required` needs none, because the API test leaves the field
out. An endpoint's needs one, because endpoints have no such test. A `min` of 1
on a string that is required, optional or in the path needs none, because its
only bad value is empty. The author writes each bad value. A generator cannot
make one for a custom rule. The endpoint DSL has the same check, with
`.Fails(doc, input)`.

On the fake host, each filesystem, command and store call fails in turn. Each
store read also returns a damaged record in turn: not JSON, empty JSON, and a
file state record with empty metadata.

The examples and refusals of sysctl get to 150 of the 152 statements of its
Debian provider. Its 1,820 lines of hand-written tests get to 152. The two that
remain are a JSON encoding error that a struct of strings cannot make. Only the
test seam of the hand-written tests can get to it.

```sh
go test ./internal/behaviors/sysctl -run TestBehaviorPublicTestSuite/TestExamples -coverprofile=c.out && go tool cover -func=c.out | grep debian.go
```

## Behaviors built on other behaviors

A behavior that needs the work of a different behavior declares it with
`behavior.Requires`. It calls the methods of the other behavior as Go calls on
the same host, in the same job. There is no second job, no API call and no round
trip.

```go
var Behavior = behavior.Register(behavior.Define(
    "sysctl", "Kernel parameters, written to sysctl.d files and applied",
    behavior.Node,
    behavior.Requires(managedfile.Behavior),
    behavior.Platform("debian", newDebian),
    ...
))
```

Generic work goes in a building block: an internal behavior that does one job,
such as managedfile for a file that osapi manages. `behavior spec` tells when to
use one and when to make one, and lists each building block in the binary. The
wiring is written by hand today, in three places: `Requires`, `host.Require` in
the builder, and `Call` in the provider. osapi-io/osapi#764 has the next steps:
scaffolding the wiring, workflows across hosts, and behaviors that call outside
APIs.

- **Building.** `host.Build` builds the provider of each required behavior
  first, for the same host. It puts the provider in the host that the requiring
  builder gets. The builder reads it with
  `host.Require[P](h, managedfile.Behavior)`, and calls each method of it with
  `behavior.Call(ctx, managedfile.Behavior, managedfile.Update, p, in)`. `Call`
  runs the method inside its own span, with its metrics, so the trace shows
  `behavior.managedfile.update` as a step under `behavior.sysctl.create`. `Call`
  also checks the input against its validate tags before the method runs, as the
  API does for a served method. An internal behavior is not served, so without
  this check its tags would only describe its rules. The agent checks a job's
  input in the same way, with `Method.Check`, before it runs the method: a job
  can reach NATS without the API. Thus the API, the agent and `Call` hold each
  method to its tags, and the author writes no check. `behaviortest` fails a
  `.Fails` input that breaks a rule when `Method.Check` passes it, so an
  internal behavior proves its rules hold, as a served one does with its HTTP
  tests. A direct call of `managedfile.Update` works but has no span and no
  check. `behaviortest.Run` reads the Go files of the behavior and fails such a
  call. The agent and the fake host in `behaviortest` both build through it.
  Thus the examples of a behavior run through its requirements exactly as they
  do on an agent.
- **Unsupported spreads.** A required behavior can have no provider on a
  platform, or it can refuse the host. Then the requiring builder does not get
  it. The builder answers `provider.ErrUnsupported`, and its methods report
  `skipped`. If a required builder fails, the requiring builder fails too, with
  the two names in the error.
- **Internal.** `behavior.Internal` marks a behavior that only other behaviors
  use. It has no route, no command, no spec and no permissions.
  `behavior validate` fails an internal behavior that also declares `API` or
  `CLI`. It still has examples, refusals, tests and a docs page, and
  `behavior list` marks it.
- **Checks.** `behavior validate` fails a requirement that is not registered,
  and a cycle, under the rule `requires`. It fails an internal behavior that no
  behavior requires, under the rule `internal`, because nothing can call it.
  `behavior get` lists what a behavior uses and what uses it. The landing page
  of the Behaviors section has a table of each behavior with the two lists,
  generated from the registry.

`managedfile` is the first internal behavior. It writes files on a host, and
keeps a record of them in `file-state`. A caller sets the mode, owner and group
of the file. A caller can also mark content as a secret. Then the record keeps
no checksum of it, because somebody can recover a short secret from its SHA-256
by guessing.

It reads ownership with `stat` and sets it with `chown` through sudo, which
`managedfile` declares. Thus the fake host tests it like each other command. The
`apptoken` eval found that it was missing. A token written through `managedfile`
was readable by each user on the host, and the session stopped and did not write
it.

The Debian provider of sysctl writes and removes its conf files through it. The
hand-written sysctl domain builds its own `managedfile` provider. Thus the two
write the same files with the same records. The code moved out of sysctl without
changes. The hand-written sysctl provider tests confirm this. They did not
change, except two marshal-failure cases that moved with the code.

A behavior is internal when two things are true. An operator would never call it
from the CLI or the API. It is a piece of work that other behaviors share, such
as writing a file or reloading a service. `osapi behavior new` always writes a
behavior that an operator calls, because a new internal behavior has nothing
that requires it yet, and `behavior validate` would fail it.

Shared work becomes an internal behavior at its second use. When one behavior
does something, that is its own code. When a second behavior needs the same
thing, it becomes a behavior that the two require. The build-a-behavior skill
asks this question before somebody writes a behavior.
[The migration plan](behavior-migration.md#internal-behaviors-the-migration-extracts)
lists the candidates that the hand-written domains share.

A chain across hosts or steps, where the output of one method is the input of
the next, is a workflow. It stays with osapi-orchestrator.

## Secret inputs

Tag an input field that has a secret, for example a password or an API key, with
`secret:"true"`. The tag does three things. Thus osapi keeps the secret of a
behavior out of all records and publications, and you edit nothing outside the
directory of the behavior:

- **Audit.** The audit summary redacts each field name that is tagged secret in
  any registered behavior, together with the fixed denylist in `internal/audit`.
  Without the tag, osapi stores a field with the name `passphrase` as it came,
  because the denylist matches names and does not have that name.
- **Spec.** The schema of the field has `format: password` and
  `writeOnly: true`. Thus a generated client and the API reference treat it as a
  secret.
- **Telemetry.** osapi never records it on a span. `behavior validate` fails a
  field that is tagged both `secret` and `telemetry:"attr"`, under the rule
  `secret`.

Redaction matches names, as the denylist does. If you tag a field `value` as
secret, osapi redacts each request field with the name `value`, in each
behavior. Give a secret field a name that tells what it has.

The value still comes as a CLI flag, as the `--password` of a hand-written
domain does. A read from standard input or a prompt is not built.

## Not built yet

The cutover:

- routes move from `/api/next` to `/api`
- commands move from `client next` to `client`
- the generated spec joins the main spec
- the hand-written handler, processor and commands of sysctl are deleted

The provider of sysctl is already in the directory of the behavior, as
`debian.go`, `darwin.go` and `linux.go`, with their tests moved without changes.
The hand-written domain imports it from there until the cutover.

The SDK knows routes, not behaviors. It has a generic `Client.Request` to any
API path. Its typed services, for example `client.Sysctl`, are hand-written over
the client that oapi-codegen generates from the spec. To generate those typed
services from the spec too, after the spec of each behavior joins the main spec,
is a later step in [the migration plan](behavior-migration.md).
