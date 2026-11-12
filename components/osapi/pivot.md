# The pivot to behaviors

osapi is moving from providers, where every layer is written by hand for every
domain, to **behaviors**: a behavior author writes typed inputs and outputs and
the logic that changes the host, and osapi generates everything between the
caller and that logic. The REST API, the SDK and the CLI keep their current
shape. What changes is who writes them.

This page is the plan. [Providers](providers.md) and
[building a domain](domains.md) describe the system as it is today, and each
gets corrected as the work lands.

## Why

Adding a domain is slow because most of the code is glue, not logic. Measured on
`main` on 12 November 2026:

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
domain has to reproduce all of it from convention. And an agent asked to use
osapi has nothing to discover operations from: no `init`, no machine-readable
help, no schema output.

## What a behavior is

A behavior is one directory holding everything specific to one area of the host:
the definition, the input and output types, the logic for each platform, and the
tests. It is what a provider is today, plus the declaration the rest of the
system is built from when osapi starts.

```
pkg/behavior/sysctl/
  behavior.go     the definition: name, methods, types, verbs
  types.go        inputs and outputs, with json, validate and doc tags
  debian.go       the logic, unchanged from the provider
  darwin.go
  linux.go
  *_test.go
```

The definition looks like this:

```go
var Behavior = behavior.Define("sysctl", "Kernel parameters under /etc/sysctl.d",
    behavior.Node,
    behavior.Read("list", List),
    behavior.Read("get", Get).Key("key"),
    behavior.Write("create", Create),
    behavior.Write("update", Update).Key("key"),
    behavior.Write("delete", Delete).Key("key"),
)

type GetInput struct {
    Key string `json:"key" validate:"required,sysctl_key" doc:"Parameter name, e.g. net.ipv4.ip_forward"`
}

type Entry struct {
    Key   string `json:"key"   doc:"Parameter name"`
    Value string `json:"value" doc:"Current runtime value"`
}

func Get(ctx context.Context, p Provider, in GetInput) (Entry, error)
```

`Read` and `Write` carry the decisions a provider author makes today by copying
another domain: the HTTP method, the permission (`sysctl:read` or
`sysctl:write`), whether the result carries `changed`, and whether a retry is
safe. `Key` names the input field that goes in the path, so
`GET /api/node/{hostname}/sysctl/{key}` comes from the definition rather than
from the spec.

`Node` and `Under` say where the behavior sits, which is the decision a
contributor makes today by picking a directory under
`internal/controller/api/node/` and a parent command in `cmd/`:

```go
behavior.Define("dns", "DNS resolver settings", behavior.Node, behavior.Under("network"), ...)
// /api/node/{hostname}/network/dns
// osapi client node network dns get
// network:read and network:write
```

- `Node` means the work runs on a host, through the job system. Every behavior
  is a node behavior. What the controller answers itself, audit, jobs, agent
  enrollment and health, stays part of the platform and is not a behavior,
  because it never reaches a host.
- `Under` nests a behavior inside a group, as `network dns` and `network route`
  are today. Without it a behavior sits directly under `node`. The group is a
  path and a command, not a behavior of its own.
- The permission comes from the top-level group, so `dns` under `network` is
  `network:read`, which is what it is today.

The method signature is the whole contract the author writes against. It takes
one typed input and returns one typed output or an error. Unsupported platforms
return the shared unsupported error, as they do now.

The behavior lives under `pkg/` because the SDK has to return its types to
callers outside this module, and Go does not let them name a type from
`internal/`. The logic is public as a result. That is harmless, since it only
does anything on an agent, and it buys one directory per behavior instead of
two.

## What the platform owns

Everything that is the same for every behavior is written once, in
`pkg/behavior`, and a behavior author never sees it:

| Convention                                        | Today                             | After                           |
| ------------------------------------------------- | --------------------------------- | ------------------------------- |
| The `{job_id, results[]}` envelope                | Restated in every spec            | Built from the definition       |
| Per-host `hostname`, `status`, `error`, `changed` | Restated in every spec            | Built from the definition       |
| 400, 401, 403, 404 and 500 with `ErrorResponse`   | Listed per operation              | Built from the definition       |
| `{hostname}` and broadcast targets                | A branch in each handler          | One generic handler             |
| Status mapping, including `skipped` and `timeout` | A switch in each handler          | One generic handler             |
| The job payload                                   | A map in, an anonymous struct out | The behavior's input type       |
| Dispatch on the agent                             | Three levels of string switch     | A lookup by behavior and method |
| Permission strings                                | Spec, SDK, UI, three docs pages   | Derived from `Read`/`Write`     |
| The route and the CLI command                     | A handler file and a command file | Registered at startup           |

This is the answer to "how does somebody adding a behavior know what the spec
should be". They don't write it. The conventions in that table are the ones a
new contributor gets wrong, and they stop being the contributor's job.

## Registered at startup, not generated

A behavior's route and CLI commands are built when osapi starts, from the
registry, rather than written to files:

- **API.** The controller walks the registry and adds each method's route to the
  router, all served by one generic handler. The hand-written code under
  `internal/controller/api/node/` goes away, and so does the oapi-codegen server
  code for each domain. What stays in `internal/controller/api` is the platform:
  the router, auth, the generic handler, and the controller-only endpoints.
- **CLI.** `osapi client node sysctl get --key ...` is built at startup from the
  same definition: flags from the input type's tags, table columns from the
  output type's fields, rendered through `internal/cli`. The 84 hand-written
  `cmd/client_node_*` files go away with nothing generated in their place.
- **SDK.** One generic call, `sdk.Run[In, Out]`, using the behavior's own types,
  with thin typed wrappers where a caller wants `client.Sysctl.Get`. There is
  nothing to convert, so the 127 converter functions go.
- **OpenAPI.** Still generated, by `osapi gen` from the registry, filling the
  conventions in the table above with each behavior's types. It is a document
  now: the docs site and outside clients read it, and nothing in osapi compiles
  against it. It stays committed so a reviewer sees an API change in the diff.

The earlier plan generated a handler adapter, SDK methods and CLI commands as
files. Building them at startup removes those files entirely. A generated file
is one more thing that can go stale and one more place a contributor edits by
mistake, and none of these needs to exist on disk. A new behavior becomes one
directory plus one line registering it.

### What still reads the spec, and what stops

The behavior definition is the one source, and the spec is generated from it, so
the two cannot disagree. oapi-codegen is no longer the thing that holds the
server to its contract. For behaviors it stops running:

| Today, generated by oapi-codegen from hand-written YAML | After                                               |
| ------------------------------------------------------- | --------------------------------------------------- |
| A strict-server interface per domain, `*.gen.go`        | Gone. Routes come from the registry                 |
| The Go SDK client, `pkg/sdk/client/gen/client.gen.go`   | Gone for behaviors. `sdk.Run` uses their own types  |
| Request validation through the generated types          | The generic handler validates the input type's tags |

What still reads the generated spec keeps working without a change: the UI's
TypeScript client under `ui/src/sdk/gen/`, the API pages on the docs site, and
any outside client in another language, which can generate itself from the spec
with oapi-codegen or any other OpenAPI generator.

The controller-only endpoints, audit, jobs, agents and health, keep their
hand-written specs and oapi-codegen for now. They are not behaviors, and moving
them onto the same registry is a separate decision once behaviors have proved
out.

The cost is that a route or a command can no longer be found by its file name.
`osapi behavior list`, `osapi help --json` and the generated spec are the index
instead.

## Discovery for agents

Two skills, because an osapi behavior is Go compiled into the binary. A behavior
cannot be added at runtime, so building one is a change to this repository:

| Skill               | For                         | Where it lives                                                   |
| ------------------- | --------------------------- | ---------------------------------------------------------------- |
| Using osapi         | an agent operating a fleet  | embedded in the binary, installed by `osapi init`                |
| Building a behavior | an agent writing osapi code | the osapi repository's `.claude/skills/`, replacing add-a-domain |

The commands both skills drive, every one answering in JSON:

- **`osapi init [--tool claude|codex]`** writes the using-osapi skill into the
  repository, from copies embedded with `go:embed`, and a section in
  `AGENTS.md`. Running it again after an upgrade rewrites them, so the skill
  matches the binary on the path.
- **`osapi help <command> --json`** prints the command tree as JSON: flags,
  which are required, exit codes and error codes. The skill tells the agent to
  run it before a command rather than guess flags.
- **`osapi behavior list`** and **`osapi behavior describe <name> [<method>]`**
  print the behaviors on the binary and each method's input and output fields,
  in the CLI's table style, or as JSON Schema with `--json`.
- **`osapi behavior validate`** checks every definition against the platform's
  rules: a placement, unique routes, input types whose tags validate, an output
  that carries `changed` for a write. It is the check an agent runs after
  writing a behavior, before the tests.
- **`--json` on every command**, and errors under `--json` as one document on
  stderr, `{"error", "code"}`, with fixed exit codes and each command's codes
  listed in its `help`. Today errors under `--json` are log lines.

Each skill is small: a routing table and a few rules, with detail in
`references/` files that load only when a request needs them. The docs site is
not copied in, because every session would pay for it in context.

The building-a-behavior skill has no scaffold command behind it. Its references
hold the templates, the agent writes the files, and it checks its own work in a
loop: `go test` for the behavior's package, `osapi behavior validate`,
`osapi behavior describe <name> --json` to see it registered with the right
schemas, then a smoke run of each method against `osapi start` with `--json`.

Both skills carry evals: whether the skill triggers on the requests it should,
whether it routes to the right reference, and whether that reference is enough
on its own. They are how the skill gets tuned until an agent can build a
behavior with nothing else.

## Cleaning up the CLI first

An audit of `cmd/` on 12 November 2026 found one command to remove and no
consistent styling.

**`osapi job` goes.** It is a parent command with no subcommands. Its help
promises "list, get, cancel, retry", but those live under `osapi client job`,
and no cancel command exists anywhere. `jobCmd` is referenced only by its own
`AddCommand`, and no docs page mentions it. Every other top-level command is in
use: `start`, `agent`, `controller`, `nats server`, `token`, `version` and
`client`.

The pivot removes no further commands. The 84 `client node ...` files become
generated from their behaviors and keep their names, so scripts and docs that
call them do not change.

**The CLI gets one style, taken from the logo.** osapi's table output already
used lipgloss, but with its own palette, while help was cobra's default and
errors were slog lines. The theme follows the package the owner's other Go CLIs
share (`internal/cli/theme.go` in kvlt, meshx, jot, grind, tlock and agentpack).
What it looks like and the rules a command follows are in
[the CLI's output style](cli.md#output-style).

The style comes first because every command added after it, `behavior describe`
included, renders through the same helpers and needs no styling of its own.

## The first behavior is sysctl

sysctl has five methods covering both reads and writes, three platform files
(`debian.go`, `darwin.go`, `linux.go`), and an integration test in
`test/integration/sysctl_test.go`. It is complete enough to exercise every
convention in the table and small enough that the generated output can be read
line by line.

The migration is done when:

1. The spec `osapi gen` writes for sysctl matches today's. The diff of the
   sysctl paths and schemas in `internal/controller/api/gen/api.yaml` before and
   after is empty, apart from descriptions that came from `doc` tags.
2. The existing sysctl integration tests pass unmodified.
3. `osapi behavior describe sysctl` prints the five methods.
4. The files a new sysctl method would touch are counted. If the answer is not
   the behavior directory and nothing else, the platform is missing something.

The old provider path and the new behavior path run side by side, because the
agent's top-level `Registry.Dispatch` already looks up by category and takes no
edits. Domains move one at a time.

## The order of work

1. The CLI cleanup: `osapi job` removed, and the logo theme for help, output and
   errors. Done first because every command added after it renders through the
   same helpers.
2. The building blocks: `pkg/behavior` with `Define`, `Node`, `Under`, `Read`,
   `Write`, the registry, JSON Schema from tags, and registration at startup for
   routes, agent dispatch and CLI commands. sysctl moves to
   `pkg/behavior/sysctl` and its old handler, processor and command files are
   deleted. Pass criteria 1 to 4 above.
3. The agent commands: `osapi help --json`, `behavior list`,
   `behavior describe`, `behavior validate`, the `--json` error document, and
   `osapi init` with the using-osapi skill.
4. The building-a-behavior skill: routing page, templates in its references, the
   check loop, and evals.
5. The test of the whole idea. In a fresh session, an agent is asked to build a
   new behavior with only that skill and the CLI. Where it gets stuck, the skill
   or the CLI is fixed, not the agent's output, and it is run again until it
   builds one unaided.
6. The remaining domains, one per pull request.
7. `provider` is retired as a term, and [providers](providers.md) and
   [building a domain](domains.md) are rewritten for behaviors.

The README changes when step 3 lands, because `init` is its first claim:

> Typed, repeatable operations for Linux hosts. Built for agents, there to
> empower humans.
>
> Give an agent a fleet of Linux hosts without handing it a shell. Every change
> is a typed operation, checked before it is queued, safe to run twice, and
> recorded.

That is followed by short lines for any harness, typed operations, repeatable,
one host or many, queued not called, four ways in, and see what happened. Every
line describes something osapi does once step 3 ships, and nothing else.

## What will surprise somebody

**The spec stops being the source.** A contributor who edits the generated spec
by hand has their change overwritten by the next `just generate`. The file stays
committed so the diff is reviewable. Nothing in CI catches a hand edit today, so
step 2 adds a check that runs `just generate` and fails on any difference.

**Not everything fits the template.** File upload, `docker exec` and command
execution stream or take multipart bodies. The generic handler covers a request
that has one typed input and a per-host typed output. A behavior that needs more
keeps a hand-written handler for that one method, and the definition says so
explicitly rather than by omission. That handler registers its own route beside
the generated ones.

**Path parameters lose their validation tags in strict-server generation.** That
is why `node/sysctl/validate.go` restates `required,min=1,sysctl_key` today. The
generic handler validates the behavior's input type after the path is bound,
which removes the restatement rather than generating it.

**The SDK's types change, and the orchestrator pins a commit.** SDK methods
start returning behavior types instead of the hand-written `SysctlEntryResult`.
Nothing breaks in osapi-orchestrator until somebody bumps the pin, and then
`pkg/orchestrator/ops.go` breaks for every migrated behavior. Each migration
lands with an orchestrator change beside it.

**The certificate domain does not follow the naming.** It serves `/api/node/...`
but dispatches under its own category, and docker's operations are named like
`docker.create.execute`. They migrate last, and the migration fixes their names.

## Not covered here

The UI. Its domain blocks in `ui/src/components/domain/` stay hand-written.
Forms built from the JSON Schema are possible afterwards and are not part of
this plan.

Workflows. osapi-orchestrator already composes operations across hosts, and its
101 step functions in `ops.go` could become one generic step over the registry.
That is its own change, in its own repository, after this one.

An MCP server. The registry makes one cheap to write, but CLI help and
`describe` are enough for an agent, and a second interface is a second thing to
keep consistent.
