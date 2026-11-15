<p align="center">
  <picture>
    <source srcset="asset/logo-dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="asset/logo-light.svg" media="(prefers-color-scheme: light)">
    <img src="asset/logo-dark.svg" alt="specs" width="250">
  </picture>
</p>

<p align="center">The design docs for osapi-io. We write them before the code, and correct them when the code shows an error.</p>

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
You design something when you write its page. Then you build it. Then you
correct the page where the build showed an error. It is the same page all three
times. Nothing changes from one form into another, because that change is where
the design and the docs become different.
</p>

## Usage

[osapi-io] makes a Linux host operate like an appliance. One binary and a config
file give you a REST API, a CLI, a Go SDK and an embedded dashboard. They manage
hostname, DNS, disk, memory, load, packages, services, users, sysctl, cron,
certificates, containers, files and command execution. They do this on a fleet,
not on one machine.

All of the design follows from one fact: **osapi queues work for a host. It does
not call the host.** The controller writes a job and waits. An agent takes the
job, and a provider does the work on the machine. These properties come from
that one decision:

- at-least-once delivery
- the idempotency that each provider must have
- two independent timeouts
- a result for each host

```
components/     one page per repository, plus a page per subject
ARCHITECTURE.md how they fit together, and what breaks what
CONSTITUTION.md the rules every repository follows
```

Read [osapi](components/osapi/README.md) first. Its subject pages are below it.
Four of the other five repositories give data to it or use it.

## Doc-driven development

Design something when you write its page. Build it. Correct the page where the
build showed an error. It is the same page all three times. Nothing changes from
one form into another, because that change is where the design and the docs
become different.

Thus a change here is one of four things:

| You are                                 | Change                          |
| --------------------------------------- | ------------------------------- |
| Designing something new                 | A new page under its component  |
| Changing how something behaves          | The page that already covers it |
| Agreeing something between repositories | `ARCHITECTURE.md`               |
| Binding every repository to a rule      | `CONSTITUTION.md`               |

[CONTRIBUTING.md](CONTRIBUTING.md) has the test that selects one, and tells what
a page looks like.

### What keeps it honest

A reader. Give a person only the page. Ask the question that the page says it
answers. Fix what the person could not find. This test found these errors:

- seven permissions where a page said one
- thirteen struct fields where a page said fourteen
- a bucket TTL that a page described in the opposite direction

## The design docs

| Repository                                                    | Is                                           |
| ------------------------------------------------------------- | -------------------------------------------- |
| [osapi](components/osapi/README.md)                           | The API and the agent that manage a host     |
| [osapi-orchestrator](components/osapi-orchestrator/README.md) | A declarative layer over osapi's SDK         |
| [nats-client](components/nats-client/README.md)               | A wrapper over the NATS client               |
| [nats-server](components/nats-server/README.md)               | A NATS server embedded in its consumer       |
| [gohai](components/gohai/README.md)                           | A system fact collection library, standalone |
| [osapi-justfiles](components/osapi-justfiles/README.md)       | Shared `just` recipes                        |

These four facts surprise people most often. Each one has a page:

- A [missing row in a broadcast result](components/osapi/agent-identity.md) is
  not an error, and nothing reports it.
- [Audit redaction](components/osapi/audit.md) is a denylist that matches names,
  and no test checks it.
- A [direct permission](components/osapi/permissions.md) cancels each role on
  the token, and nothing tells you.
- [Ten minutes](components/osapi/exec.md) is a maximum, not a fallback. A job
  that needs twenty minutes does not get them.

## Skills

The skills here answer questions about all of the repositories. They also have
the operational knowledge for work in them.

No skill lists what it describes. `org-status` gets the repository list from
GitHub each time it runs. `add-a-domain` finds its reference domain in the
codebase. `document` reads the component pages that exist, not a table of them.
An inventory in a skill is correct on the day that somebody writes it. It is
incorrect after the next change, and nothing shows that change.

| Skill                                                   | Answers                                                                                                               |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| [document](.claude/skills/document/README.md)           | Where a design goes, what the page looks like, and if a page already covers it                                        |
| [org-status](.claude/skills/org-status/README.md)       | Open pull requests, Dependabot updates, security alerts, CI status, and the merge queue across [osapi-io]             |
| [add-a-domain](.claude/skills/add-a-domain/README.md)   | How to add an osapi domain: the provider and each layer that must have it, in the order that prevents rework          |
| [release](.claude/skills/release/README.md)             | If a repository needs a tag, which number it gets, and if the tag will publish                                        |
| [work-an-issue](.claude/skills/work-an-issue/README.md) | How to take an issue to a merged pull request: if the problem still occurs, its size, the fix and its test            |
| [ste-100](.claude/skills/ste-100/README.md)             | How to write and check pages in ASD-STE100 Simplified Technical English, the sentence rules that each page here obeys |

Each skill uses the [Agent Skills] format. A short `SKILL.md` sends the agent to
the correct reference file. An agent reads a reference file only when the
question needs it.

The skills are in `.claude/skills/`. `.agents/skills` is a link to that
directory, so each coding agent finds the same copy. `AGENTS.md` is the
instructions file for all agents. `CLAUDE.md` points to it.

## Contributing

Refer to the [Contributing](CONTRIBUTING.md) guide for the prerequisites, the
test that tells where a change goes, what a page looks like, and the PR
workflow.

## License

The [MIT] License.

[agent skills]: https://agentskills.io/specification
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
