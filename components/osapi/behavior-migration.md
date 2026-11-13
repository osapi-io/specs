# Moving domains to behaviors

osapi is moving from providers, where every layer is written by hand for every
domain, to **behaviors**: a behavior author writes typed inputs and outputs and
the logic that changes the host, and osapi generates everything between the
caller and that logic. The REST API, the SDK and the CLI keep their current
shape. What changes is who writes them.

This page tracks that move: what is left to build, the order, and what has to be
true before each step counts as done. What is already built is described in
[behaviors](behaviors.md), and moves there from here as each step lands; the
page is deleted when nothing in it is still a plan. [Providers](providers.md)
and [building a domain](domains.md) describe the domains not yet moved.

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
  cycle. `behavior get` lists what a behavior requires and what requires it.
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

## What the cutover changes

Built so far, and described in [behaviors](behaviors.md): the generic handler,
the generic agent processor, generated commands, the generated spec and docs
pages, all served beside the hand-written domain under `/api/next` and
`osapi client next`. A domain's cutover, step 4 below for sysctl, makes the
behavior the only path:

- **API.** Its routes move from `/api/next` to `/api`, and its hand-written
  handler under `internal/controller/api/node/` and its oapi-codegen server code
  are deleted.
- **CLI.** Its generated commands move from `client next` to `client`, and its
  hand-written `cmd/client_node_*` files are deleted.
- **Agent.** Its hand-written processor is deleted, and its provider's
  implementations move into the behavior's directory as
  `provider_<platform>.go`.
- **SDK.** Callers move to `Client.Behavior` and `client.Rows`, with thin typed
  wrappers where a caller wants `client.Sysctl.Get`. The hand-written result
  types and their converter functions go.
- **Spec.** Its part of the generated spec joins the main one, and its
  hand-written YAML is deleted. What reads the spec keeps working: the UI's
  TypeScript client, the docs site's API pages, and outside clients generated
  from it.

Two checks the spec does not have today come with the first cutover, because
once the spec is generated nothing else holds it to the server:

- **The spec still describes what the server does.** The integration tests run
  every request and response through a validator built from the generated spec,
  `kin-openapi`'s `openapi3filter`, which is already in the module graph.
- **The spec still works for somebody else's generator.** CI runs oapi-codegen
  on the generated spec into a scratch package and compiles the client.

The controller-only endpoints, audit, jobs, agents and health, keep their
hand-written specs and oapi-codegen. They are not behaviors, and moving them is
a separate decision once behaviors have proved out.

## Discovery for agents

Built: [help as JSON](cli.md#help-as-json-for-agents), the
[`--json` error document](cli.md#errors-go-through-one-handler),
[`behavior list`, `get` and `validate`](behaviors.md#inspecting-behaviors-from-the-cli),
and [`osapi init` with the embedded skill](agent-skills.md).

Not built yet:

- **The building-a-behavior skill**, in the osapi repository's
  `.claude/skills/`, replacing add-a-domain. It has no scaffold command behind
  it. Its references hold the templates, the agent writes the files, and it
  checks its own work in a loop: `go test` for the behavior's package,
  `osapi behavior validate`, `osapi behavior get --name <name> --json` to see it
  registered with the right schemas, then a smoke run of each method against
  `osapi start` with `--json`.
- **Evals for both skills**: whether the skill triggers on the requests it
  should, whether it routes to the right reference, and whether that reference
  is enough on its own. They are how a skill gets tuned until an agent can do
  the job with nothing else.
- **`--json` on every client command's success output** is already the API body;
  the gap is commands outside `client`, such as `start` and `token`.

## The first behavior is sysctl

sysctl has five methods covering both reads and writes, three platform files
(`debian.go`, `darwin.go`, `linux.go`), and an integration test in
`test/integration/sysctl_test.go`. It is complete enough to exercise every
convention in the table and small enough that the generated output can be read
line by line.

The migration is done when:

1. The spec generated for sysctl matches today's. The diff of the sysctl paths
   and schemas in `internal/controller/api/gen/api.yaml` before and after is
   empty, apart from descriptions that came from `doc` tags.
2. The existing sysctl integration tests pass unmodified.
3. `osapi behavior get --name sysctl` prints the five methods.
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
   `behavior list` and `get` (first named `describe`), the `--json` error
   document, and `osapi init` with the embedded skill. Described in
   [behaviors](behaviors.md), [the CLI](cli.md) and
   [agent skills](agent-skills.md).
3. sysctl built entirely from its definition, served beside the hand-written
   domain under `/api/next` and `osapi client next`: the generic handler and
   agent processor, generated commands, the generated spec and docs pages,
   telemetry, `API` and `CLI` as opt-in surfaces, and the standard layout.
   Described in [behaviors](behaviors.md). The generated spec matches today's on
   30 of 32 compared fields; the two differences are constraints the server
   already enforced and the old spec omitted.

Next:

4. The cutover: sysctl's routes and commands move to `/api` and `client`, its
   spec joins the main one, its provider moves into `pkg/behavior/sysctl`, and
   its hand-written handler, processor and command files are deleted. Pass
   criteria 2 to 4 above.
5. `Requires` and `Internal`, from
   [behaviors built on other behaviors](#behaviors-built-on-other-behaviors).
6. The building-a-behavior skill: routing page, templates in its references, the
   check loop, and evals.
7. The test of the whole idea. In a fresh session, an agent is asked to build a
   new behavior with only that skill and the CLI. Where it gets stuck, the skill
   or the CLI is fixed, not the agent's output, and it is run again until it
   builds one unaided.
8. The remaining domains, one per pull request.
9. `provider` is retired as a term, [providers](providers.md) and
   [building a domain](domains.md) are rewritten for behaviors, and this page is
   deleted once nothing in it is still a plan.

The README changed when step 2 landed, because `init` is its first claim:

> Typed, repeatable operations for Linux hosts. Built for agents, there to
> empower humans.
>
> Give an agent a fleet of Linux hosts without handing it a shell. Every change
> is a typed operation, checked before it is queued, safe to run twice, and
> recorded.

That is followed by short lines for any harness, typed operations, repeatable,
one host or many, queued not called, four ways in, and see what happened. Every
line describes something osapi does, and nothing else. Behaviors join the README
at the cutover, when they are what a user gets rather than a preview under
`next`.

## What will surprise somebody

**The spec stops being the source.** A contributor who edits the generated spec
by hand has their change overwritten by the next `just generate`. The file stays
committed so the diff is reviewable. `just behavior-gen-check`, which
`just test` runs, regenerates and fails on any difference.

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

Docs for the platform's own commands. `start`, `token`, `agent` and the
controller-only `client` commands keep hand-written pages until they move onto
the same registry. Generating the SDK reference from behaviors is possible the
same way and is not part of this plan.

An MCP server. The registry makes one cheap to write, but CLI help and
`behavior get` are enough for an agent, and a second interface is a second thing
to keep consistent.
