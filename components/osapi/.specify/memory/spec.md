# osapi

osapi manages Linux hosts over a message bus. Two things ship together: a
**controller** exposing a REST API, and an **agent** running on each managed host.
`cmd/` holds both entry points and `main.go` dispatches between them.

**Work reaches a host by being queued, not by being called.** The controller does
not run anything itself. A request becomes a job, an agent picks it up, and a
provider does the work on the machine. Almost everything else about osapi follows
from that.

```
CLI → SDK → REST API → job client → NATS → agent → provider
```

Three kinds of consumer: an operator through the CLI, a program through the Go SDK
at `pkg/sdk/client`, and [osapi-orchestrator](../../../osapi-orchestrator/.specify/memory/spec.md)
through that same SDK.

## Read about it

| Subject                                        | What it answers                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------- |
| [The job system](architecture/job-system.md)   | How work reaches a host, what is guaranteed, the two clocks, the four statuses, and one request traced end to end |
| [Providers](architecture/providers.md)         | How work gets done on the machine, the idempotency rule, the four patterns    |
| [Agent identity](architecture/agent-identity.md) | Enrollment, signing, rotation, and why targeting needs verification         |
| [Building a domain](architecture/domains.md)   | What a new endpoint touches, in what order, and what is forced by tooling     |
| [The embedded UI](architecture/ui.md)          | The dashboard compiled into the binary, and what it does not verify          |
| [The Go SDK](architecture/sdk.md)              | What a service owes, the five naming rules, and the seven methods that break them |
| [Running commands](architecture/exec.md)       | The six ways to run one, why ten minutes is a ceiling, and where a secret goes |
| [Permissions](architecture/permissions.md)     | The 37 permissions, the three roles, and why a direct permission overrides them |

## Where it sits

It imports [nats-client](../../../nats-client/.specify/memory/spec.md) for the
client side of the bus and
[nats-server](../../../nats-server/.specify/memory/spec.md) for the embedded
server. [osapi-orchestrator](../../../osapi-orchestrator/.specify/memory/spec.md)
imports osapi.

A change to either NATS repository can break osapi's transport. A change to
osapi's SDK surface breaks the orchestrator, but the orchestrator pins a commit
rather than a tag, so nothing breaks there until somebody bumps it. Land a rename
and its bump together.

Its build fetches
[osapi-justfiles](../../../osapi-justfiles/.specify/memory/spec.md) through a
justfile recipe, from `main`. That edge is in no `go.mod`.

The organisation-wide picture is
[system's architecture](../../../../system/.specify/memory/architecture.md).

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

## Where knowledge lives

Two audiences, split by who is served rather than by where a file sits. This
corpus states how osapi is **built**, for a contributor or an agent. The published
site under `docs/docs/sidebar/` states how to **use** it, for an operator.

A rule lives in one of them and is cited from the other, never stated twice. A
citation names a requirement, and `just skill-lint` fails when one stops
resolving, which is what makes the one-statement rule enforceable rather than
aspirational.

The site does not send an operator here. A contributor page may, and three do; an
operator page answering with "see the specifications repository" has lost its
reader.

## What was measured

At `0cca62060`, 2026-09-29.

| Measurement              | Value | Command                                                                                                                   |
| ------------------------ | ----: | ------------------------------------------------------------------------------------------------------------------------- |
| Go files                 | 2,739 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                      |
| Go files excluding tests | 1,814 | `find . -name '*.go' -not -path './.git/*' -not -name '*_test.go' \| wc -l`                                               |
| Site pages               |   219 | `find docs/docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                      |
| Files under `docs/`      |   221 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                           |
| Provider categories      |     6 | `ls -d internal/provider/*/ \| wc -l`                                                                                     |
| API domains              |    24 | `ls -d internal/controller/api/node/*/ internal/controller/api/*/ \| grep -vE '/(gen\|mocks\|common\|apierr)/$' \| wc -l` |

**219 and 221 are different quantities.** 219 are published pages under
`docs/docs/`; 221 adds `docs/README.md` and `docs/SUPPORT.md`, which belong to the
Docusaurus project rather than to the site. Both are right about different
questions, and a reader given only one concludes the other is broken.

## Known limitations

**`sdk/guidelines.md` is still partly contributor knowledge on an operator's
site.** Its rules are stated here and the page demonstrates them with worked
examples, which is fine. What it holds beyond demonstration, the package structure
and the response pattern, has no counterpart here and no feature open for it.

**The orchestrator pins a commit, not a tag.** A rename here lands green and
breaks there at the bump.

**The `osapi-justfiles` fetch is unpinned.** Nothing records which version of a
shared recipe a build used.

## Not covered here

How any individual provider or domain works. There are 24 domains and 6 provider
categories, and the contract they share is in the subject documents above.

The CLI's full command surface, which is 143 pages of reference under `usage/cli`
where an operator should read it.

osapi's testing conventions, which are its own `CONTRIBUTING.md`'s.

______________________________________________________________________

Traced to the seven features under `specs/`: the provider contract, the agent key
store, the corpus backfill, the job system, building a domain, the baseline that
first said what this repository is, and the embedded UI.
