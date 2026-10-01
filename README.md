[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![docs driven](https://img.shields.io/badge/docs-driven-blue.svg?style=for-the-badge)](CONTRIBUTING.md)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The design docs for [osapi-io]. How each repository is built and why, written
before the code and corrected when the code proves them wrong.

## Usage

This repository holds no product code. It holds the standing description of how
every other repository behaves, which is what the next change reads first.

```
components/     one page per repository, plus a page per subject
ARCHITECTURE.md how they fit together, and what breaks what
CONSTITUTION.md the rules every repository follows
history/        superseded specs, kept for the record
```

Doc-driven: you design something by writing its page, build it, then correct the
page where building proved it wrong. Same page all three times, and nothing is
converted from one form into another, because that conversion is where the
design and the docs drift apart.

Two things make that worth the overhead. A reviewer reads the design on its own,
separate from the diff that implements it. And one place describes a change
spanning several repositories, instead of scattering it across them.

`just test` keeps it honest. [check-counts](scripts/check-counts.py) runs every
count in every page against the command written beside it, in the repository
that page describes, so a number that moved breaks the build.
[check-docs](scripts/check-docs.py) fails on a dead link, a page missing from
its index, or a page that reads like a specification instead of documentation.
Neither catches prose that drifted from the code: a reader does, and has found
more than both scripts together.

[CONTRIBUTING.md](CONTRIBUTING.md) has the workflow, the test for where a change
belongs, and what a page looks like. [VOICE.md](VOICE.md) has how they are
written.

## Skills

Skills in this repository answer questions that span every repository in the
organization, and carry the operational knowledge for working in them.

None of them lists what it describes. `org-status` takes the repository list
from GitHub on each run, `add-a-domain` resolves its reference domain from the
codebase, and `document` reads the pages that exist rather than a table of them,
so all three stay correct as repositories and layers come and go. An inventory
written into a skill is right the day it is written and wrong after the next
change, with nothing marking the moment.

| Skill                                                 | Answers                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [document](.claude/skills/document/README.md)         | Where a design goes, what the page looks like, and whether one already covers it                                          |
| [org-status](.claude/skills/org-status/README.md)     | Open pull requests, Dependabot bumps, security alerts, whether CI is green, and working the merge queue across [osapi-io] |
| [add-a-domain](.claude/skills/add-a-domain/README.md) | Adding an osapi domain: the provider and every layer it has to appear in, in the order that avoids rework                 |

Each follows the [Agent Skills] format: a slim `SKILL.md` that routes, with the
detail in reference files an agent reads only when the question calls for them.

## The architecture documentation

[osapi-io] makes a Linux host behave like an appliance: one binary and a config
file give you a REST API and a CLI for reading and changing system
configuration, over a fleet rather than one box.

The design fact everything else follows from is that **work reaches a host by
being queued, not by being called.** The controller writes a job and waits; an
agent picks it up and a provider does the work on the machine. At-least-once
delivery, the idempotency providers owe, two independent timeouts and a per-host
result all come out of that one choice.

Each repository's page is its architecture document, kept current as changes
land. Start with [how they fit together](ARCHITECTURE.md), or go straight to
one.

| Repository                                                    | Is                                                                 |
| ------------------------------------------------------------- | ------------------------------------------------------------------ |
| [osapi](components/osapi/README.md)                           | The API and the agent that manage a host                           |
| [osapi-orchestrator](components/osapi-orchestrator/README.md) | A declarative layer over osapi's SDK                               |
| [nats-client](components/nats-client/README.md)               | A wrapper over the NATS client                                     |
| [nats-server](components/nats-server/README.md)               | A NATS server embedded in its consumer                             |
| [gohai](components/gohai/README.md)                           | A system fact collection library, standalone                       |
| [osapi-justfiles](components/osapi-justfiles/README.md)       | Shared `just` recipes, fetched by every repository with a justfile |

osapi's is the one to read first, since most of the others either feed it or
consume it. gohai is the exception and reads standalone. osapi links out to
subjects of its own: the message bus, the job system, providers, building a
domain, agent identity, permissions, the audit trail, running commands, the Go
SDK, the embedded UI, configuration and observability.

The things most likely to catch you out, each written up where it belongs: a
[missing row in a broadcast result](components/osapi/agent-identity.md) is not
an error and nothing reports it, [audit redaction](components/osapi/audit.md) is
a name-matched denylist with no test behind it, a
[direct permission](components/osapi/permissions.md) silently nullifies every
role on the token, and [ten minutes](components/osapi/exec.md) is a ceiling
rather than a fallback.

The specs under [history/](history/) are the process that produced these
documents. They record what a change was going to do, are not maintained, and
where one disagrees with a page the page is right.

## Documentation

[CONTRIBUTING.md](CONTRIBUTING.md) covers prerequisites, setup, where a change
belongs, and the PR workflow. [CONSTITUTION.md](CONSTITUTION.md) is the rules.
[VOICE.md](VOICE.md) is how the docs are written.

## Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## License

The [MIT] License.

[agent skills]: https://code.claude.com/docs/en/skills
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
