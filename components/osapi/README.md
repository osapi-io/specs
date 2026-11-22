# osapi

osapi manages Linux hosts over a message bus. Thus you can configure a host
through an interface. You do not log in and edit files. Almost each constraint
below comes from the need to do this on a fleet, not on one machine.

osapi ships two parts together: a **controller** with a REST API, and an
**agent** on each managed host. `cmd/` has the two entry points, and `main.go`
selects between them.

**osapi queues work for a host. It does not call the host.** The controller runs
nothing itself. A request becomes a job. An agent takes the job, and a provider
does the work on the machine. These properties come from that decision:

- at-least-once delivery
- the idempotency that each provider must have
- two independent timeouts
- a result for each host

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

There are three kinds of consumer:

- an operator, through the CLI
- a program, through the Go SDK at `pkg/sdk/client`
- [osapi-orchestrator](../osapi-orchestrator/README.md), through the same SDK

## The six layers

Each layer does one thing. The boundaries keep the code of a domain in its
layers.

| Layer           | Does                                         | Lives in                   |
| --------------- | -------------------------------------------- | -------------------------- |
| CLI             | parses flags, prints results                 | `cmd/`                     |
| REST API        | validates input, delegates to the job client | `internal/controller/api/` |
| Job system      | carries work to a host and answers back      | `internal/job/`            |
| Provider        | does the work, on the agent                  | `internal/provider/`       |
| Agent lifecycle | registers providers, dispatches to them      | `internal/agent/`          |
| Configuration   | resolved once, at startup                    | `internal/config/`         |

A handler validates and gives the work to the job client. It never touches the
operating system.

## Read about it

| Subject                                              | What it answers                                                                                                                                                     |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [The message bus](transport.md)                      | What NATS carries, its namespaces, and the three things that osapi cannot control                                                                                   |
| [The job system](job-system.md)                      | How work gets to a host, what is guaranteed, the three limits, the four statuses, and one request from start to end                                                 |
| [Providers](providers.md)                            | How the work occurs on the machine, the idempotency rule, the four patterns                                                                                         |
| [Behaviors](behaviors.md)                            | A typed definition that the routes, permissions, CLI commands and schemas come from, and the rules that `behavior validate` checks                                  |
| [Agent skills](agent-skills.md)                      | The skill in the binary, what it tells an agent, and how `osapi init` installs and updates it                                                                       |
| [Admission](admission.md)                            | Which machines can join, the four states, and why admit needs the fingerprint from the machine                                                                      |
| [Agent identity](agent-identity.md)                  | Enrollment, signatures, rotation, and why targeting needs verification                                                                                              |
| [Building a domain](domains.md)                      | What a new endpoint changes, in what order, and what the tools force                                                                                                |
| [The embedded UI](ui.md)                             | The dashboard in the binary, and what it does not verify                                                                                                            |
| [The Go SDK](sdk.md)                                 | What a service must do, the five naming rules, and the seven methods that break them                                                                                |
| [The API conventions](api.md)                        | Status codes, the error body, the shape of a list, names, and the test that holds each operation to them                                                            |
| [The docs site](docs-site.md)                        | What the sections of the docs site hold, and which pages are generated from the binary: each reference page is the output of a command                              |
| [The CLI](cli.md)                                    | A thin shell over the SDK: one command per endpoint, two inherited flags, command and flag names, shared renderers, and the output style                            |
| [Running commands](exec.md)                          | The five ways to run a command, why ten minutes is a maximum, and where a secret goes                                                                               |
| [Permissions](permissions.md)                        | The 37 permissions, the three roles, and why a direct permission replaces them                                                                                      |
| [The audit trail](audit.md)                          | What osapi records, why redaction is a denylist, and what a read does not record                                                                                    |
| [Configuration](configuration.md)                    | Where a value comes from, and how secrets stay out of the log                                                                                                       |
| [Observability](observability.md)                    | Tracing across the queue, metrics on their own port, conditions                                                                                                     |
| [Moving domains to behaviors](behavior-migration.md) | Which domains are behaviors now, what is built, and the steps that remain: the cutover, chains, the skill, the other domains                                        |
| [Endpoints](endpoints.md)                            | The controller's own operations defined in Go, the spec and CLI generated from them, and the tests that hold them to the hand-written spec; the first step is built |
| [Commands](commands.md)                              | A plan: each command of the binary from a definition, in the layer that endpoints and behaviors embed, with its own spec and validate                               |
| [The parts of a DSL](dsls.md)                        | What each DSL shares: spec, checks, typed values, tag keys, permissions, generation, docs and skill, and the tests that hold them                                   |
| [Least privilege](least-privilege.md)                | A plan: the agent as a user that is not root, privileged steps that a behavior declares, and the sudoers and systemd files made from them                           |
| [Workflows](workflows.md)                            | A proposal: named, ordered behavior calls in a file, checked against the registry, and run again with the same result                                               |

## Where it sits

It imports [nats-client](../nats-client/README.md) for the client side of the
bus, and [nats-server](../nats-server/README.md) for the embedded server.
[osapi-orchestrator](../osapi-orchestrator/README.md) imports osapi.

A change to either NATS repository can break the transport of osapi. A change to
the SDK API of osapi breaks the orchestrator. But the orchestrator pins a
released tag, so it does not break until somebody updates the pin. Merge a
rename and its pin update together.

Its build gets [osapi-justfiles](../osapi-justfiles/README.md) through a
justfile recipe, from `main`. No `go.mod` shows that connection.

[The architecture of the system](../../ARCHITECTURE.md) shows the full
organization.

## How big it is

There are 24 API domains in 6 provider categories, and 1,814 Go files that are
not tests.

## Known limitations

**`sdk/guidelines.md` still has some contributor knowledge on a site for
operators.** This page states its rules, and that page shows them with examples.
That is correct. But it also has the package structure and the response pattern.
This page has no copy of them, and no feature is open for them.

**The orchestrator pins a tag of osapi.** A rename here passes, and breaks the
orchestrator at the next pin update.

**The `osapi-justfiles` fetch has no pin.** Nothing records which version of a
shared recipe a build used.

## Not covered here

How one provider or domain works. There are 24 domains and 6 provider
categories. The subject documents above have the contract that they share.

The full command set of the CLI. osapi generates one reference page for each
command under `usage/cli`, from the commands, where an operator reads them.

The test conventions of osapi. They are in its own `CONTRIBUTING.md`.

______________________________________________________________________

Written from the osapi repository.
