# osapi-io design docs

How the six repositories behind [osapi-io](https://github.com/osapi-io) are
built, and why. No product code here.

**The product makes a Linux host behave like an appliance.** One binary, one
config file, and you get a REST API, a CLI, a Go SDK and an embedded dashboard
over hostname, DNS, disk, memory, load, packages, services, users, sysctl, cron,
certificates, containers, files and command execution. Across a fleet, not one
box.

The load-bearing design fact: **work reaches a host by being queued, not by
being called.** The controller writes a job and waits; an agent picks it up and
a provider does the work. At-least-once delivery, the idempotency providers owe,
two independent timeouts and a per-host result all come out of that one choice.

```
          nats-client ─┐
                       ├─→ osapi ──→ osapi-orchestrator
          nats-server ─┘

          gohai                    (standalone)
          osapi-justfiles          (every build, by fetch)
```

## Start here

| If you want to                           | Read                                                       |
| ---------------------------------------- | ---------------------------------------------------------- |
| Understand the product                   | [osapi](components/osapi/README.md), then its twelve pages |
| Know what breaks if you change something | [ARCHITECTURE.md](ARCHITECTURE.md)                         |
| Add a page, or know where one belongs    | [CONTRIBUTING.md](CONTRIBUTING.md)                         |
| Know the rules every repository follows  | [CONSTITUTION.md](CONSTITUTION.md)                         |
| See all six repositories                 | [components/](components/README.md)                        |

The four things most likely to surprise you, all written up:
[a missing row in a broadcast result is not an error](components/osapi/agent-identity.md),
[audit redaction is a name-matched denylist with no test](components/osapi/audit.md),
[a direct permission silently nullifies every role](components/osapi/permissions.md),
and [ten minutes is a ceiling, not a fallback](components/osapi/exec.md).

## Doc-driven development

Design something by writing its page. Build it. Correct the page where building
proved it wrong. Same page all three times, which is the point: nothing is
converted from one form into another, because that conversion is where the
design and the docs drift apart.

A feature is an edit to a page here plus a change in the repository it
describes. `/document` is the skill that does the first half.

### What keeps it honest

| Check               | Fails when                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| `just check-counts` | A count no longer matches the command written beside it, run in the repository the page describes |
| `just check-docs`   | A link is dead, a page is missing from its index, or a page reads like a spec instead of docs     |
| A reader            | They cannot answer the question the page claims to answer                                         |

The third is a person, not a script, and it has found more than the other two
together: seven permissions where a page said one, thirteen struct fields where
it said fourteen, a bucket TTL described backwards.

## history/

Fifteen specifications written under a workflow this repo no longer uses. Kept
because they record what was decided and when. Not maintained, and where one
disagrees with a page under `components/`, the page is right.
