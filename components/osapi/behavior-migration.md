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

Built: `behavior.Requires` and `behavior.Internal`, proven by sysctl requiring
the internal `managedfile` behavior.
[Behaviors](behaviors.md#behaviors-built-on-other-behaviors) describes them.
What remains is moving the other domains whose providers depend on each other,
such as cron on the file provider, onto requirements as each migrates.

## What the platform owns

Everything that is the same for every behavior is written once, in
`internal/behavior`, and a behavior author never sees it:

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

This is the answer to "how does somebody adding a behavior know what the spec
should be". They don't write it. The conventions in that table are the ones a
new contributor gets wrong, and they stop being the contributor's job.

## What the cutover changes

Built so far, and described in [behaviors](behaviors.md): a generated handler
per method with its HTTP tests, the generic agent processor, generated commands,
the generated spec and docs pages, all served beside the hand-written domain
under `/api/next` and `osapi client next`. While both exist, the domain has a
row in the [parity test](behaviors.md#served-beside-the-hand-written-domains)
holding the generated spec to the hand-written one. A domain's cutover, step 4
below for sysctl, deletes that row and makes the behavior the only path.

sysctl's row went before its cutover. Trying the branch on real hosts showed its
reads were wrong: `list` and `get` reported only the parameters osapi wrote, so
a fresh host listed nothing and `get` answered 404 for a key the kernel has.
Ansible, Salt and Puppet all read the host as it is. So `list` now reads every
parameter under `/proc/sys`, with an optional `prefix`, `get` reads any key, and
each entry says whether osapi manages it; `update` sets and manages a parameter
whether or not osapi managed it before. The API then differs from the
hand-written one on purpose, and a parity row holding it to the old one had to
go. The cutover changes:

- **API.** Its routes move from `/api/next` to `/api`, and its hand-written
  handler under `internal/controller/api/node/` and its oapi-codegen server code
  are deleted.
- **CLI.** Its generated commands move from `client next` to `client`, and its
  hand-written `cmd/client_node_*` files are deleted.
- **Agent.** Its hand-written processor is deleted. Its provider already lives
  in the behavior's directory, as `<platform>.go` with its tests moved
  unchanged, since sysctl showed the move is safest done before the cutover; the
  platform files the behavior does not declare, `darwin.go` and `linux.go` for
  sysctl, are deleted with the processor that built them.
- **SDK.** The routes and operationIds are the hand-written ones, so the client
  oapi-codegen generates from the joined spec keeps its methods, and
  `client.Sysctl` keeps working over it. Its entries gain `managed`, and its
  list takes a `prefix`. Generating those typed services from the spec is a
  later step.
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

Built since: the build-a-behavior skill, in the osapi repository's
`.claude/skills/`, and the `osapi behavior new` command behind it. This plan
said the skill would have no scaffold command and would carry templates in its
references for the agent to copy. Building it showed the templates would be a
second copy of the layout, kept in step with the code by hand, so the layout is
now written once, as the command's templates, which a test runs end to end: the
written behavior must build, validate and pass every test. The skill routes to
the command, to `go doc ./internal/behavior`, and to `behavior get` and
`validate`. See [behaviors](behaviors.md#inspecting-behaviors-from-the-cli).

Not built yet:

Built since: evals for the skill, in its `evals/`, each a request run in a fresh
session and checked with commands. They cover a served behavior, one that runs a
program with sudo and declares refusals, an internal behavior another requires,
a behavior for one platform, a secret input, a behavior nested under a group, a
request the platform cannot express, where passing means the skill saying so,
and a request too vague to build from, where passing means it asks. The first
run of the internal behavior's eval found that the fake host could not model
state a program keeps, which `PrintsAfter` now does; building the grouped one
found that `osapi behavior new` could not write a behavior under its group,
which `--group` now does.

Next:

4. The cutover, after the behavior work merges: remove sysctl's `behavior.Next`
   and follow the checks that fail. Its routes and commands move to `/api` and
   `client`, its spec joins the main one, and its hand-written handler,
   processor and command files are deleted. Its provider has already moved into
   `internal/behaviors/sysctl`, and its parity row has already gone. Pass
   criteria 2 to 4 above.
5. `Requires` and `Internal`, which are built.
6. Evals for the build-a-behavior skill, which are built.
7. The test of the whole idea. In a fresh session, an agent is asked to build a
   new behavior with only that skill and the CLI. Where it gets stuck, the skill
   or the CLI is fixed, not the agent's output, and it is run again until it
   builds one unaided.
8. The remaining domains, one per pull request.
   - Generate the SDK's typed services from the joined spec, once every
     behavior's part has joined it, so the SDK is built entirely from the spec
     and never imports a behavior.
9. `provider` is retired as a term, [providers](providers.md) and
   [building a domain](domains.md) are rewritten for behaviors, and this page is
   deleted once nothing in it is still a plan.

The README took its shape from swamp's when sysctl was built from its
definition: a claim, why it is better, getting started with `osapi init`, the
requests to try, and the core concepts. Behaviors are a core concept there,
named as served under `next` until the cutover. Every line describes something
osapi does, and nothing else.

## What blocks the other domains

25 of the 94 hand-written node operations use something a behavior cannot
express yet. Each is a platform change, designed here before it is built, and
each unblocks a set of domains:

| Missing                                                       | Operations                                                                                                                                                | Blocks                                            |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Action methods, a write named for what it does under the item | service start, stop, restart, enable, disable; docker start, stop, exec, pull; process signal; power reboot, shutdown; user password; command exec, shell | service, container, process, power, command, user |
| The `execute` and `shell` permissions beside read and write   | command exec and shell, power, process signal, docker exec                                                                                                | command, power, process, container                |
| A resource under another, with two keys in the path           | a user's SSH keys, a container's images                                                                                                                   | user, container                                   |
| A step on the controller before the job is queued             | a password hashed so the plaintext never reaches NATS                                                                                                     | user                                              |
| The object store on `host.Host`                               | cron and file deploys of uploaded content                                                                                                                 | schedule, file                                    |

`GET /api/node/{hostname}`, the node's status summary, has no behavior shape and
stays hand-written. The rest fit today: hostname, timezone, NTP, disk, load,
memory, OS, uptime, log, package, certificate, DNS, interface, route and ping.
The build-a-behavior skill's "Not yet" list is this table, so an agent asked for
one of these says so rather than wiring around the platform.

A domain's hand-written handler tests are deleted at its cutover, so every case
in them has to land somewhere first: in the behavior's generated HTTP tests,
which cover the cases every method has, or as an example or refusal on the
method, which covers the ones particular to the domain. A domain is not cut over
while a hand-written case has neither. Its provider tests move with the provider
and are not deleted.

## Internal behaviors the migration extracts

Shared work becomes an internal behavior at its second use, the rule of two: one
domain doing something is that domain's code, and a second that needs the same
thing is when it becomes a behavior both require, rather than a copy.
`managedfile` is the first, taken out of sysctl because every domain that owns
files on a host needs what it does. The candidates, each with more than one
domain doing it today:

- **Package install and removal**, done by the package domain and needed by any
  behavior that installs what it manages.
- **Service control**, reload or restart after a change, done by service and
  repeated in NTP, hostname and cron.
- **File deploy from the object store**, done by the file domain and cron, once
  the object store is on `host.Host`.
- **Running a command and reading its output**, which every provider does
  through `h.Exec` today; it becomes a behavior only if it gains checks every
  caller needs, such as refusing input that would reach a shell.

Chaining across hosts or across steps is a workflow, osapi-orchestrator's job,
and not a requirement.

## What will surprise somebody

**The spec stops being the source.** A contributor who edits the generated spec
by hand has their change overwritten by the next `just generate`. The file stays
committed so the diff is reviewable. `just behavior-gen-check`, which
`just test` runs, regenerates and fails on any difference.

**Not everything fits the template.** File upload, `docker exec` and command
execution stream or take multipart bodies. The generated handlers cover a
request that has one typed input and a per-host typed output. A behavior that
needs more keeps a hand-written handler for that one method, and the definition
says so explicitly rather than by omission. That handler registers its own route
beside the generated ones.

**Path parameters lose their validation tags in strict-server generation.** That
is why `node/sysctl/validate.go` restates `required,min=1,sysctl_key` today. A
behavior's generated decoder validates the input type after the path is bound,
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

Behaviors from outside osapi. Every behavior is a package under `internal/`,
registered by a line in `internal/behaviors/all`, so an outside author's
behavior is a pull request here. A behavior from another module compiled into a
custom build, the way swamp extensions are published, would need a public
extension API designed for it, not today's internals made public. That is a
decision of its own, not made here.

An MCP server. The registry makes one cheap to write, but CLI help and
`behavior get` are enough for an agent, and a second interface is a second thing
to keep consistent.
