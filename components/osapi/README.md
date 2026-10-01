# osapi

osapi manages Linux hosts over a message bus, so a host can be configured
through an interface rather than by logging in and editing files. Almost every
constraint below comes from wanting that across a fleet rather than one box.

Two things ship together: a **controller** exposing a REST API, and an **agent**
running on each managed host. `cmd/` holds both entry points and `main.go`
dispatches between them.

**Work reaches a host by being queued, not by being called.** The controller
does not run anything itself. A request becomes a job, an agent picks it up, and
a provider does the work on the machine. At-least-once delivery, the idempotency
providers owe, two independent timeouts and a per-host result all come out of
that.

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

Three kinds of consumer: an operator through the CLI, a program through the Go
SDK at `pkg/sdk/client`, and
[osapi-orchestrator](../osapi-orchestrator/README.md) through that same SDK.

## The six layers

Each does one thing, and the boundary is what keeps a domain's code from
spreading.

| Layer           | Does                                         | Lives in                   |
| --------------- | -------------------------------------------- | -------------------------- |
| CLI             | parses flags, prints results                 | `cmd/`                     |
| REST API        | validates input, delegates to the job client | `internal/controller/api/` |
| Job system      | carries work to a host and answers back      | `internal/job/`            |
| Provider        | does the work, on the agent                  | `internal/provider/`       |
| Agent lifecycle | registers providers, dispatches to them      | `internal/agent/`          |
| Configuration   | resolved once, at startup                    | `internal/config/`         |

A handler validates and delegates. It never touches the operating system.

## Read about it

| Subject                             | What it answers                                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [The message bus](transport.md)     | What NATS carries, how it is namespaced, and the three things osapi cannot control                                  |
| [The job system](job-system.md)     | How work reaches a host, what is guaranteed, the three limits, the four statuses, and one request traced end to end |
| [Providers](providers.md)           | How work gets done on the machine, the idempotency rule, the four patterns                                          |
| [Agent identity](agent-identity.md) | Enrollment, signing, rotation, and why targeting needs verification                                                 |
| [Building a domain](domains.md)     | What a new endpoint touches, in what order, and what is forced by tooling                                           |
| [The embedded UI](ui.md)            | The dashboard compiled into the binary, and what it does not verify                                                 |
| [The Go SDK](sdk.md)                | What a service owes, the five naming rules, and the seven methods that break them                                   |
| [Running commands](exec.md)         | The five ways to run one, why ten minutes is a ceiling, and where a secret goes                                     |
| [Permissions](permissions.md)       | The 37 permissions, the three roles, and why a direct permission overrides them                                     |
| [The audit trail](audit.md)         | What is recorded, why redaction is a denylist, and what a read does not capture                                     |
| [Configuration](configuration.md)   | Where a value comes from, and how secrets stay out of the log                                                       |
| [Observability](observability.md)   | Tracing across the queue, metrics on their own port, conditions                                                     |

## Where it sits

It imports [nats-client](../nats-client/README.md) for the client side of the
bus and [nats-server](../nats-server/README.md) for the embedded server.
[osapi-orchestrator](../osapi-orchestrator/README.md) imports osapi.

A change to either NATS repository can break osapi's transport. A change to
osapi's SDK surface breaks the orchestrator, but the orchestrator pins a commit
rather than a tag, so nothing breaks there until somebody bumps it. Land a
rename and its bump together.

Its build fetches [osapi-justfiles](../osapi-justfiles/README.md) through a
justfile recipe, from `main`. That edge is in no `go.mod`.

The organization-wide picture is [system's architecture](../../ARCHITECTURE.md).

## How big it is

24 API domains over 6 provider categories, and 1,814 non-test Go files.

```sh
ls -d internal/provider/*/ | wc -l    # 6
```

## Known limitations

**`sdk/guidelines.md` is still partly contributor knowledge on an operator's
site.** Its rules are stated here and the page demonstrates them with worked
examples, which is fine. What it holds beyond demonstration, the package
structure and the response pattern, has no counterpart here and no feature open
for it.

**The orchestrator pins a commit, not a tag.** A rename here lands green and
breaks there at the bump.

**The `osapi-justfiles` fetch is unpinned.** Nothing records which version of a
shared recipe a build used.

## Not covered here

How any individual provider or domain works. There are 24 domains and 6 provider
categories, and the contract they share is in the subject documents above.

The CLI's full command surface, which is 143 pages of reference under
`usage/cli` where an operator should read it.

osapi's testing conventions, which are its own `CONTRIBUTING.md`'s.

______________________________________________________________________

Written from the osapi repository.
