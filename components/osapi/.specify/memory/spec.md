# osapi

osapi manages Linux hosts over a message bus. Two things ship together: a
**controller** exposing a REST API, and an **agent** running on each managed
host. `cmd/` holds both entry points and `main.go` dispatches between them.

**Work reaches a host by being queued, not by being called.** That single fact
explains the rest of the design. The API cannot do the work itself, because the
work happens on the agent, so a request becomes a job, a job becomes a
notification, and an agent picks it up and runs a provider.

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

Three kinds of consumer: an operator through the CLI, a program through the Go
SDK at `pkg/sdk/client`, and `osapi-orchestrator` through that same SDK. Most of
the published documentation site serves the first.

## Where it sits

It imports `nats-client` and `nats-server`. `osapi-orchestrator` imports it.

A change to either NATS repository can break osapi's transport. A change to
osapi's SDK surface breaks the orchestrator, but the orchestrator pins a commit
rather than a tag, so nothing breaks there until somebody bumps it. Land a rename
and its bump together.

It also depends on `osapi-justfiles` for its build, through a justfile recipe
that fetches from `main`. That edge is in no `go.mod`, so a reader who checked
only the module graph would miss it.

## The six layers

Each does one thing, and the boundary between them is what keeps a domain's code
from spreading.

| Layer               | Does                                        | Lives in                      |
| ------------------- | ------------------------------------------- | ----------------------------- |
| CLI                 | parses flags, prints results                | `cmd/`                        |
| REST API            | validates input, delegates to the job client | `internal/controller/api/`    |
| Job system          | carries work to a host and answers back     | `internal/job/`               |
| Provider            | does the work, on the agent                 | `internal/provider/`          |
| Agent lifecycle     | registers providers, dispatches to them     | `internal/agent/`             |
| Configuration       | resolved once, at startup                   | `internal/config/`            |

A handler validates and delegates. It never touches the operating system.

## The job system

### A job is stored before it is announced

The definition is written to `jobs.{job-id}` first, then a notification goes out.
The notification carries the job's **identity**, not its content, so a consumer
fetches the definition rather than trusting what arrived on the wire.

Status is recorded as **append-only events** under `{status}.{uuid}` rather than
by mutating one field, so the history of a job survives it. Results go to a
separate bucket, `job-responses`, keyed by the job they answer.

### Subjects and targets

Operations route by dot-notation subject under one of two prefixes, `jobs.modify`
for anything that changes a host and `jobs.query` for anything that does not. The
prefix is **namespaced rather than literal**, so a stated subject is a shape and
a deployment may sit under its own root.

A target resolves four ways: a hostname, a machine ID, a broadcast, or a label
selector. `internal/job/subjects.go` has one implementation of that parsing and a
domain must not write a second.

### Delivery is at-least-once, so the agent owes idempotency

The bus will deliver the same unit of work twice. Nothing in the transport
prevents it, so **the obligation lands on the provider**: running an operation a
second time must be harmless.

Four operations cannot honour that, and the specification names them rather than
pretending otherwise: `command.exec`, `command.shell`, `power.reboot` and
`power.shutdown`. For those, the agent treats a job that has already run as
**terminal** and refuses to run it again.

### Two clocks, bounding different things

`AckWait` bounds how long the bus waits for an acknowledgement.
`DefaultCommandTimeout` bounds how long an operation may run. An operation
outliving `AckWait` is not a failure of the operation.

An operator reading "timed out" will otherwise conclude the work did not happen.
It may well have. Cancelling the originating API request does not cancel the job,
because the job is already queued and the agent is already holding it.

### What a caller gets back

A per-host result carries one of four statuses: `ok`, `failed`, `skipped`, or
`timeout`. A failure carries a machine-readable cause alongside its message, so a
caller branches on the cause rather than on prose.

The KV buckets carry TTLs per bucket rather than per status: `job-queue` for
definitions and status events, `job-responses` for results, `agent-facts` for
what an agent gathers on its own schedule.

## Providers

A provider is the operations layer. It runs **in the agent process**, receives
its parameters from the job, and does the work.

A mutation result carries whether anything actually changed. That is what makes
`OnlyIfChanged` possible for a caller, and it is why creating a resource that
already exists is a success with `changed: false` rather than an error.

An operation unsupported on the host's OS family returns the shared **unsupported
outcome**, which is distinct from a failure and from no change. "Not available
here" and "broken" are different answers and a caller can tell them apart.

Platform-specific providers are selected by OS family. Facts reach a provider by
injection, walking the registered providers, so a provider constructed but never
registered has no facts and fails when called rather than at startup.

Three rules about the boundary, each of which was got wrong somewhere first:

**Validation on the request path does not substitute for the provider's own.** A
value stored before a rule existed still reaches the provider.

**A secret never reaches a command through its arguments**, because arguments are
visible in the process table.

**A file a provider writes is not written in place.** A partially written
configuration file is worse than none.

## Agent identity

An accepted agent's public key is retained beyond the enrollment handshake, and
it is recorded **only** as part of accepting an enrollment. Nothing else creates
or replaces it, so the arrival of a message signed with a different key changes
nothing.

The controller verifies a job response against the key recorded at acceptance.
The agent signs what it registers, and the controller verifies that too, so a
second machine publishing the same hostname cannot claim work addressed to the
first. Targeting resolves only verified registrations.

Rotation keeps the previous key accepted for a grace period, so keys change
without an outage. Removal is immediate.

## Building a domain

A domain is a coherent area of system behaviour exposed as API endpoints. It is
complete when it appears everywhere an existing domain appears, which makes the
check mechanical: pick `sysctl` or `cron`, grep the codebase for it, and anything
that exists for it and not for yours is missing.

Some of the build order is forced by code generation rather than convention. The
OpenAPI specification precedes generation because generation reads it. Generation
precedes the handler because the handler implements a generated interface. The
**combined** specification at `internal/controller/api/gen/api.yaml`, which
`redocly join` assembles from every domain's own `gen/api.yaml`, precedes the SDK
client, because the SDK generates from the combined file. **A domain absent from
the combined file is invisible to the SDK however complete its own spec is.**

The specification is the source of truth for input validation, and a tag goes in
three places and does nothing in a fourth: on request body properties, at
parameter level for query parameters rather than inside `schema:`, as
`format: uuid` for UUID path parameters, and **not** on path parameters in
strict-server mode, where oapi-codegen generates no tags at all.

Create and update get separate verbs. A combined upsert is forbidden, because a
caller cannot then say which one they meant.

`{hostname}` accepts a literal, `_any`, `_all`, or a label selector. Broadcast
support is mandatory, and both the single-target and broadcast paths return the
same collection shape, so a caller writes one parser.

## The embedded UI

osapi ships a React single-page application compiled into the controller binary
and served from the REST API's port, so enabling it adds no network
configuration. `controller.ui.enabled: false` turns it off, defaulting to true;
when off the controller skips registering the SPA handler.

Its API client is **generated from the same OpenAPI specification as the Go
SDK**, so an endpoint added to a domain reaches both. A fetch mutator adapts it
for the browser.

Four kinds of component, separated by what each one knows. A primitive knows no
osapi resource. A domain component knows exactly one. Layout knows none and holds
the page's chrome. A hook holds state or fetches data and renders nothing, which
is enforced by every file in `ui/src/hooks/` being `.ts` rather than `.tsx`. A
new file goes where its knowledge puts it.

**The UI decodes its JWT without verifying it.** Verification is the server's
job. A contributor who read only the client would take the decode for a check.

`/ui/` is excluded from the coverage gate by `.coverignore`, so osapi's coverage
figure says nothing about the UI.

## Where knowledge lives

Two audiences, split by who is served rather than by where a file sits. The
corpus under `components/osapi/specs/` states how osapi is **built**, for a
contributor or an agent. The published site under `docs/docs/sidebar/` states how
to **use** it, for an operator.

A rule lives in one of them and is cited from the other, never stated twice. A
citation is a relative markdown link naming a requirement, and `just skill-lint`
fails when one stops resolving, which is what makes the one-statement rule
enforceable rather than aspirational.

The site does not send an operator to the corpus. A contributor page may cite it,
and three do; an operator page answering with "see the specifications repository"
has lost its reader.

## What was measured

At `0cca62060`, 2026-09-29, reproduced unchanged 2026-09-30.

| Measurement              | Value | Command                                                                                                                   |
| ------------------------ | ----: | ------------------------------------------------------------------------------------------------------------------------- |
| Go files                 | 2,739 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                      |
| Go files excluding tests | 1,814 | `find . -name '*.go' -not -path './.git/*' -not -name '*_test.go' \| wc -l`                                               |
| Site pages               |   219 | `find docs/docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                      |
| Files under `docs/`      |   221 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                           |
| Provider categories      |     6 | `ls -d internal/provider/*/ \| wc -l`                                                                                     |
| API domains              |    24 | `ls -d internal/controller/api/node/*/ internal/controller/api/*/ \| grep -vE '/(gen\|mocks\|common\|apierr)/$' \| wc -l` |

**219 and 221 are different quantities.** 219 are published pages under
`docs/docs/`. 221 adds `docs/README.md` and `docs/SUPPORT.md`, which belong to the
Docusaurus project rather than to the site. Both are right about different
questions, and a reader given only one concludes the other is broken.

The SDK exposes 117 methods, counted with
`grep -cE '^func \(s \*[A-Za-z]+Service\)' pkg/sdk/client/*.go` summed across the
files. It is not in the table above because the command needs a sum across a glob
and the per-file counts are what `grep -c` returns.

## Known limitations

**`sdk/guidelines.md` is still partly contributor knowledge on an operator's
site.** Its rules are stated in the corpus and the page demonstrates them with
worked examples, which is fine. What it holds beyond demonstration, the package
structure and the response pattern, has no corpus counterpart and no feature
open for it.

**The orchestrator pins a commit, not a tag.** A rename here lands green and
breaks there at the bump.

**The `osapi-justfiles` fetch is unpinned.** Nothing records which version of a
shared recipe a build used.

## Not covered here

How any individual provider or domain works. There are 24 domains and 6 provider
categories, and the contract they share is stated above.

The CLI's full command surface, which is 143 pages of reference under
`usage/cli` where an operator should read it.

The UI's internals beyond the component boundary.

osapi's testing conventions, which are its own `CONTRIBUTING.md`'s.

______________________________________________________________________

Traced to the seven features archived under `specs/`: the provider contract, the
agent key store, the corpus backfill, the job system, building a domain, the
baseline that first said what this repository is, and the embedded UI.
