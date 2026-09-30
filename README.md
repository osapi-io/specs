[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![powered by](https://img.shields.io/badge/powered%20by-spec--kit-blue.svg?style=for-the-badge)](https://github.com/github/spec-kit)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The spec-driven development workspace for [osapi-io]. Every change is designed
here first, then implemented in the repository it belongs to.

## Usage

This repository holds no product code. It holds the design record and the
durable knowledge behind [osapi-io]: what was agreed before something was built,
and why it is built that way.

It is a [Spec Kit] monorepo, and knowledge sits at one of three levels:

```
.charter/       rules binding every repository
components/     one project per repository, for how that repository behaves
system/         agreements between repositories: protocols, conventions, the graph
```

A change is designed here first, reviewed as a pull request, then implemented in
the repository it belongs to. What survives is each project's
`.specify/memory/`, the standing description of how things behave, which every
later change reads first and keeps honest.

Two things make that worth the overhead. Reviewers read the design on its own,
separate from the diff that implements it. And one place describes a change
spanning several repositories, instead of scattering it across them.

[CONTRIBUTING.md](CONTRIBUTING.md) has the workflow, the skills that run it, and
the test for which level a change belongs to.

## Skills

Skills in this repository answer questions that span every repository in the
organization, and carry the operational knowledge for working in them.

None of them lists what it describes. `org-status` takes the repository list
from GitHub on each run, and `add-a-domain` resolves its reference domain from
the codebase, so both stay correct as repositories and layers come and go. An
inventory written into a skill is right the day it is written and wrong after
the next change, with nothing marking the moment.

| Skill                                                 | Answers                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [org-status](.claude/skills/org-status/README.md)     | Open pull requests, Dependabot bumps, security alerts, whether CI is green, and working the merge queue across [osapi-io] |
| [add-a-domain](.claude/skills/add-a-domain/README.md) | Adding an osapi domain: the provider and every layer it has to appear in, in the order that avoids rework                 |

Each follows the [Agent Skills] format: a slim `SKILL.md` that routes, with the
detail in reference files an agent reads only when the question calls for them.

## The architecture documentation

[osapi-io](https://github.com/osapi-io) makes a Linux host behave like an
appliance: one binary and a config file give you a REST API and a CLI for
reading and changing system configuration, over a fleet rather than one box. Six
repositories build that.

Each repository's memory is its architecture document, kept current as features
land. Start with
[how they fit together](system/.specify/memory/architecture.md), or go straight
to one.

| Repository                                                                  | Is                                                                 |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| [osapi](components/osapi/.specify/memory/spec.md)                           | The API and the agent that manage a host                           |
| [osapi-orchestrator](components/osapi-orchestrator/.specify/memory/spec.md) | A declarative layer over osapi's SDK                               |
| [nats-client](components/nats-client/.specify/memory/spec.md)               | A wrapper over the NATS client                                     |
| [nats-server](components/nats-server/.specify/memory/spec.md)               | A NATS server embedded in its consumer                             |
| [gohai](components/gohai/.specify/memory/spec.md)                           | A system fact collection library, standalone                       |
| [osapi-justfiles](components/osapi-justfiles/.specify/memory/spec.md)       | Shared `just` recipes, fetched by every repository with a justfile |

osapi's is the one to read first, since four of the other five either feed it or
consume it. gohai is the exception and reads standalone. osapi links out to
twelve subjects of its own: the message bus, the job system, providers, building
a domain, agent identity, permissions, the audit trail, running commands, the Go
SDK, the embedded UI, configuration and observability.

The specifications under each `specs/` are the process that produced those
documents. They record what a change was going to do and are not written to be
read afterwards.

## Documentation

[CONTRIBUTING.md](CONTRIBUTING.md) covers prerequisites, setup, how to operate
Spec Kit here, and the PR workflow. The [Spec Kit] repository documents the tool
itself.

## Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## License

The [MIT] License.

[agent skills]: https://agentskills.io
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
[spec kit]: https://github.com/github/spec-kit
