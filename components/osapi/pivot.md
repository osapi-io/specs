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
tests. It is what a provider is today, plus the declaration that the rest of the
system is generated from.

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
`pkg/behavior` and the generator, and a behavior author never sees it:

| Convention                                        | Today                             | After                           |
| ------------------------------------------------- | --------------------------------- | ------------------------------- |
| The `{job_id, results[]}` envelope                | Restated in every spec            | Generator template              |
| Per-host `hostname`, `status`, `error`, `changed` | Restated in every spec            | Generator template              |
| 400, 401, 403, 404 and 500 with `ErrorResponse`   | Listed per operation              | Generator template              |
| `{hostname}` and broadcast targets                | A branch in each handler          | One generic handler             |
| Status mapping, including `skipped` and `timeout` | A switch in each handler          | One generic handler             |
| The job payload                                   | A map in, an anonymous struct out | The behavior's input type       |
| Dispatch on the agent                             | Three levels of string switch     | A lookup by behavior and method |
| Permission strings                                | Spec, SDK, UI, three docs pages   | Derived from `Read`/`Write`     |

This is the answer to "how does somebody adding a behavior know what the spec
should be". They don't write it. The conventions in that table are the ones a
new contributor gets wrong, and they stop being the contributor's job.

## The generators stay

osapi remains spec-driven. What changes is where the spec comes from.

```
behavior definition ──osapi gen──▶ node/{behavior}/gen/api.yaml ──oapi-codegen──▶ server and client, as today
                     └────────────▶ handler adapter, agent registration, SDK methods, CLI commands
```

`osapi gen` reads the registered behaviors and writes each one's `gen/api.yaml`
by filling the templates above with that behavior's types. The types' JSON
Schema comes from their Go struct tags. From there, `redocly join`,
oapi-codegen, the combined spec, the SDK client and the docs site build exactly
as they do now. Generated files are committed, as they are today, so a reviewer
sees the spec change in the diff.

The same pass writes the Go that is hand-written today:

- A handler adapter implementing the generated strict-server interface by
  calling the generic handler.
- The agent's registration of the behavior.
- Typed SDK methods that return the behavior's own types, so there are no SDK
  result types left to copy into.
- The `osapi client node sysctl ...` commands, with flags from the input type's
  tags and table columns from the output type's fields.

## Discovery for agents

Three commands, following the pattern agent-operated CLIs have settled on:

- **`osapi init [--tool claude|codex|cursor]`** writes osapi's skills into the
  repository, from copies embedded in the binary with `go:embed`. Running it
  again after an upgrade rewrites them, so the skill always matches the binary
  on the path.
- **`osapi help <command> --json`** prints the cobra command tree as JSON: the
  flags, which ones are required, the exit codes and the error codes. The skill
  tells the agent to run it before running a command, rather than guess flags.
  This needs nothing from the rest of the pivot.
- **`osapi behavior describe <name> [<method>]`** prints a behavior's methods
  and each method's input and output fields, rendered with the CLI's existing
  table output. With `--json` it prints the JSON Schema. `osapi behavior list`
  lists the behaviors on the binary.

The skill stays small. It is a routing table and four rules: run `help` before a
command, run `describe` before building a request, use `--json` and match errors
on `code`, and read the target before anything destructive. The detail is in
`references/` files that load only when a request needs them. The docs site is
not copied in, because every session would pay for it in context.

Errors under `--json` become one document on stderr, `{"error", "code"}`, with
the codes listed in each command's `help`. Today 119 of the 120 client commands
print the raw API body, and errors are only text.

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

**The CLI gets one style, taken from the logo.** osapi's other output already
uses lipgloss, but help is cobra's default and errors are slog lines. The style
follows the theme package the owner's other Go CLIs share
(`internal/cli/theme.go` in kvlt, meshx, jot, grind, tlock and agentpack):

- The root help opens with the README logo from `asset/logo-dark.svg`, drawn as
  colored half blocks: its 17 by 4 grid of cells becomes two terminal lines.
- Section headings take colors from the logo's palette: cyan `#00d5ff`, magenta
  `#ff00ff`, green `#45ae17`, yellow `#ffd100`, and blue `#2300fd` lightened to
  read on a dark terminal. Each run starts at a random point in the palette.
  Command and flag names take a second color, and secondary text takes the
  logo's gray `#8a8a8a`.
- Errors print as a red `✗` line with a muted `Run 'osapi <cmd> --help'` hint
  for usage and flag errors. API errors show the status code and message.
- The status colors in tables keep their meaning: green for ok, red for an
  error, matching the web UI.
- `NO_COLOR` and output that is not a terminal get plain text with the same
  structure as cobra's default help. Under `--json` the output is unchanged,
  until the error document below replaces it.

The style comes first because every command added after it, `behavior describe`
included, renders through the same helpers and needs no styling of its own.

## The first behavior is sysctl

sysctl has five methods covering both reads and writes, three platform files
(`debian.go`, `darwin.go`, `linux.go`), and an integration test in
`test/integration/sysctl_test.go`. It is complete enough to exercise every
convention in the table and small enough that the generated output can be read
line by line.

The migration is done when:

1. The generated `internal/controller/api/node/sysctl/gen/api.yaml` produces the
   same combined spec as today. The diff of
   `internal/controller/api/gen/api.yaml` before and after is empty, apart from
   descriptions that came from `doc` tags.
2. The existing sysctl integration tests pass unmodified.
3. `osapi behavior describe sysctl` prints the five methods.
4. The files a new sysctl method would touch are counted. If the answer is not
   the behavior directory and nothing else, the platform is missing something.

The old provider path and the new behavior path run side by side, because the
agent's top-level `Registry.Dispatch` already looks up by category and takes no
edits. Domains move one at a time.

## The order of work

1. The CLI cleanup: `osapi job` removed in its own pull request, then the logo
   theme for help and errors.
2. `osapi help --json`, `osapi init` and the skill. These need nothing else and
   make the agent story real first.
3. `pkg/behavior`: `Define`, `Read`, `Write`, the registry and JSON Schema from
   tags, plus a CI check that `just generate` leaves no diff.
4. sysctl moves to `pkg/behavior/sysctl`, with the spec generator. Pass
   criterion 1 above.
5. The generic handler and the agent registration, for sysctl. Criterion 2.
6. Generated SDK methods and CLI commands, for sysctl. Criteria 3 and 4.
7. The remaining domains, one per pull request.
8. `provider` is retired as a term, and [providers](providers.md) and
   [building a domain](domains.md) are rewritten for behaviors.

The README changes when step 2 lands, because `init` is its first claim:

> Typed, repeatable operations for Linux hosts. Built for agents, there to
> empower humans.
>
> Give an agent a fleet of Linux hosts without handing it a shell. Every change
> is a typed operation, checked before it is queued, safe to run twice, and
> recorded.

That is followed by short lines for any harness, typed operations, repeatable,
one host or many, queued not called, four ways in, and see what happened. Every
line describes something osapi does once step 2 ships, and nothing else.

## What will surprise somebody

**The spec stops being the source.** A contributor who edits a behavior's
`gen/api.yaml` by hand has their change overwritten by the next `just generate`.
The file stays committed so the diff is reviewable. Nothing in CI catches a hand
edit today, so step 3 adds a check that runs `just generate` and fails on any
difference.

**Not everything fits the template.** File upload, `docker exec` and command
execution stream or take multipart bodies. The generic handler covers a request
that has one typed input and a per-host typed output. A behavior that needs more
keeps a hand-written handler for that one method, and the definition says so
explicitly rather than by omission.

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
