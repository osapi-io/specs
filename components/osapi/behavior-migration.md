# Moving domains to behaviors

osapi moves from providers to **behaviors**. With providers, people write each
layer by hand for each domain. With behaviors, an author writes the typed inputs
and outputs, and the logic that changes the host. osapi generates everything
between the caller and that logic. The REST API, the SDK and the CLI keep their
current shape. What changes is who writes them.

This page tracks the move: what remains to build, the order, and what must be
true before each step is complete. [Behaviors](behaviors.md) describes what is
already built. Content moves there from here as each step merges. When nothing
here is still a plan, this page goes away. [Providers](providers.md) and
[building a domain](domains.md) describe the domains that did not move yet.

## Behaviors built on other behaviors

Built: `behavior.Requires` and `behavior.Internal`. sysctl proves them, because
it requires the internal `managedfile` behavior.
[Behaviors](behaviors.md#behaviors-built-on-other-behaviors) describes them.

What remains: the other domains whose providers depend on each other must use
requirements when each one moves. An example is cron, which uses the file
provider.

## What the platform owns

`internal/behavior` has everything that is the same for each behavior, in one
location. A behavior author never sees it:

| Convention                                        | Today                             | After                                   |
| ------------------------------------------------- | --------------------------------- | --------------------------------------- |
| The `{job_id, results[]}` envelope                | Restated in every spec            | Built from the definition               |
| Per-host `hostname`, `status`, `error`, `changed` | Restated in every spec            | Built from the definition               |
| 400, 401, 403, 404 and 500 with `ErrorResponse`   | Listed per operation              | Built from the definition               |
| `{hostname}` and broadcast targets                | A branch in each handler          | The runtime the generated handlers call |
| Status mapping, including `skipped` and `timeout` | A switch in each handler          | The runtime the generated handlers call |
| The job payload                                   | A map in, an anonymous struct out | The behavior's input type               |
| Dispatch on the agent                             | Three levels of string switch     | A lookup by behavior and method         |
| Permission strings                                | Spec, SDK, UI, three docs pages   | Derived from `Read`/`Write`             |
| The route and the CLI command                     | A handler file and a command file | Registered at startup                   |

This answers the question "how does a person who adds a behavior know what the
spec must be". That person does not write the spec. New contributors make errors
in the conventions of that table, and those conventions are not the work of the
contributor now.

## What the cutover changes

[Behaviors](behaviors.md) describes what is built so far:

- a generated handler for each method, with its HTTP tests
- the generic agent processor
- generated commands
- the generated spec and docs pages

A domain moves in one change: the behavior goes to `/api` and `osapi client`,
and the hand-written domain is deleted. The two never run side by side. Before
sysctl's cutover, osapi served it under `/api/next` and `osapi client next`
beside the hand-written domain. Its cutover (osapi-io/osapi#731) removed
`behavior.Next`, the `/api/next` routes, `osapi client next`, the next spec and
its docs section.

A test of the branch on real hosts showed that the reads of sysctl were
incorrect. `list` and `get` reported only the parameters that osapi wrote. Thus
a new host listed nothing, and `get` answered 404 for a key that the kernel has.
Ansible, Salt and Puppet all read the host as it is. Thus:

- `list` now reads each parameter under `/proc/sys`, with an optional `prefix`.
- `get` reads any key.
- Each entry tells if osapi manages it.
- `update` sets and manages a parameter, if osapi managed it before or not.

The cutover changed these parts:

- **API.** Its hand-written handler under `internal/controller/api/node/` and
  its oapi-codegen server code are deleted.
- **CLI.** Its hand-written `cmd/client_node_*` files are deleted.
- **Agent.** Its hand-written processor is deleted. Its provider is already in
  the directory of the behavior, as `<platform>.go`, with its tests moved
  without changes. sysctl showed that this move is safest before the cutover.
  The platform files that the behavior does not declare, `darwin.go` and
  `linux.go` for sysctl, are deleted with the processor that built them.
- **SDK.** The routes and operationIds are the hand-written ones. Thus the
  client that oapi-codegen generates from the joined spec keeps its methods, and
  `client.Sysctl` continues to work over it. Its entries get `managed`, and its
  list takes a `prefix` (`SysctlListOpts`). The old job operations,
  `node.sysctl.*`, are deleted: a behavior's job is `behavior.sysctl.<method>`.
  To generate those typed services from the spec is a later step.
- **Spec.** Its part of the generated spec joins the main spec, and its
  hand-written YAML is deleted. What reads the spec continues to work: the
  TypeScript client of the UI, the API pages of the docs site, and outside
  clients that people generate from it.

The first cutover brought two checks. After osapi generates the spec, nothing
else holds it to the server:

- **The spec still describes what the server does.** The integration tests send
  each request and response through a proxy that validates it against the joined
  spec, with `openapi3filter` of `kin-openapi`
  (`test/integration/spec_test.go`). A request or a response that breaks the
  spec fails the run. A request that no operation describes fails only when the
  server serves it. Its first runs found an object `example` written as a
  string, and DNS answering `null` where its spec says a list.
- **The spec still works for the generator of a different person.**
  `just spec-client-check`, one of the slow checks of `just test`, runs
  oapi-codegen with its default options on the joined spec into a scratch
  package, and compiles the client.

The controller-only endpoints (agent, audit, facts, file, health, job and
telemetry) are not behaviors. They move to a DSL of their own, which
[endpoints](endpoints.md) designs. No cutover of a behavior occurs before that
DSL is settled.

## Discovery for agents

Built:

- [help as JSON](cli.md#help-as-json-for-agents)
- the [`--json` error document](cli.md#errors-go-through-one-handler)
- [`behavior list`, `get` and `validate`](behaviors.md#inspecting-behaviors-from-the-cli)
- [`osapi init` with the embedded skill](agent-skills.md)
- the build-a-behavior skill, in `.claude/skills/` of the osapi repository, and
  the `osapi behavior create` command that it uses
- evals for the skill, in its `evals/`

This plan first said that the skill has no scaffold command, and that it keeps
templates in its references for the agent to copy. The build showed that the
templates were a second copy of the layout, which people must keep current by
hand. Thus the layout now exists one time, as the templates of the command. A
test runs them from start to end: the new behavior must build, validate and pass
each test. The skill sends the agent to the command, to
`go doc ./internal/behavior`, and to `behavior get` and `validate`. Refer to
[behaviors](behaviors.md#inspecting-behaviors-from-the-cli).

Each eval is a request that runs in a new session, and commands check the
result. The evals cover these cases:

- a served behavior
- a behavior that runs a program with sudo and declares refusals
- an internal behavior that a different behavior requires
- a behavior for one platform
- a secret input
- a behavior in a group
- a request that the platform cannot express. It passes when the skill says so.
- a request that is not clear enough to build. It passes when the skill asks.

The first run of the eval for the internal behavior found that the fake host
could not model state that a program keeps. `PrintsAfter` now does this. The
build of the grouped eval found that `osapi behavior create` could not write a
behavior in its group. `--group` now does this.

## Next

4. The cutover of sysctl: built (osapi-io/osapi#731). It removed
   `behavior.Next`, so each later domain moves in one change. It corrected
   `references/migrating.md` of the build-a-behavior skill, which it followed.
5. `Requires` and `Internal`: built.
6. Evals for the build-a-behavior skill: built.
7. The test of the full idea. In a new session, ask an agent to build a new
   behavior with only that skill and the CLI. Where it stops, fix the skill or
   the CLI, not the output of the agent. Run it again until it builds one
   without help.
8. The other domains. A pull request can move more than one domain when they
   have the same shape. The node reads moved together: uptime, OS, memory, load
   and disk, each over `host.Host` and not gopsutil, so that the fake host can
   run their examples. Hostname moved with them, and needed `.On` for an update
   that runs only on the Debian family.
   - Generate the typed services of the SDK from the joined spec, after the part
     of each behavior joins it. Then the SDK comes fully from the spec, and
     never imports a behavior.
   - Group moved on its own (osapi-io/osapi#992). The user domain kept the user
     and SSH key routes until the behavior DSL got a step on the controller,
     `.Before` (osapi-io/osapi#1094). The duplicate-route check works for each
     route, not for each directory, so a domain can lose some routes to a
     behavior. The group behavior reads `/etc/group` through gohai on each
     platform, so Fedora and macOS answer list and get, and it changes groups on
     the Debian family. Its permissions are `group:read` and `group:write`, the
     name of the behavior, not `user:read` and `user:write`. The built-in roles
     grant them. A custom role that named `user:write` for groups must name
     `group:write`.
9. Stop using the term `provider`. Rewrite [providers](providers.md) and
   [building a domain](domains.md) for behaviors. Delete this page when nothing
   in it is still a plan.

The README got its shape from the README of swamp when sysctl was built from its
definition: a claim, why it is better, a start with `osapi init`, the requests
to try, and the core concepts. Behaviors are a core concept there. Each line
describes something that osapi does, and nothing else.

## What blocks the other domains

These hand-written node operations use something that a behavior cannot express
yet. Each is a platform change. This page designs it before somebody builds it.
Each one unblocks a set of domains. Action methods, such as `service restart`,
and the Object Store on `host.Host` are built (osapi-io/osapi#985). A resource
under another is built with `behavior.Of` (osapi-io/osapi#986). Thus they are
not in the table. A container's images are at `/container/docker/image/{image}`,
which is not under a container, so they need no `Of`:

| Missing                                                     | Operations                                                 | Blocks                             |
| ----------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------- |
| The `execute` and `shell` permissions beside read and write | command exec and shell, power, process signal, docker exec | command, power, process, container |

The status summary of a node is the `status` behavior, at
`GET /api/node/{hostname}/status` (osapi-io/osapi#945). It requires the
hostname, uptime, os, load, memory and disk behaviors, and calls the get of each
through `behavior.Call`. A read that fails is in `errors`, and the others still
answer. Thus no hand-written node spec is left. Timezone is a behavior too
(osapi-io/osapi#964): gohai reads it on every platform, and timedatectl sets it
on the Debian family. Packages are two behaviors (osapi-io/osapi#964).
`package`, whose Go package is `packages` because `package` is a Go keyword,
reads through gohai on every platform, and installs and removes with apt-get on
the Debian family. `updatepackages` lists and refreshes the package index with
apt, because the index is what the repositories have, not a fact about the host.
Its refresh reports `changed: true` only when a repository's Release file under
`/var/lib/apt/lists` changed. Ansible's apt module reports a change on each
update that runs, by the stamp time, and offers `cache_valid_time` to skip one.
That fails the rule that a second identical call changes nothing, and apt-get's
`Get:` lines do not tell either: the CI runner prints them on each run. DNS is
the `dns` behavior under `network` (osapi-io/osapi#988). gohai reads it on every
platform, and it writes through `netplan`, an internal behavior that writes a
file under `/etc/netplan`, validates it with `netplan generate`, and applies it
(osapi-io/osapi#987). When `netplan generate` refuses the file, the file gets
back the content that it had, or a new file is removed. A DNS write goes under
the netplan ID of the definition that matches the interface, such as
cloud-init's `all` for `en*`: netplan ignores a second definition of the same
interface, so a file under the interface's name changed nothing on the lab's
Ubuntu image. `netplan status` lists only the interfaces that netplan manages.
Thus whether a host has an interface is gohai's to read, not netplan's: on the
lab, a dummy interface that netplan did not manage was not in the list.

Services are the `service` behavior (osapi-io/osapi#991). gohai reads the
services of each Linux host with `systemctl`. On the Debian family, create and
update deploy an uploaded object as `/etc/systemd/system/osapi-<name>.service`
through the `object` and `managedfile` behaviors, and delete, start, stop,
restart, enable and disable are actions on a service that osapi deployed. An
action reports `changed: true` only when systemd says the service moved: an
enable of a unit with no `[Install]` section, which systemd calls static, runs
and changes nothing. On the lab, the hand-written domain reported a change on
each such enable. The hand-written domain also read the main process of a
service. gohai does not read it, so the behavior does not have it. gohai lists
only the units that systemd has loaded, so a service that is stopped and
disabled is not found until gohai reads the unit files too (osapi-io/gohai#321).

Interfaces are the `interface` behavior under `network` (osapi-io/osapi#989),
whose Go package is `iface` because `interface` is a Go keyword. gohai reads
each interface on every platform. A write on the Debian family goes only under
the interface's own definition: an interface that a match defines, such as
cloud-init's `all`, is refused. A static address under `all` changes each
interface that the match takes, now and later. On the lab that match took one
interface, so a check that counted the interfaces let the write through. The
write examples run on `osapi0`, a dummy interface that the integration job
makes, and set no gateway. A default route through `osapi0` would take the
traffic of the runner.

Routes are the `route` behavior, under the interface with `behavior.Of`
(osapi-io/osapi#990, #998): `osapi client node network interface route`, at
`/api/node/{hostname}/network/interface/{name}/route`. gohai reads the routes of
an interface on every platform. A write on the Debian family goes only under the
interface's own definition, as for interfaces, and refuses a default route: the
interface behavior sets the gateway. Each call is one route, as `ip route add`
and `ip route del` are, with a flag for each value: `--destination` in CIDR
notation, `--via` of the same family, and an optional `--metric`. Each has its
own `validate` rule; only the family of the gateway against the destination is
the provider's to check. A route was first a string as `ip route` writes it, a
list of them a call, which replaced all the routes of the interface. That needed
a rule of its own to parse the string. The destination is in the body, not the
path, of an update or a delete: the router cannot match an encoded slash in a
path segment, so `10.0.0.0%2F8` has no route. The routes of the whole host are
in the facts of the agent; the behavior has no list of them. The interface name
rule, `interface_name`, is in the shared registry, because dns, interface and
route each use it. With routes, no hand-written code reads or writes netplan.
The others fit now: NTP, log, certificate and ping. The "Not yet" list of the
build-a-behavior skill is this table. Thus an agent that gets a request for one
of these says so, and does not add code around the platform.

The cutover of a domain deletes its hand-written handler tests. Thus each case
in them must go somewhere first:

- into the generated HTTP tests of the behavior, which cover the cases that each
  method has
- or into an example or a refusal on the method, which covers the cases that are
  special to the domain

A domain does not get its cutover while a hand-written case has neither. Its
provider tests move with the provider and are not deleted.

## Internal behaviors the migration extracts

Shared work becomes an internal behavior at its second use. This is the rule of
two. When one domain does something, that is the code of that domain. When a
second domain needs the same thing, it becomes a behavior that the two require,
not a copy.

`managedfile` is the first. It came out of sysctl, because each domain that owns
files on a host needs what it does. These are the candidates. More than one
domain does each of them now:

- **Package install and removal.** The package domain does it, and each behavior
  that installs what it manages needs it.
- **Service control**: reload or restart after a change. The service domain does
  it, and NTP, hostname and cron do it again.
- **File deploy from the object store.** The file domain and cron do it. The
  `object` behavior reads the object, and `managedfile` writes it. The service
  behavior is the first that requires the two.
- **Run a command and read its output.** Each provider does it now through
  `h.Exec`. It becomes a behavior only if it gets checks that each caller needs,
  for example a refusal of input that can get to a shell.

A chain across hosts or across steps is a workflow. That is the job of
osapi-orchestrator, not a requirement.

## What will surprise somebody

**The spec stops being the source.** If a contributor edits the generated spec
by hand, the next `just generate` writes over the change. The file stays in git,
so that a reviewer can read the diff. `just behavior-gen-check`, which
`just test` runs, generates the files again and fails on each difference.

**Not everything fits the template.** File upload, `docker exec` and command
execution stream data, or take multipart bodies. The generated handlers cover a
request that has one typed input and one typed output for each host. A behavior
that needs more keeps a hand-written handler for that one method. The definition
says so explicitly, not by omission. That handler registers its own route next
to the generated routes.

**Path parameters lose their validation tags in strict-server generation.** That
is why `node/sysctl/validate.go` states `required,min=1,sysctl_key` again now.
The generated decoder of a behavior validates the input type after it binds the
path. Thus the second statement is not necessary, and nothing generates it.

**The types of the SDK change, and the orchestrator pins a tag.** SDK methods
start to return behavior types, not the hand-written `SysctlEntryResult`.
Nothing breaks in osapi-orchestrator until somebody updates the pin. Then
`pkg/orchestrator/ops.go` breaks for each migrated behavior. Each migration
merges with an orchestrator change next to it.

**The certificate domain does not obey the naming.** It serves `/api/node/...`,
but dispatches under its own category. The names of the docker operations look
like `docker.create.execute`. They move last, and the move fixes their names.

## Not covered here

The UI. Its domain blocks in `ui/src/components/domain/` stay hand-written.
Forms built from the JSON Schema are possible later, and are not part of this
plan.

Workflows. osapi-orchestrator already puts operations together across hosts. Its
101 step functions in `ops.go` can become one generic step over the registry.
That is its own change, in its own repository, after this one.

Docs for the commands of the platform itself. `start`, `token`, `agent` and the
controller-only `client` commands keep hand-written pages until they move onto
the same registry. The SDK reference can also come from behaviors in the same
way. That is not part of this plan.

Behaviors from outside osapi. Each behavior is a package under `internal/`, and
one line in `internal/behaviors/all` registers it. Thus the behavior of an
outside author is a pull request here. A behavior from a different module in a
custom build, as people publish swamp extensions, needs a public extension API.
Somebody must design that API. Making the current internals public is not
sufficient. That is a separate decision, and this page does not make it.

An MCP server. The registry makes one easy to write. But CLI help and
`behavior get` are sufficient for an agent, and a second interface is a second
thing to keep consistent.
