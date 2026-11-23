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

Each operation on a node is a behavior now. Behaviors replaced the hand-written
domains, one domain at a time, from sysctl to command (osapi-io/osapi#1113).
[Built-in behaviors](built-in-behaviors.md) tells why each behavior that osapi
ships operates as it does.

## Why

A hand-written domain was slow to add, because most of its code connected layers
and had no logic. A measurement on `main` on 12 November 2026, before sysctl
moved, found:

- `sysctl get` had 59 lines of logic in `debian.go`, and 312 hand-written lines
  around it: handler 153, validator 10, agent processor 28, SDK 56, CLI 63,
  operation constants 2. Its spec was 104 more lines of hand-written YAML.
- In the full repository, the handlers, agent processors, SDK and CLI were
  47,792 hand-written lines, against 15,189 lines of provider.
- The last three domain additions changed 130 files (`service`), 75
  (`certificate`) and 47 (the SSH key operations).

The connecting code was the same each time, and somebody typed it again each
time. The `key` argument to `sysctl get` was declared by hand in eight
locations. Its pattern, `^[a-zA-Z0-9][a-zA-Z0-9._-]*$`, was written three times.
The handler sent the job payload as a `map[string]string`. The agent read it
back into an anonymous `struct{ Key string }`. Nothing checked that the two
agreed.

The same shapes occurred again and again in the codebase:

- 40 anonymous payload structs in `internal/agent`.
- 90 copies of the `ok`/`failed`/`skipped`/`timeout` switch in the handlers.
- 94 handlers that branched on `IsBroadcastTarget`.
- 136 hand-written SDK result types, with 127 functions that copied generated
  types into them.

The cost was clear, and it also blocked agents. An agent that had to add a
domain had to copy all of it from convention. An agent that must use osapi had
nothing to learn operations from, until `osapi init`, `help --json` and
`behavior get` existed. Those read the definitions.

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
are next to the definition, not in a subdirectory.

`docs/docs/sidebar/development/behaviors.md` in osapi describes the layout and
the tags for authors. This page records why the design is as it is.

## What the definition decides

| Declared                                | Decides                                                                                                                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `behavior.Node`                         | The work runs on a host, through the job system. It is the only placement                                                                                                                                                                                                                                                                                                                                                   |
| `behavior.Of(user.Behavior)`            | Puts the items under an item of another behavior: `/api/node/{hostname}/user/{name}/sshkey`, `osapi client node user sshkey`. Each input has the parent's key, which goes in the path before the method's own. The permissions are the parent's. Not with `Under`; `behavior validate` refuses that, a parent with no key, and a parent that is not registered                                                              |
| `behavior.Area(area.Hardware)`          | Puts a served behavior in an area, a constant of `internal/area`: the tab of the Add Block panel of the Configure page, the folder of its SDK page and its section of the SDK menu. [Areas](endpoints.md#areas) tells what an area decides. `behavior validate` refuses a behavior with API and no area                                                                                                                     |
| `behavior.Under(behavior.GroupNetwork)` | Nests the behavior: `/api/node/{hostname}/network/dns`, `osapi client node network dns`. The group is also the prefix of the permissions. `behavior validate` refuses a group outside `KnownGroups()`                                                                                                                                                                                                                       |
| `Read`                                  | `GET`, the `<group>:read` permission, no `changed` in the result                                                                                                                                                                                                                                                                                                                                                            |
| `Write`                                 | `POST`, or `PUT` for `update` and `DELETE` for `delete`, and the `<group>:write` permission                                                                                                                                                                                                                                                                                                                                 |
| `Action`                                | A write named for what it does to the item, such as `restart`: `POST` on the path of the item with the name after it, `/service/{name}/restart`, and the `<group>:execute` permission. The name is one of the actions of the CLI                                                                                                                                                                                            |
| `.Always()`                             | An action that changes the host each time it runs, such as `restart`. The generated test and the integration test do not run it a second time to see `changed: false`. `behavior validate` refuses it on a method that is not an action                                                                                                                                                                                     |
| `.Disrupts("why")`                      | A method that takes the host down, such as a reboot, and why. Its examples run on the fake host. The integration test does not run them on a live host, because the host would go down under the test. `behavior validate` refuses it with no reason                                                                                                                                                                        |
| `.PermitAs(verb)`                       | An action whose permission is `<name>:<verb>` in place of `<name>:execute`, such as `docker:exec` for docker exec with `behavior.VerbExec`. Thus the action does not share a permission with the other actions of the behavior, which the operator role gets. The verb is `VerbExec` or `VerbShell`, which only the admin role gets. `behavior validate` refuses it on a method that is not an action, and a different verb |
| `.Shell()`                              | `.PermitAs(behavior.VerbShell)`: an action that runs a shell command line, such as `command shell`. Its permission is `<name>:shell`                                                                                                                                                                                                                                                                                        |
| `.NotAFact("why")`                      | A read that runs a command outside gohai, and why: what it reads is not a fact of the host, such as the updates of the package index. Without it, the `gohai` test check fails each command of a read that does not go through `h.Sources()`                                                                                                                                                                                |
| `.Key("key")`                           | The input field addressed in the path, `/{key}`                                                                                                                                                                                                                                                                                                                                                                             |
| `behavior.API`                          | Routes, its part of the OpenAPI spec, and the API reference pages                                                                                                                                                                                                                                                                                                                                                           |
| `behavior.CLI`                          | Generated commands, with their pages in the CLI reference. It needs `API`, because the commands call the API                                                                                                                                                                                                                                                                                                                |
| `.Describe`, `.Explain`                 | The one-line description, and the longer text that the help and the CLI page of a command, and the spec, carry. Neither has `<`, `>`, `{` or `}`: the docs site reads them as markup, so `behavior validate` refuses them                                                                                                                                                                                                   |
| `.Example`                              | Sample calls. They are the examples of a command, and the tests                                                                                                                                                                                                                                                                                                                                                             |
| `behavior.Config(v)`                    | Settings under `behaviors.<name>`, with `v` as their defaults                                                                                                                                                                                                                                                                                                                                                               |
| `behavior.Platform(p, f)`               | How the provider is built on platform `p`, a `PlatformName` constant: `PlatformDebian`, `PlatformSUSE`, `PlatformDarwin`, or `PlatformLinux` for every Linux host without its own. On any other, the methods report `skipped`                                                                                                                                                                                               |
| `behavior.Sudo("prog")`                 | A program the provider runs with sudo, which the agent's preflight checks                                                                                                                                                                                                                                                                                                                                                   |
| `behavior.Runs("prog")`                 | A program the provider runs without sudo; the agent warns at startup when it is missing                                                                                                                                                                                                                                                                                                                                     |
| `behavior.RunsOnPlatform(p, "prog")`    | A program the provider runs on platform `p` only, such as `vm_stat` on darwin; a Linux host is not asked for it                                                                                                                                                                                                                                                                                                             |
| `behavior.SudoOnPlatform(p, "prog")`    | A program that the provider of platform `p` runs with sudo, such as `update-ca-certificates` on debian and `update-ca-trust` on linux. It holds on each host that this provider serves, so linux does not hold on debian when debian has its own provider                                                                                                                                                                   |
| `behavior.RunsIfPresent("prog")`        | A program the provider runs only when the host has it, such as `zfs`; the agent and the integration test do not ask for it                                                                                                                                                                                                                                                                                                  |
| `behavior.Runs(behavior.AnyProgram)`    | Each program: the provider runs the program that the caller names, as `command` does. The agent and the integration test look for none                                                                                                                                                                                                                                                                                      |
| `.On(p...)`                             | Limits one method to some of the platforms. On any other platform, that method reports `skipped`, and its examples do not run there                                                                                                                                                                                                                                                                                         |
| `.Sudo`, `.Runs` on a method            | A program that only this method runs. A host needs it only where the method runs                                                                                                                                                                                                                                                                                                                                            |
| `behavior.Writes("...")`                | The paths the provider writes, removes or changes the mode of, as `path.Match` patterns; `"*"` is any path                                                                                                                                                                                                                                                                                                                  |
| `behavior.KeepsState`                   | The provider keeps a record in the `file-state` bucket                                                                                                                                                                                                                                                                                                                                                                      |
| `behavior.Validator(...)`               | A `validate` tag of the behavior's own: its check, its schema and its message                                                                                                                                                                                                                                                                                                                                               |

The permission prefix is the name of the behavior. A group does not change it.
Thus `dns` under `network` needs `dns:read`.

The names of the methods are verbs, because they become the commands.
`behavior validate` refuses a read with a name that is not `list`, `get` or
`status`, and a write with a name that is not `create`, `update` or `delete`. A
write with a different name is an action, such as `restart`, and its name must
be one of the actions of the CLI. For a synonym, such as `remove` or `add`, the
refusal gives the standard verb.

Thus no method creates an item and also updates it. `create` is `POST`, and
`update` is `PUT`. The split gives 404 a meaning. When `update` answers 404, the
item that the caller wanted to change does not exist. One method that creates
and updates cannot tell the caller that.

The things that the controller answers itself (audit, jobs, admission and
health) are not behaviors, and have no placement. They never go to a host.

`API` and `CLI` are separate, because not each behavior is called from outside.
A behavior that only other behaviors use has neither. Only the job system can
get to it.

`internal/behavior/behavior.go` has `Path`, `HTTPMethod`, `Permission` and
`Command`. They change a definition into those four values. For sysctl, they
gave the same routes and permissions that the hand-written API served.

## The name of a behavior

The name of a behavior is the thing that it manages, not the tool that does the
work. The NTP behavior is `ntp`, and chrony does its work. The behavior that
runs jobs on a schedule is `schedule`, and cron does its work. If the name is
the tool, the name becomes incorrect when a different tool does the work. Then
the route, the permission and the command change together, and a change to the
route breaks each caller. Do not use an abbreviation as a name: the behavior is
`memory`, not `mem`.

One question decides if the tool is in the route: does the caller select the
tool, or does the host?

A caller selects a container runtime. A person decided to run Docker, and wants
to address it directly. Thus the runtime is a behavior in the `container` group,
at `/container/docker`. A Podman behavior can go next to it, at
`/container/podman`, and the two can be on one host.

A caller does not select a package manager. The host selected it before. A
request to a fleet to install a package cannot depend on which hosts use apt.
Thus the route is `/package`, and the provider of each platform runs the tool of
that platform. `ntp` and `schedule` are the same.

An error in either direction has a cost:

- If the route has a tool that the caller did not select, one call cannot go to
  the full fleet.
- If the route does not have a tool that the caller selected, the caller cannot
  address two runtimes on one host.

The name is the same in the route, the command and the docs page. The Go package
can have a different name, when the name is a Go keyword
([generated, and committed](#generated-and-committed)).

## A resource under another

`behavior.Of(parent)` makes a child behavior: its items exist only inside an
item of the parent, as the SSH keys of a user do. The child is a behavior of its
own, with its types, its provider, its docs page and its chain. It takes three
things from the parent:

- **The path.** The route is the parent's item, then the child:
  `/api/node/{hostname}/user/{name}/sshkey`. `Method.PathKeys()` is the parent's
  key, then the method's own key, and each generator reads it: the request
  fields that go in the path, the decoder, the generated API tests and the span
  attributes.
- **The command.**
  `osapi client node user sshkey delete --name alice --fingerprint SHA256:...`.
  The endpoint layer already reads a path field in the prefix of a group, as it
  does `{hostname}`, so the child's group has the prefix
  `node/{hostname}/user/{name}`.
- **The permissions.** The keys of a user need `user:read` and `user:write`.

The parent's key is the key of its keyed methods, such as `name` for a user.
Each input of the child has a field of that name, which `behavior validate`
holds to the `key` rule as it does the method's own key. The `parent` rule
refuses `Of` with `Under`, a parent with no keyed method, and a parent that is
not registered. The `key` rule also refuses a key whose name in the spec is the
name of a row type: the request parameter of the key `part` of a behavior
`zzpart` and a row type `Part` are both `ZzpartPart`, and oapi-codegen fails on
the full spec. A throwaway parent and child found that before any real child
existed.

The `route` behavior is the first child: a route is under its interface,
`/api/node/{hostname}/network/interface/{name}/route`. A child's names in the
spec start with its parent's, `NetworkInterfaceRoute`, as its path does. Its
route keeps its destination in the body, because a CIDR's slash cannot go in a
path segment. The integration test's reset deletes an example's item with each
field that the delete takes, so it resets a route by its interface and its
destination, as it resets an item by its key.

A child that needs the parent's provider, such as to check that the user exists,
declares `Requires` too. `Of` is the place in the API, not a call between the
two.

The `sshkey` behavior is the second child, under user. It requires user, and
reads the user through `behavior.Call` of `user.Get`, so that a missing user is
not found and the trace shows the call. Its delete keeps the fingerprint in the
body, as a route keeps its destination: the base64 of a fingerprint can have a
slash. A delete for a user that the host does not have reports `changed: false`.
Thus the integration test can reset a key before the example adds its user.

`After` can name a method of the parent. An example of a key adds its user
first, with `After(user.CreateInput{...})`. The fake host runs the parent's
method on the parent's provider, on the same host. The integration test runs the
parent's command, and deletes the parent's item with the parent's delete, after
the example's own item.

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
through `rule.OnDeclare`, in either order of package initialization. A tag that
more than one behavior uses, such as `interface_name`, is in
`internal/validation`, with `rule.Register` next to it. Only the sysctl behavior
uses `sysctl_key`, so it is a `behavior.Validator` of sysctl.

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

## A refusal runs as the agent runs it

The tests of a behavior run each refusal as the agent and `behavior.Call` do:
the method's `validate` rules first, then the method. A refusal that a rule
refuses holds with the rule's text, so the provider need not check what a tag
already says. A refusal that no tag can say, such as "not found", holds with the
provider's error. Before, the tests called the provider alone, so a rule
declared only as a tag looked accepted, and each behavior checked its rules a
second time in the provider.

## Each layer owns its rules

A behavior builds on the two other DSLs: it makes an endpoint, its routes and
its part of the spec, and CLI commands. Each layer owns the rules of what it
makes, and `behavior validate` asks that layer. It does not keep a copy:

| Rule                                              | Owner          | Asked as                                        |
| ------------------------------------------------- | -------------- | ----------------------------------------------- |
| The types a flag holds                            | CLI            | `command.Flaggable`, which its generator builds |
| The `render` values an output knows               | CLI            | `command.TagProblems`                           |
| An optional body field is `omitempty` in `json`   | endpoint       | `endpoint.SentEmpty`, the `optional` rule       |
| `dive`, `secret`, `pattern` in the spec           | rule, endpoint | the spec builder that ships the spec            |
| A requirement is registered, with no cycle        | chain          | `behavior.ChainChecks`, the `requires` rule     |
| An internal behavior has a behavior that needs it | chain          | `behavior.ChainChecks`, the `internal` rule     |

A copy drifts. The behavior `surface` rule kept its own list of flag types,
which allowed an `int64` that the generator could not build
(osapi-io/osapi#973). The `optional` rule was written first in the behavior DSL
only, and a hand-written endpoint could still send `""` (osapi-io/osapi#974).

The behavior's own rules cover what only a behavior has. The name and the group
are lowercase letters and digits, with no dash, because the generators make Go
names of them (osapi-io/osapi#976). An input field has a `json` name and a
`doc`, no `default`, which the server does not apply, and is not named
`hostname` or `target`, which every request has (osapi-io/osapi#975,
osapi-io/osapi#978, osapi-io/osapi#980, osapi-io/osapi#981). A key is required,
because it is a path segment. A struct that an output holds is named in one spec
for every behavior, so two behaviors cannot each have a different `Usage`
(osapi-io/osapi#979).

An audit of the three DSLs on 20 November 2026 found these: each was an
assumption of a generator that no rule checked. The `version` of
`package create` was the first one seen. It sent `"version": ""` for a plain
install, the spec's pattern refused it, and only the integration test saw it.

An output can be a struct or a slice of structs. A slice becomes one result row
for each element, and each row has the name of the host. sysctl `list` answers
in this way now. An empty slice is one row with only the name and the status of
the host. Thus a host that answered with nothing is different from a host that
did not answer. The generated API tests expected no row there, until route `get`
gave the first example with an empty list (osapi-io/osapi#990).

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
  `behavior spec get` lists the fact keys from `job.FactsRegistration`. The
  `template` rule of `validate` checks the types, and the generated API tests of
  each such method send a template with a missing var and expect a 400. File
  deploy uses it when it moves to a behavior. A template that reads a fact that
  a host does not have fails on that host, with the error in its result. osapi
  does not check facts before it sends the job: that would change how it sends
  jobs to hosts, for a small gain (osapi-io/osapi#768, not planned).

## How a behavior is served

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
the `{job_id, results[]}` envelope. A host that runs the job and fails it is a
row with `status: failed` and the error of the provider, on one host as on a
broadcast. A job that osapi cannot send is a 500. On one host, the API answers
`ErrNotFound` with 404 on each method, `ErrNotManaged` and `ErrNotInstalled`
with 409, and `ErrInvalid` with 400; `ErrUnsupported` is a `skipped` row.
`ErrInvalid` is an input that the host refuses and that the validate tags cannot
see, such as a path that is a directory where `file status` reads a file. Before
osapi-io/osapi#1021, a not found on a method with no key, such as a create whose
object is not in the Object Store, was a 500, and not managed and not installed
were a 404 that said "not found". Until osapi-io/osapi#989, a single host that
failed a job was a 500 that said the job could not be sent. Thus the agent's
message did not get to the caller.

An earlier version served each method through one handler that read the
definition when osapi started. It worked. But you could not open, debug or test
one endpoint alone, and the HTTP tests were a loop that no file named. A
generated handler for each method gives each endpoint a file and a test file,
which was the shape of the hand-written domains.

**The agent.** `internal/agent/processor_behavior.go` builds the provider of
each behavior one time at startup, for the platform of the agent. It uses what
the definition declares with `behavior.Platform`, and runs the methods of any
behavior with it.

A platform matches exactly first. If no platform matches, a host that is not
macOS gets the provider declared for `linux`, because the agent runs only on
Linux and macOS. gohai's `family.Detect` names the platform: a family as Ohai
names it, such as `debian`, `rhel`, `fedora` or `amazon`, `darwin` on macOS, or
the distribution's own name when it has no family. Without the fallback, a
behavior that works the same on each distribution needs a line for each
distribution.

One method can run on fewer platforms than its behavior. `hostname` declares
`linux` and `darwin`, and its `get` reads the name on both. Its `update` has
`.On(behavior.PlatformDebian)`, so it runs only on the Debian family. The agent
does not call the provider for `update` on any other host, and reports
`skipped`. `.On` takes the names that `behavior.Platform` takes, and `linux` in
`.On` is each host that is not macOS. A name that resolves to no provider of the
behavior fails `behavior validate`. The macOS provider still implements
`SetHostname`, because the provider interface has each method, but it only
returns `ErrUnsupported`.

The builder gets a `host.Host` from `internal/behavior/host`: the platform, the
filesystem, the command runner, the file state store, the hostname, the facts,
the clock and the settings of the behavior. A provider gets the time from
`h.Time()`, not from `time.Now`. Thus the fake host can give an example a fixed
time, and an output that the time changes, such as uptime on macOS, is the same
each run. If a behavior has no provider on the platform, or its builder returns
`provider.ErrUnsupported`, its methods report `skipped`. The agent logs which
providers it built. The built providers go into the registry of the agent. A
provider reads the facts of the agent from `h.Facts`.

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
  `internal/behavior`: `ErrUnsupported`, `ErrNotFound`, `ErrNotManaged`,
  `ErrNotInstalled` and `ErrInvalid`. `internal/provider` gives the same values
  under its own names to the providers that the agent uses for its own facts,
  under `internal/provider/node`. `behavior spec get` lists each one, with what
  the API answers and when to return it, under "Errors a provider returns". A
  test fails on an exported error with no entry there.
- The file-state record, `managedfile.State`, and its key,
  `managedfile.StateKey`, belong to `managedfile`, the behavior that owns
  managed files. The file endpoints of the controller read them from there. A
  write of a file changes when the content, the mode or the owner changes. It
  also changes when osapi deployed the path with other metadata: then only the
  record changes, as for a cron entry with a new schedule and the same content
  (osapi-io/osapi#1106). A file that has the content and no record, or an
  undeployed record, does not change.

Permissions and sudo also come from the definitions. `internal/authtoken` makes
the known permissions, and those of each built-in role, from a short list in
`internal/authtoken`, the methods of each endpoint group and the methods of each
registered behavior. The persona roles get a behavior's permissions by a rule:
`admin` gets each one, `read` gets each read, `automation` gets each read and
write, and `operator` gets each read and execute, except the permissions that
are admin only. [Permissions](permissions.md) has each role, and the permissions
that are admin only and why.

The preflight of the agent checks only the programs that the behaviors declare
with `Sudo` on the platform of the host. The agent has no list of its own
(osapi-io/osapi#1180). At startup, the agent also finds each program that a
behavior declares with `Runs` or `Sudo` and that the host does not have. It
looks for a `Runs` program on its `PATH`, and for a `Sudo` program on its `PATH`
and in `/usr/local/sbin`, `/usr/sbin` and `/sbin`, because sudo finds a program
there. The agent logs a warning for each missing program, and reports the list
as `missing_programs` in its registration. `agent get` and `agent list` show it
(osapi-io/osapi#1139). A program declared on a method counts only on a platform
where the method runs. A behavior that has no provider for a platform runs
nothing there, so it needs no program there. Thus an agent on Fedora does not
ask for the `apt-get` of a behavior that has only a Debian provider. `hostname`
declares `hostnamectl` on `update`, so an agent on macOS does not ask for it. A
missing program fails only that behavior, so it does not stop the agent. Nobody
edits either list for a behavior. The fake host fails an example that runs a
program without its declaration, and counts the programs that the required
behaviors declare. The integration test `TestPrograms` reads `missing_programs`
from each agent that the suite targets, and fails when one is not empty. Thus on
CI it checks the runner, and against the lab it checks each VM, not the machine
that runs `go test`.

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
spec is part of the full spec ([endpoints](endpoints.md#the-full-spec)). Thus
the SDK client, the UI client and the API docs cover it.

Each behavior that replaced a hand-written domain deleted that domain in the
same change. The two never ran side by side: osapi has no `/api/next` and no
`osapi client next`. [Built-in behaviors](built-in-behaviors.md) has the
decisions of each move.

A change to the routes of a behavior changes the full spec, and `TestJoinedSpec`
in `internal/apicontract` fails. Its golden diff is the change to the API. Write
it again with `-update`, and read it. `TestEveryCommandIsAttached` in
`internal/behaviors/all` fails when a behavior command is not attached to the
command tree.

## Generated, and committed

`go generate ./internal/behaviors/all` runs `internal/behavior/gen`, which
writes:

| File                                                            | Holds                                                                                                                               |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `internal/behaviors/<name>/gen/api.go`                          | the route table, registered from `init`                                                                                             |
| `internal/behaviors/<name>/gen/api_<method>.go`                 | the method's handler and the decoder for its typed input                                                                            |
| `internal/behaviors/<name>/gen/cli.go`                          | the behavior's commands, from its group, by the endpoint layer's command writer                                                     |
| `internal/behaviors/<name>/gen/*_public_test.go`                | a test for each of those files, described under the tests below                                                                     |
| `internal/behaviors/<name>/gen/api.yaml`                        | the behavior's spec, which is also part of the full spec                                                                            |
| `internal/behaviors/all/gen/gen.go`                             | the import of every behavior's generated code: its routes and commands                                                              |
| `docs/docs/sidebar/reference/behaviors/<area>/<name>/<name>.md` | the behavior's page, in the folder of its area: `behavior get` and `method get` as markdown ([The docs site](docs-site.md))         |
| `ui/src/lib/blocks.gen.ts`                                      | a block of the Configure page for each method that the API serves, from `internal/behavior/uiblocks/gen` ([The embedded UI](ui.md)) |

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
response type for each method. Then `internal/behavior/gen/group`, the second
`go:generate` step, builds the spec of each group with the endpoint layer's
builder. The same step writes the full spec of the API
([endpoints](endpoints.md#the-full-spec)). Thus the wording, the error responses
and the validate tags of a behavior's spec are the same as an endpoint's, from
the same code ([endpoints](endpoints.md#behaviors-on-endpoints)). The builder
uses the `openapi3` types of kin-openapi, the library that oapi-codegen uses to
read specs. A test loads each written spec back and validates it. The keys are
in the order of kin-openapi, which is alphabetical, not the order that a person
uses. `TestJoinedSpecIsValid`, in `internal/apicontract`, validates the full
spec with kin-openapi. It found an object field whose `example` was a string,
which a strict tool rejects. The builder now writes the example of an object or
a list as its JSON.

After osapi generates the spec, nothing else holds the spec to the server. Thus
two more checks do it:

- The integration tests send each request and each response through a proxy that
  validates it against the full spec, with `openapi3filter` of kin-openapi
  (`test/integration/spec_test.go`). A request or a response that does not agree
  with the spec fails the run. A request that no operation describes fails only
  when the server serves it. The first runs found an object `example` written as
  a string, and DNS that answered `null` where its spec has a list.
- `just spec-client-check`, one of the slow checks of `just test`, runs
  oapi-codegen with its default options on the full spec into a scratch package,
  and compiles the client. Thus the spec also works for the generator of a
  different person.

The name of a behavior and its Go package are two names. The name is the route,
the command, the permission and the docs page. The Go package is where the
definition lives, and every generator reads it from the package of the types,
not from the name. `osapi behavior create --package <go-package>` sets it. With
no `--package`, it is the name. The scaffold refuses a name that is a Go
keyword, such as `package`, and asks for `--package`. It does not change a name
to make it a Go name. Thus `--name package --package packages` serves `/package`
from `internal/behaviors/packages/`.

`osapi behavior create` also writes its first files with jen, in
`internal/behavior/scaffold_files.go`. Those files are not generated code. A
person edits them from the first minute, so they do not go in `gen/`. But the
rule is the same for each Go file that osapi writes: jen builds it, not a
template. The move from templates did not change the output. For a behavior with
no group and for a behavior under a group, each file was the same, byte for
byte.

`gen/cli.go` puts the docs of each method on its cobra command. `.Describe` is
the `Short`, `.Explain` is the `Long`, and the `Example`s are the command lines
of the `Example`, each under its doc as a `#` line: the group's
`.Example(flags, doc)`. The `reference.Permission` annotation has the permission
of the method, and the `reference.Result` annotation has what each example does
on the host and the refusals. Thus `just cli-docs-generate` writes the CLI page
of a behavior command as it writes the page of each other command, and a
behavior has no page of its own for each method. The output of a command is not
on the page: the same renderer prints each result, and the `output.md` page of
the CLI reference shows it one time.

`just behavior-gen-check`, which `just test` runs, generates the files again. It
fails if any of them changed. Thus a behavior that somebody edits without
`go generate` fails CI. It does not ship commands and pages that describe its
old shape. It compares only the generated files, so other uncommitted work does
not make it fail.

`just behavior-cover-check`, also in `just test`, holds each behavior package to
100% coverage alone. The target for the total of the repository is also 100%.
This check names the behavior package that is below the target.

`just behavior-scaffold-check`, also in `just test`, runs
`osapi behavior create` in a copy of the checkout, generates the new behavior
and runs its tests. Thus the scaffold cannot fall behind the checks that each
behavior must pass. A new check in `behaviortest` that the scaffold does not
obey fails CI. Before this check, the scaffold wrote a file through `h.FS`, and
did not declare it with `behavior.Writes`. Thus a new behavior failed its own
tests (osapi#781). The check also writes a behavior with
`--requires managedfile`. Its tests must fail only on the rule `used`, because
no example calls managedfile until the author writes the call.

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
osapi behavior list                                      # the behaviors and their methods
osapi behavior get --name sysctl                         # surfaces, methods, types, settings, telemetry
osapi behavior method get --name sysctl --method update  # one method in full
osapi behavior spec get                                  # each part of the DSL, and when to use it
osapi behavior validate                                  # every definition against the rules, each with its fix
osapi behavior create --name motd --description "x"      # write a new behavior's layout
osapi behavior create --group network --name neighbors --description "x"  # under a group
osapi behavior create --name ntpconf --description "x" --requires managedfile  # wired to a block
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

`behavior spec get` lists each option, method, refinement, part of an example,
call in a provider and field tag, with what it does and when to use it. It also
lists the generated paths, and what the platform cannot do yet. The table is
`Spec` in `internal/behavior/spec.go`. How to build on other behaviors, and the
building blocks in the binary, are in `behavior chain spec get`, which the chain
layer owns. A test fails on an option, method, part of an example or field tag
of the package without a term in one of the two.

`behavior create` writes `internal/behaviors/<name>/` as a working behavior that
keeps a value in a file, with each standard file. It adds its import to
`internal/behaviors/all`. Before you change anything, it builds, validates,
lints and passes each test with 100% coverage. Thus the layout is stated one
time, in code. An agent starts from a correct skeleton, not from a description
of one.

`osapi token roles list` lists each permission, and which roles give it, with
the permissions of behaviors, as the binary has them. `--json` gives the input
and output as JSON Schema. An agent reads that before it makes a request. Tables
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
the behavior in its own initializer.

## The host a provider gets

A builder gets a `host.Host`, and the provider uses only its services: `h.FS`
for files, `h.Exec` for programs, `h.Sources()` for gohai, `h.Objects`,
`h.FileState`, `h.Facts`, `h.Time()`, the settings and the required providers.
The fake host of `behaviortest` replaces each one: an in-memory filesystem, a
generated mock of the command runner, an in-memory store, the objects of
`Stored`, no facts, and a fixed clock. `h.Facts` returns the facts that the
agent collected last, for a template that a person uploaded, such as the object
of a cron entry. A value that the provider uses itself comes from gohai. Thus a
behavior that uses these services gets its tests with no fake of its own.
`behavior spec get` has a term for each service, under "The host a provider
gets", with what it is, how the tests replace it, and when to use it. A test
fails when a field of `host.Host` has no term.

A read of a fact of the host goes through gohai: a collector with `h.Sources()`,
such as `services.NewWith(h.Sources())`. gohai's runner marks the context of
each command that it runs (`host.FromGohai`), and the `gohai` test check fails a
read whose command does not have the mark. Two reads say `.NotAFact`: the
updates of the package index, which are what the repositories have, and the
definition that netplan has of an interface, which is the configuration of
netplan. A write runs its programs with `h.Exec`. A fact that gohai does not
read is a change to gohai first.

`behavior spec get` lists gohai's collectors, under "gohai collectors", from
`gohai.Collectors()` (gohai v1.11.0). Each entry says what the collector
returns, how a provider builds it, such as `dns.NewWith(h.Sources())`, and the
files and commands that it reads on debian, rhel and darwin. An example gives
those with `Exists` and `Prints`. gohai records the reads on an empty host, so a
collector also reads under those paths when they have content.
`internal/behavior/collectors` makes the section, and the generated Behavior DSL
page has it too.

## Tests a behavior gets from its definition

The examples of a behavior are its tests at each layer above the provider. An
example can tell how the host is before the call:

- `After`: a different method runs first
- `Prints`: the output of a command
- `PrintsAfter`: the output of a command after a different command ran
- `Exits`: the exit code of a command, as `h.Exec.RunCmdFull` returns it
- `Exists`: a file
- `ExistsAfter`: the content of a file after a command ran
- `Links`: a symbolic link, such as `/etc/localtime` to the zone file of the
  timezone
- `OnPlatform`: the platforms the example runs on, for an answer that is the
  platform's own. An Ubuntu host reads `ubuntu` and a Mac reads `darwin`, so one
  example cannot hold for both. Each platform that a method serves must still
  run one of its examples, or the `platforms` check fails.

It can also tell what the call changes, with `Wrote`, `Removed` and `Ran`.

`NotLive("why")` keeps a write example off the live host of the integration
test. The test skips the example and shows why. The provider tests still run it
on the fake host. Use it only for a write whose starting state the methods of
the behavior cannot make on a real host. `After` can call only those methods.
The signal of the process behavior is the example: no method of process starts a
process for the signal to stop (osapi-io/osapi#1112). The lab tests it by hand:
start `sleep 300` over ssh, then signal it.

`PrintsAfter` is for state that a program keeps, not a file. A package query
prints "not installed" until the install runs, and "installed" after it. The
second-run check needs to see that. The `aptpkg` eval of the skill found the
gap. Without it, the install example of a package behavior could not pass that
check correctly, and the session stopped and said so.

`ExistsAfter` is the same for a file that a program changes. The group behavior
reads `/etc/group` through gohai, and `groupadd` changes it. Thus the example
says the file before with `Exists`, and the file after `groupadd -- osapitest`
with `ExistsAfter`. The fake host writes the file when that command runs, and
the second run reads the group and reports `changed: false`.

| Layer       | Where                                              | Checks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Provider    | `behaviortest.Run`, from `behavior_public_test.go` | each example on a fake host per platform that serves its method gives its output and effects; a write declares effects and reports `changed: false` run twice; each command and store call failing in turn never panics                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| API         | `gen/api_<method>_public_test.go`, generated       | a table of literal requests through the real handler and middleware with the job client mocked, every response validated against the generated spec with kin-openapi: each example on one host and broadcast, with its body; the host skipping, failing or timing out; the job client failing (500); a missing item (404); a bad target, each missing required field, a body that is not JSON, a field of the wrong type and each refusal the API can see (400, no job queued); a missing token (401) and a missing permission (403)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Routes      | `gen/api_public_test.go`, generated                | every method's HTTP method, path and permission                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| CLI         | `gen/cli_public_test.go`, generated                | each example's flags, given to the generated command, send the example's input                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Wiring      | `internal/behaviors/all/all_public_test.go`        | every registered behavior validates, every route is mounted and every command attached                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Live server | `test/integration/behavior_test.go`                | every unkeyed read against a real agent; the write examples with `OSAPI_INTEGRATION_WRITE_BEHAVIORS=1`, each reporting the example's `changed` and then `false`; CI's `Integration` step runs the whole suite as root on its throwaway Linux runner, with `OSAPI_INTEGRATION_WRITE_BEHAVIORS=1`; without that variable, as on a Mac, the writes are skipped. The suite refreshes the package index of the target first, with `updatepackages update`, because an install fails with exit status 100 on a lab VM whose lists are old. Each write example starts with its item deleted, as on the fake host, and its items and uploaded objects are deleted again after it, also when it fails. At the end each delete runs again and must change nothing, so the suite leaves the target as it found it. A write example sets its starting state with `After`, which a live host can run, and not with `Prints` or `Exists` alone. A write example with `NotLive` is skipped, with its reason. The test uploads each object of `Stored` with `osapi client file upload` first, and does not run an `.Always()` action a second time. It does not run a `.Disrupts` method, such as a power `reboot`, at all. `behavior spec get` says this under "A write example on a live host", so an author learns it before CI runs the example. A behavior with no `delete` gets its item back after each example: the test reads it with `get` first and writes it back with `update`, so a hostname example renames the runner and then gives it its own name back. With `OSAPI_INTEGRATION_OSAPIFILE`, the same suite starts nothing and tests the controller that the file names, such as the lab's, on the host `OSAPI_INTEGRATION_TARGET` names |

Each failure of `behaviortest.Run` ends with the fix of its check. The checks
are the table `TestChecks`, in `internal/behavior/checks.go`, and
`behavior validate --help` prints them after the rules. The `file-span` check
fails a change to a file that does not go through `atomicfile`: a write, a
removal or a mode change through `h.FS`. Such a change has no `file.write`,
`file.remove` or `file.chmod` span, and is not atomic. The fake host finds it
from the stack of the call. The fix sends a behavior that manages a file to
managedfile, and a building block to `atomicfile.Write`, `Remove` or `Chmod`.

The generated HTTP tests split the cases of each method as the handler tests of
the hand-written domains did: `Test<Method>` for the answers,
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
`behavior create` writes. The methods and the provider of each platform also
have their own tests. Thus each file with code has one, as the rule of the
repository requires.

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
only bad value is empty. A `required` on a struct value, such as an `in:"body"`
struct, needs none. The validator does not examine it, and the rules of the
fields of the struct refuse an empty body. The author writes each bad value. A
generator cannot make one for a custom rule. The endpoint DSL has the same
check, with `.Fails(doc, input)`.

On the fake host, each filesystem, command and store call fails in turn. Each
store read also returns a damaged record in turn: not JSON, empty JSON, and a
file state record with empty metadata.

When sysctl moved, its examples and refusals got to 150 of the 152 statements of
its Debian provider. Its 1,820 lines of hand-written tests got to 152. The two
that remained were a JSON encoding error that a struct of strings cannot make.
Only the test seam of the hand-written tests could get to it.

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
    behavior.Platform(behavior.PlatformDebian, newDebian),
    ...
))
```

Generic work goes in a building block: an internal behavior that does one job,
such as managedfile for a file that osapi manages. `behavior spec get` tells
when to use one and when to make one, and lists each building block in the
binary. The wiring is in three places: `Requires`, `host.Require` in the
builder, and `Call` in the provider.
`osapi behavior create --requires <behavior>[,<behavior>...]` writes the first
two, and a field of the provider for each behavior that it names. The comment on
the field shows the `Call` to write. The provider test gives a mock of each
required provider, and tests that the builder declines a host that does not have
one. The author writes only the calls. Until an example makes a call, the tests
of the behavior fail the rule `used`, and its message tells the author what to
add. A name that the registry does not have, or a name given two times, is
refused. Workflows across hosts are osapi-io/osapi-orchestrator#151. Behaviors
that call outside APIs are osapi-io/osapi#1064.

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
  behavior requires, under the rule `internal`, because nothing can call it. The
  chain layer owns these two rules, and `behavior validate` states them in its
  words. `behavior get` lists what a behavior uses and what uses it. The landing
  page of the Behaviors section has a table of each behavior with the two lists,
  generated from the registry.

`object` is the second internal behavior. It reads an object of the Object
Store: a file that a person uploads one time with `osapi client file upload`,
with its content type, `raw` or `template`, and its SHA-256. It does not render
a template. The behavior that deploys the object renders it. The agent gives the
Object Store to each behavior as `host.Host.Objects`. An agent with no Object
Store has none, and `object` and each behavior that requires it report `skipped`
there. An example says what the store has with
`behavior.Stored(name, content, contentType)`, and the fake host of
`behaviortest` serves it.

`service` is the first behavior that requires the two. Its create gets the
object with `object`, and writes it as the unit file
`/etc/systemd/system/osapi-<name>.service` with `managedfile`. Thus a unit file
goes to the fleet in two steps: upload it one time, then deploy it by its name
to each host. The service writes and acts only on a unit file that `managedfile`
has a record of. The prefix alone is not sufficient: the agent's own unit is
`osapi-agent.service`, and on the lab a delete of the service `agent` would have
stopped the agent.

`certificate` is the second (osapi-io/osapi#1108). It writes the PEM of an
object as `osapi-<name>.crt` in the local directory of the family, the directory
that gohai's `ca_certificates` collector reads:
`/usr/local/share/ca-certificates` on the Debian family,
`/etc/pki/trust/anchors` on SUSE, and `/etc/pki/ca-trust/source/anchors` on the
RHEL family. Then it rebuilds the trust store: with `update-ca-certificates` on
the Debian family and SUSE, and with `update-ca-trust` on the others. The
directory comes from gohai's `cacertificates.LayoutFor`, so a CA that osapi
writes is a CA that gohai reads. A CA that osapi deployed reads by its name,
with `managed`, as a service does. Thus `managedfile` has a provider for
`PlatformLinux` too, not only for the Debian family: its writes are the same on
each Linux family. The behavior declares a provider for `PlatformDebian`,
`PlatformSUSE` and `PlatformLinux`, and each program with `SudoOnPlatform`. Thus
a Debian or SUSE host is not asked for `update-ca-trust`, and a RHEL host is not
asked for `update-ca-certificates` (osapi-io/osapi#1122). A delete runs
`update-ca-certificates --fresh` on the Debian family and SUSE, because without
`--fresh` the links of the CA stay in `/etc/ssl/certs`. osapi does not support
Alpine. There the writer is the reader, and the writes report `skipped`.

A read takes the same name as a write. `list` and `get` show a service that
osapi deployed by the name it was deployed with, such as `app`, not by the name
of its unit, `osapi-app`, and set `managed`. `get` finds it by either name. A
unit with the prefix that osapi did not deploy, such as `osapi-agent`, keeps its
name and is not managed. If the host has a unit `app.service` of its own too,
`get app` gives the service that osapi deployed, because the writes act on that
one. Before osapi-io/osapi#1028 the reads came from gohai with the names of the
units. Thus a `get app` after `create app` was not found, and a person had to
know the prefix.

`managedfile` is the first internal behavior. It writes files on a host, and
keeps a record of them in `file-state`. It operates on each Linux family. A
caller sets the mode, owner and group of the file. A caller can also mark
content as a secret. Then the record keeps no checksum of it, because somebody
can recover a short secret from its SHA-256 by guessing.

The record keeps two checksums. `sha256` is the SHA-256 of the file.
`file status` compares the file on the host with it to find drift.
`object_sha256` is the SHA-256 of the object that the file came from, when the
caller names an object. `file stale list` compares the object in the object
store with it. For a template, the file is the rendered object, so the two
checksums are different. Before osapi-io/osapi#1131 the stale list compared the
object with `sha256`. Thus it showed each template deploy as stale. A record
without `object_sha256`, from a deploy before that change, is stale until the
next deploy. A record that names no object, such as a sysctl file, is never
stale. When the object changes and the file does not, a write changes only the
record and reports a change.

It reads ownership with `stat` and sets it with `chown` through sudo, which
`managedfile` declares. Thus the fake host tests it like each other command. The
`apptoken` eval found that it was missing. A token written through `managedfile`
was readable by each user on the host, and the session stopped and did not write
it.

The Debian provider of sysctl writes and removes its conf files through it. The
code moved out of sysctl without changes. The sysctl provider tests confirmed
this. They did not change, except two marshal-failure cases that moved with the
code.

A behavior is internal when two things are true. An operator would never call it
from the CLI or the API. It is a piece of work that other behaviors share, such
as writing a file or reloading a service. `osapi behavior create` always writes
a behavior that an operator calls, because a new internal behavior has nothing
that requires it yet, and `behavior validate` would fail it.

Shared work becomes an internal behavior at its second use. When one behavior
does something, that is its own code. When a second behavior needs the same
thing, it becomes a behavior that the two require. The build-a-behavior skill
asks this question before somebody writes a behavior. Three internal behaviors
exist now. `managedfile` writes a file that osapi owns. It came out of sysctl,
and each behavior that owns a file on a host requires it. `object` reads an
object from the Object Store. The service, file, schedule and certificate
behaviors require the two. `netplan` writes and applies a file under
`/etc/netplan`, and the dns, interface and route behaviors require it.

A chain across hosts or steps, where the output of one method is the input of
the next, is a workflow. It stays with osapi-orchestrator.

### Chains

The behaviors that a behavior calls, and the ones that they call, are a chain:
`dns → netplan → managedfile`,
`status → (hostname, uptime, os, load, memory, disk)`. The chain has the name of
the behavior at its top. It is not declared on its own. `Requires` on each
behavior makes it (osapi-io/osapi#1000).

`osapi behavior chain` is a group of the command DSL, as `behavior` is:

| Command                       | Does                                                                                      |
| ----------------------------- | ----------------------------------------------------------------------------------------- |
| `chain list`                  | each behavior in a chain, with its tree and what calls it                                 |
| `chain get --name <behavior>` | the calls of each example of the behavior, with what each call sends and gets             |
| `chain validate`              | the chain rules, each with its fix                                                        |
| `chain spec get`              | what a chain is, how to build one, what occurs when a step fails, and the building blocks |

`chain get` does not read a record. It runs each example of the behavior on the
fake host that `go test` uses, and `behavior.Call` records each call under the
call that made it: the behavior, the method, the input, and the output or the
error. `behavior.Record` gives the context that collects the steps. Thus the
tree shows what the code does now, and it cannot be stale. A field with the tag
`secret:"true"` shows as `[redacted]`. `behaviortest.Chains` runs the examples,
in the binary as in the tests.

A real job records its chain with the same mechanism. The job handler of the
agent gives the processor a context from `behavior.Record`, so each
`behavior.Call` of the method adds its step. The response of the job has the
tree as `client.Step`: the behavior, the method, `changed`, the error, the
duration in milliseconds, and the calls of the step. The agent records the tree
also when a step fails, because a failed job is where the tree helps most.
`osapi client job get` prints a line for each host:

```text
ubuntu-1: (netplan get, netplan update (changed) → managedfile update (changed))
```

`client.FormatSteps` writes the line. A run records no input and no output. An
input is redacted only by its top-level `secret` tags, an output is not
redacted, and the content of a managed file can be large. The request and the
response of the job have the input and the output of the method at the top. The
format is the one that a behavior of an extension returns (osapi-io/osapi#1064).
The job view of the UI shows the tree of each host, one row for each call
(osapi-io/osapi#1162). The trace has a span `behavior.<name>.<method>` for each
call, under the span of the call that made it. The audit entry records the tree
of each host that answered before the request returned, also when a step failed
(osapi-io/osapi#1193). `osapi client audit get` prints the chain line, and the
audit view of the UI shows the tree with the component of the job view.
[The audit trail](audit.md#the-steps-come-from-the-job-client-at-request-time)
has why the entry records the tree at request time.

A chain does not roll back. A step that fails returns its error to the step that
called it, and the job fails on that host. The writes before the failure stay on
the host. Only a building block undoes its own change: netplan puts its file
back when `netplan generate` refuses it. When `netplan apply` fails, the new
file stays in `/etc/netplan`, and the job shows the line
`netplan update (failed) → (managedfile update (changed), managedfile update (changed))`.
A test of the netplan provider records this chain through `behavior.Record` and
checks the line. The `Behavior chains` feature page of the osapi docs tells a
caller this story.

The second `managedfile update` puts a mark in the record of the file:
`managedfile.MarkUnapplied` adds the metadata key `osapi.unapplied`. No caller
writes that key. Thus a retry with the same input does not agree with the
record, and `managedfile update` reports a change and writes the record without
the mark. Then netplan runs `netplan apply` again. After an apply that succeeds,
the same input reports no change. Before osapi-io/osapi#1194, a retry found the
same content on disk, reported no change and did not apply the file.
`certificate` and `service` mark the record in the same way when the command
after the write fails: `update-ca-certificates`, `update-ca-trust` or
`systemctl daemon-reload`. When the command fails after a delete, the behavior
puts the file back with the mark, so a retry deletes it and runs the command
again. The record keeps the metadata of a file that osapi stopped managing, and
`managedfile get` gives its `object_sha256`. Thus the file comes back with the
record that it had, and `file stale list` does not change.

The mark keeps the file that the caller asked for. A rollback would also make a
retry apply. But `netplan apply` can fail after it applied a part of the file.
Then the host would use a part of a file that is not on disk. A check of the
host, as sysctl does with the runtime value, is not available for each command:
no command tells whether `systemctl daemon-reload` or `update-ca-certificates`
ran after the last write.

Only an author composes behaviors, in Go, with `Requires`. A user does not
compose behaviors on one host without Go. Multi-step work is an
osapi-orchestrator workflow. This is the current rule, from the decision on
osapi-io/osapi#1063. Extensions (osapi-io/osapi#1064) can change it.

The chain rules are `behavior.ChainChecks`. Two hold when the behaviors are
built, and `behavior validate` checks them too. Two need a run of the examples,
and `go test` checks them through `behaviortest.Run`:

| Rule       | Requires                                                       | Checked by                            |
| ---------- | -------------------------------------------------------------- | ------------------------------------- |
| `requires` | each required behavior is registered, with no cycle            | `behavior validate`, `chain validate` |
| `internal` | an internal behavior has a behavior that requires it           | `behavior validate`, `chain validate` |
| `called`   | a provider calls only the behaviors that its behavior requires | `go test`, `chain validate`           |
| `used`     | an example calls each behavior that a behavior requires        | `go test`, `chain validate`           |

`behavior validate --help` lists `called` and `used` after the rules that
`go test` checks, because `go test` checks them for each behavior. Thus a reader
of the help sees each rule that a test can fail on. `called` holds because the
agent builds the provider of a required behavior, and of no other. `used` finds
a requirement that no example tests, or that the behavior does not need.

There is no chain DSL. The glue between two steps is logic, not a field that
goes from one output to the next input. dns reads the current resolvers and the
netplan ID of the interface before it writes, and netplan puts its file back
when `netplan generate` refuses it. A declarative chain would be too weak for
that, or it would become a programming language. That is what osapi-orchestrator
workflows are for, across hosts. A declarative `behavior.Chain` is worth it when
two or more behaviors only pass the output of one building block to the next,
with no logic.

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

Go reads a tag only by its exact key and value. Thus `secret:"True"`, or the key
`secrte`, makes the field an ordinary field, and nothing reports it. Under the
rule `tag`, `behavior validate` fails each field of an input, nested fields too,
that has a tag key outside `command.KnownTags`. It fails each field of an input
or an output that has a `secret` value other than `true`, or a `telemetry` value
other than `attr`. The command DSL checks the keys of an output, with the same
list, under the rule `output`. Thus one list of tag keys serves the three DSLs.

## A step on the controller

A secret that the agent must not see in plain text, such as a password, cannot
travel in the job. The input of a behavior is the data of its job, and NATS and
the job KV keep that data. A field with the tag `secret:"true"` stays out of the
audit log and the spans, but not out of NATS. Thus a method that takes such a
secret declares a controller step with `.Before(fn)`. The function is
`func(ctx context.Context, in In) (In, error)`, on the input type of the method.

The generated route calls the step through `dispatch.Run`, on the controller,
before it queues the job. The step runs in a span of its own,
`behavior.<name>.<method>.before`. It changes what the caller sent into what the
agent gets: a user's `password` becomes `password_hash` with `password.Hash`,
the SHA-512 crypt hash that `chpasswd -e` takes. `internal/password` has the
hash. The user behavior's `create` and `passwd` each have a step.

Two rules keep the plain secret out of the job:

- **Each field with the tag `secret:"true"` is empty after the step.** If a
  secret field is not empty, `RunBefore` fails, and osapi does not queue the
  job. Thus a step that forgets to clear the password does not leak it.
- **A field that the step fills has the tag `before:"set"`.** The request, the
  command and the block of the UI do not have it, so a caller cannot send a hash
  directly.

Under the rule `before`, `behavior validate` checks the step:

- its signature takes the method's input type and returns it, with an error;
- the behavior is served, because the step runs in its route;
- the input has a secret field, which the step keeps out of the job;
- each field with the tag `before` has a step to set it, and the value of the
  tag is `set`.

An example of the method has the password and its hash. The route test and the
integration test send the password, as a caller does. The route test then checks
that the job has a hash and no password, and not the same hash, because each
hash has a new salt. The provider test gets the hash, as the agent does. The
audit log records the request, with the secret redacted, as for each other
method.

A secret field cannot have the rule `required`. The agent checks the input
again, and the step has cleared the field. Thus the provider refuses a call with
no hash, and an example under `Fails` shows the refusal.

## Typed values

A value that the DSL selects from a fixed set is a named type with constants, as
`Verb` is. A platform is a `PlatformName`: `PlatformLinux`, `PlatformDarwin`,
`PlatformDebian` or `PlatformSUSE`. `Platform`, `On`, `RunsOnPlatform`,
`SudoOnPlatform` and `OnPlatform` take one. Go converts an untyped string
literal to a named type. Thus `Platform("debain", ...)` compiles, and
`behavior validate` is the guard: under the rule `platform`, it fails a name
outside `KnownPlatforms()`. Before this rule, `Platform("debain", ...)` fell
back to the linux provider, and a behavior with no linux provider skipped each
method on Debian with no error. To name a new family of gohai, add its constant
to `KnownPlatforms` first.

The other typed values:

- **A group** is a `GroupName`, such as `GroupNetwork`. The group is a path
  segment, a command and the prefix of the permissions of each behavior in it.
  Thus a misspelled group made a new route, a new command and a new permission,
  and the role rule granted the permission. `behavior validate` refuses a group
  outside `KnownGroups()`, under the rule `name`.
- **An area** is an `area.Name` of `internal/area`, such as `area.Hardware`.
  `area.All` lists them, and `behavior validate` refuses an area outside it.
- **A content type** is `client.ContentType`: `ContentRaw` or `ContentTemplate`.
  `Stored` in an example, the file behavior, the file provider, the agent and
  the file endpoints use the constants. The value that a header or a form
  carries is a string, and the conversion is at that boundary.

Two tests in `internal/dslcheck` keep the DSLs typed. They apply to the behavior
DSL, the endpoint DSL and the command DSL:

- **`TestStringsAreReviewed`** reads the exported API of the three DSLs. It
  lists each function or method parameter, and each struct field, of type
  `string`, `[]string` or a map with string keys. It compares the list with
  `internal/dslcheck/testdata/strings.txt`, which gives each string a category
  and a reason: `identity`, `free text`, `program`, `path pattern`, `fixture`,
  `boundary` or `checked`. A `checked` string picks from a set, and a validate
  rule or a test checks it. A new string fails the test until it is a type with
  constants, or until the file has it with its reason. An entry that the API no
  longer has fails the test too.
- **`TestNoLiteralForATypedValue`** reads the definitions under
  `internal/behaviors`, `internal/controller/endpoints` and
  `internal/cli/commands`. It fails a string literal where a typed value of a
  DSL goes: an argument, a conversion or a field of a composite literal. Thus
  `behavior.Under("netwrok")` fails before a test runs, and the constants are
  the only way to name a value. Generated files are exempt: a generator writes
  each permission as a literal, because the constant of a new permission is
  written after the routes, from the registry that the routes register in.

`behavior new` writes `Under(behavior.GroupNetwork)` and `Area(area.Config)`,
and it refuses a group outside `KnownGroups()`.

Redaction matches names, as the denylist does. If you tag a field `value` as
secret, osapi redacts each request field with the name `value`, in each
behavior. Give a secret field a name that tells what it has.

The value still comes as a CLI flag, such as the `--password` of `user create`.
A read from standard input or a prompt is not built.
