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

The definition, its placement with `Node` and `Under`, what `Read`, `Write` and
`Key` decide, schemas from tags and custom validators, and the rules
`behavior validate` checks are built and described in [behaviors](behaviors.md).
What follows is the part not built yet.

## Behaviors built on other behaviors

Providers already depend on each other, by constructor argument in
`cmd/agent_setup.go`: cron is built on the file provider, and dns and sysctl on
the file-state KV and the exec manager. Nothing declares those edges, so the
only record of them is the order of the setup code.

A definition declares them instead:

```go
var Behavior = behavior.Register(behavior.Define(
    "cron", "Scheduled jobs under /etc/cron.d",
    behavior.Node,
    behavior.Requires(lineinfile.Behavior, file.Behavior),
    ...
))
```

- **On the agent**, the platform builds a required behavior's provider first and
  hands it to the one that requires it. A method calls the other behavior's
  method as a typed Go call on the same host in the same job, such as
  `lineinfile.Ensure(ctx, p.Lines, lineinfile.Input{...})`, not through the API.
- **`behavior validate`** fails a requirement that is not registered and a
  cycle. `behavior describe` lists what a behavior requires and what requires
  it.
- **`behavior.Internal`** marks a behavior other behaviors use but callers do
  not: it gets no route, no CLI command and no spec. A primitive such as
  lineinfile can start internal and be exposed later by removing the option.

Chaining behaviors across hosts and steps, the output of one method feeding the
input of the next, is a workflow, and stays osapi-orchestrator's job. Typed
inputs and outputs are what make that possible: a step can be checked against
the next one's schema before anything runs. The orchestrator's 101 hand-written
step functions become one generic step over the registry, in that repository,
after this.

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

### How the spec is generated

`osapi gen` runs inside `just generate`. It imports osapi, so every behavior has
registered itself, and for each method it builds the operation from the
definition:

| Part of the spec | Comes from                                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Path             | placement, name and key: `Node` + `sysctl` + `.Key("key")` is `/api/node/{hostname}/sysctl/{key}`                                          |
| HTTP method      | `Read` is `GET`; `Write` is `POST`, `PUT` or `DELETE` by method name                                                                       |
| Security scope   | the top-level group and the verb: `sysctl:read`, `sysctl:write`                                                                            |
| `operationId`    | today's naming rule, such as `GetNodeSysctlByKey`, so clients see no change                                                                |
| Request schema   | the input type's tags: `json` names the field, `validate` gives the constraints, `doc` the description                                     |
| Response schema  | the `{job_id, results[]}` envelope, each result's `hostname`, `status`, `error` and, for a write, `changed`, plus the output type's fields |
| Error responses  | the shared 400, 401, 403, 404 and 500 templates                                                                                            |

It writes one `api.yaml` per behavior, and `redocly join` combines them into
`internal/controller/api/gen/api.yaml` exactly as today.

The standard `validate` tags map straight to JSON Schema: `required`, `min`,
`max`, `len`, `oneof`, `ip`, `cidr`, `url` and the rest. A custom validator such
as `sysctl_key` is a Go function, and nothing can read a schema out of it. So a
custom validator is registered with its schema beside it, once:

```go
validation.Register("sysctl_key", isSysctlKey, jsonschema.Pattern(`^[a-zA-Z0-9][a-zA-Z0-9._-]*$`))
```

That pattern is written by hand in three places today, `debian.go`,
`internal/validation/validation.go` and the sysctl spec. After this it is
written once, and the generator fails on a tag whose validator has no schema,
rather than emitting a spec that validates less than the server does.

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

Today's validation is written in the spec and carried into Go by oapi-codegen:
306 `x-oapi-codegen-extra-tags` entries across the domain specs become
`validate:` struct tags on the generated types. After the pivot the same tags
sit directly on the behavior's input type, written once, and the generated spec
carries them out as JSON Schema constraints. The rule moves closer to the code
that depends on it and stops being restated.

"Here is the API spec" stays true, and gets two checks it does not have today:

- **The spec still describes what the server does.** The integration tests run
  every request and response through a validator built from the generated spec,
  `kin-openapi`'s `openapi3filter`, which is already in the module graph. A
  response that drifts from its schema fails a test. oapi-codegen's strict
  server only proves the Go compiles against the types, not that the bytes on
  the wire match.
- **The spec still works for somebody else's generator.** CI runs oapi-codegen
  on the generated spec into a scratch package and compiles the client. If a
  change produces a spec a generator chokes on, the build says so before a user
  does.

The controller-only endpoints, audit, jobs, agents and health, keep their
hand-written specs and oapi-codegen for now. They are not behaviors, and moving
them onto the same registry is a separate decision once behaviors have proved
out.

The cost is that a route or a command can no longer be found by its file name.
`osapi behavior list`, `osapi help --json` and the generated spec are the index
instead.

## Docs generated from the behavior

The docs site's CLI reference is written by hand today: 166 pages under
`docs/docs/sidebar/usage/cli/`, six for sysctl alone. Each restates the
command's flags, an example invocation, a sample of the table it prints and a
sample of its `--json` body. All of that is already in the behavior definition
or comes out of the CLI's own renderers.

`osapi gen` writes those pages too, one per method, from the same registry:

- **Usage and description** from the method's name, placement and `doc`.
- **The flags table** from the input type's tags: name, type, required, default,
  description.
- **Examples** from examples declared on the method, an input and a sample
  output for each. The sample output is printed by running the real renderer
  over the sample, so the page shows exactly what the CLI prints, in the same
  layout, and cannot drift from it when the theme changes.
- **The `--json` body** from the same sample, marshalled through the envelope.

A page carries the theme's colors through an ANSI-aware `<Terminal>` block in
the docs site rather than a plain code fence, so the docs look like the
terminal.

Pages for the platform's own commands, `start`, `token`, `agent` and the
controller-only `client` commands, stay hand-written until they move onto the
same registry. Generating the SDK reference from behaviors is possible the same
way and is not part of this plan.

## Discovery for agents

Built: [help as JSON](cli.md#help-as-json-for-agents), the
[`--json` error document](cli.md#errors-go-through-one-handler),
[`behavior list`, `describe` and `validate`](behaviors.md#inspecting-behaviors-from-the-cli),
and [`osapi init` with the embedded skill](agent-skills.md).

Not built yet:

- **The building-a-behavior skill**, in the osapi repository's
  `.claude/skills/`, replacing add-a-domain. It has no scaffold command behind
  it. Its references hold the templates, the agent writes the files, and it
  checks its own work in a loop: `go test` for the behavior's package,
  `osapi behavior validate`, `osapi behavior describe <name> --json` to see it
  registered with the right schemas, then a smoke run of each method against
  `osapi start` with `--json`.
- **Evals for both skills**: whether the skill triggers on the requests it
  should, whether it routes to the right reference, and whether that reference
  is enough on its own. They are how a skill gets tuned until an agent can do
  the job with nothing else.
- **`--json` on every client command's success output** is already the API body;
  the gap is commands outside `client`, such as `start` and `token`.

## Cleaning up the CLI first

Done in osapi#665: `osapi job` removed, and one theme for help, output and
errors, recorded in [the CLI's output style](cli.md#output-style).

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

Done:

1. The CLI cleanup, in osapi#665.
2. The behavior core and the agent commands: `pkg/behavior` with `Define`,
   `Node`, `Under`, `Read`, `Write`, `Key`, the registry, JSON Schema from tags
   and `behavior validate`; sysctl's definition; `osapi help --json`,
   `behavior list` and `describe`, the `--json` error document, and `osapi init`
   with the embedded skill. Described in [behaviors](behaviors.md),
   [the CLI](cli.md) and [agent skills](agent-skills.md).

Next:

3. Registration at startup for routes, agent dispatch and CLI commands, with
   `osapi gen` writing the spec and the docs pages. sysctl moves to
   `pkg/behavior/sysctl` and its old handler, processor and command files are
   deleted. Pass criteria 1 to 4 above.
4. `Requires` and `Internal`, from
   [behaviors built on other behaviors](#behaviors-built-on-other-behaviors).
5. The building-a-behavior skill: routing page, templates in its references, the
   check loop, and evals.
6. The test of the whole idea. In a fresh session, an agent is asked to build a
   new behavior with only that skill and the CLI. Where it gets stuck, the skill
   or the CLI is fixed, not the agent's output, and it is run again until it
   builds one unaided.
7. The remaining domains, one per pull request.
8. `provider` is retired as a term, [providers](providers.md) and
   [building a domain](domains.md) are rewritten for behaviors, and this page is
   deleted once nothing in it is still a plan.

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
