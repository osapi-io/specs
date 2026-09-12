# org-status

Answers "what needs my attention across [osapi-io]?" without you opening eight
browser tabs.

An [Agent Skills] skill. The agent loads only the name and description until a
question matches, then reads `SKILL.md`, then reads one reference file for the
category you asked about. Nothing else enters context.

## Install

Nothing to install. The skill lives at `.claude/skills/org-status/` in this
repository and any skills-aware agent working from the repository root finds it.

It needs the [gh] CLI, authenticated:

```bash
gh auth status
```

Security alert queries need one extra scope, which a stock `gh auth login` does
not grant:

```bash
gh auth refresh -h github.com -s security_events
```

Without it the alert endpoints return 403. The skill reports that as "the token
cannot see them" rather than as a clean result.

## Usage

Ask in plain language. These all route correctly:

```
do i have any open PRs?
any dependabot PRs?
anything waiting on review?
any security alerts across the org?
any vulnerabilities in osapi?
is CI green everywhere?
give me a sweep of what needs attention
```

In Claude Code you can also invoke it directly with `/org-status`.

Scope it by naming repositories, and it queries only those:

```
any open PRs in gohai and nats-client?
```

## Features

The repository list is never written down. Every run asks GitHub which
repositories exist, so a new repository is covered the day it is created and a
retired one stops being queried. The reasoning is in
[.charter/fragments/global/repositories.md](../../../.charter/fragments/global/repositories.md).

Human PRs and bot PRs are separated, because "do I have PRs" and "are there
Dependabot bumps" are different questions with different urgency.

Alerts and version bumps are separated too. An alert says a vulnerability
applies to you. A PR says a newer version exists. A repository with alerts and
no PR needs a manual bump, and that gap is easy to miss.

A query that failed is reported as a failure. Three of GitHub's security
endpoints return 404 for a repository that never enabled the feature, which
looks exactly like zero alerts if you only count array length. The skill
distinguishes "clean" from "not configured" from "token cannot see it".

## Documentation

| File                                                       | Covers                                                                    |
| ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md)                                       | Repository resolution, routing, reporting rules                           |
| [references/pull-requests.md](references/pull-requests.md) | Open PRs, author filtering, draft and mergeable and review state          |
| [references/security.md](references/security.md)           | Dependabot, code-scanning and secret-scanning alerts, and required scopes |
| [references/quality.md](references/quality.md)             | Default-branch checks, named workflows, release state, coverage           |

The [Agent Skills specification] documents the format.

## Contributing

See the [Contributing](../../../CONTRIBUTING.md) guide.

Keep `SKILL.md` a router. When it starts explaining how to run a query, that
explanation belongs in a reference file, because `SKILL.md` loads on every
activation and reference files load only when the question calls for them.

Every command in a reference file should be one that has been run against the
live org. A command that looks right and has never executed is the failure mode
this skill exists to avoid.

## License

The [MIT] License.

[agent skills]: https://agentskills.io
[agent skills specification]: https://agentskills.io/specification
[gh]: https://cli.github.com
[mit]: ../../../LICENSE
[osapi-io]: https://github.com/osapi-io
