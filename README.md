<p align="center">
  <picture>
    <source srcset="asset/logo-dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="asset/logo-light.svg" media="(prefers-color-scheme: light)">
    <img src="asset/logo-dark.svg" alt="specs" width="250">
  </picture>
</p>

<p align="center">The design docs for osapi-io. Written before the code, corrected when the code proves them wrong.</p>

<p align="center">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge"></a>
  <a href="https://conventionalcommits.org"><img alt="conventional commits" src="https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge"></a>
  <a href="CONTRIBUTING.md"><img alt="docs driven" src="https://img.shields.io/badge/docs-driven-blue.svg?style=for-the-badge"></a>
  <a href="https://just.systems"><img alt="built with just" src="https://img.shields.io/badge/Built_with-Just-black?style=for-the-badge&logo=just&logoColor=white"></a>
  <img alt="github commit activity" src="https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge">
</p>

<p align="center">
<b>Doc-driven: the page is the design, then the description.</b>
</p>

<p align="center">
You design something by writing its page, build it, then correct the page where
building proved it wrong. Same page all three times, so nothing is converted from
one form into another, because that conversion is where the design and the docs
drift apart.
</p>

## Usage

[osapi-io] makes a Linux host behave like an appliance. One binary and a config
file give you a REST API, a CLI, a Go SDK and an embedded dashboard over
hostname, DNS, disk, memory, load, packages, services, users, sysctl, cron,
certificates, containers, files and command execution, across a fleet rather
than one box.

The design fact everything else follows from: **work reaches a host by being
queued, not by being called.** The controller writes a job and waits; an agent
picks it up and a provider does the work on the machine. At-least-once delivery,
the idempotency providers owe, two independent timeouts and a per-host result
all come out of that one choice.

```
components/     one page per repository, plus a page per subject
ARCHITECTURE.md how they fit together, and what breaks what
CONSTITUTION.md the rules every repository follows
```

Read [osapi](components/osapi/README.md) first. Its subject pages hang off it,
and four of the other five repositories either feed it or consume it.

## Doc-driven development

Design something by writing its page. Build it. Correct the page where building
proved it wrong. Same page all three times, and nothing is converted from one
form into another, because that conversion is where the design and the docs
drift apart.

So a change here is one of four things:

| You are                                 | Change                          |
| --------------------------------------- | ------------------------------- |
| Designing something new                 | A new page under its component  |
| Changing how something behaves          | The page that already covers it |
| Agreeing something between repositories | `ARCHITECTURE.md`               |
| Binding every repository to a rule      | `CONSTITUTION.md`               |

[CONTRIBUTING.md](CONTRIBUTING.md) has the test for which, and what a page looks
like.

### What keeps it honest

A reader. Hand somebody the page and nothing else, ask them the question it
claims to answer, and fix what they could not work out. That has found seven
permissions where a page said one, thirteen struct fields where it said
fourteen, and a bucket TTL described backwards.

## The design docs

| Repository                                                    | Is                                           |
| ------------------------------------------------------------- | -------------------------------------------- |
| [osapi](components/osapi/README.md)                           | The API and the agent that manage a host     |
| [osapi-orchestrator](components/osapi-orchestrator/README.md) | A declarative layer over osapi's SDK         |
| [nats-client](components/nats-client/README.md)               | A wrapper over the NATS client               |
| [nats-server](components/nats-server/README.md)               | A NATS server embedded in its consumer       |
| [gohai](components/gohai/README.md)                           | A system fact collection library, standalone |
| [osapi-justfiles](components/osapi-justfiles/README.md)       | Shared `just` recipes                        |

The four things most likely to catch you out, all written up: a
[missing row in a broadcast result](components/osapi/agent-identity.md) is not
an error and nothing reports it, [audit redaction](components/osapi/audit.md) is
a name-matched denylist with no test behind it, a
[direct permission](components/osapi/permissions.md) silently nullifies every
role on the token, and [ten minutes](components/osapi/exec.md) is a ceiling
rather than a fallback, so a job that needs twenty does not get them.

## Skills

Skills here answer questions that span every repository, and carry the
operational knowledge for working in them.

None of them lists what it describes. `org-status` takes the repository list
from GitHub on each run, `add-a-domain` resolves its reference domain from the
codebase, and `document` reads the component pages that exist rather than a
table of them. An inventory written into a skill is right the day it is written
and wrong after the next change, with nothing marking the moment.

| Skill                                                 | Answers                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [document](.claude/skills/document/README.md)         | Where a design goes, what the page looks like, and whether one already covers it                                          |
| [org-status](.claude/skills/org-status/README.md)     | Open pull requests, Dependabot bumps, security alerts, whether CI is green, and working the merge queue across [osapi-io] |
| [add-a-domain](.claude/skills/add-a-domain/README.md) | Adding an osapi domain: the provider and every layer it has to appear in, in the order that avoids rework                 |

Each follows the [Agent Skills] format: a slim `SKILL.md` that routes, with the
detail in reference files an agent reads only when the question calls for them.

## Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, the test for
where a change belongs, what a page looks like, and the PR workflow.

## License

The [MIT] License.

[agent skills]: https://code.claude.com/docs/en/skills
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
