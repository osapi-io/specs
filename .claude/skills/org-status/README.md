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

Ask in plain language. Nothing needs special syntax.

### Reading

```
do i have any open PRs?
any dependabot PRs?
anything waiting on review?
any security alerts?
is CI green everywhere?
give me a sweep of what needs attention
```

Scope it by naming repositories and only those are queried:

```
any open PRs in gohai and nats-client?
```

### Triaging

Paste a security URL, or ask what an alert means:

```
https://github.com/osapi-io/osapi/security
what do i do about the osapi alerts?
are we actually exposed to these?
is that vulnerable code even reachable?
```

You get a verdict rather than a count: upgrade available, not affected, exposed
with no patch, or already dismissed.

### Fixing

Any of these work, and all of them show you the verdict and the exact command
before touching anything:

```
fix it
fix the osapi security alerts
dismiss them
dismiss the docker alerts as not_used
bump it
```

The verdict decides what the fix is. An upgrade is a version bump. A
reachability finding is a dismissal with the checked import paths recorded as
the comment. An exposed dependency with no upstream fix is a decision, and the
skill brings you the evidence rather than picking for you.

`fix` is the only path that writes, it always confirms first, and dismissals go
one alert at a time.

In Claude Code you can also invoke it directly with `/org-status`.

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

Alerts are triaged rather than counted. Dependabot knows a vulnerable version
is in `go.mod`; it does not know whether the vulnerable code runs. The skill
checks for a patched version, then checks which import paths the repository
actually uses, and reports one of four verdicts: upgrade available, not
affected, exposed with no patch, or already dismissed. "2 HIGH" is a count.
`HIGH 7.2 CVE-2026-42306 archive endpoint runs container binary on host` next
to a verdict is a decision.

Reachability is established once per module, not once per repository, and the
report says which other repositories share the dependency. The reader's next
question is always whether this is one problem or eight.

Output fits one terminal screen, with a twenty-line budget and bare URLs. A
terminal makes a bare address cmd-clickable; `[text](url)` hides it behind
punctuation you cannot click. Detail is offered rather than printed.

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

Validate the frontmatter after editing it. The `description` is a plain YAML
scalar, so a `: ` anywhere inside it makes the file invalid and the skill
silently undiscoverable. Nothing warns you:

```bash
uvx --with pyyaml python -c "
import re,sys,yaml,pathlib
t=pathlib.Path('.claude/skills/org-status/SKILL.md').read_text()
m=re.match(r'^---\n(.*?)\n---\n',t,re.S); assert m,'no frontmatter'
print(sorted(yaml.safe_load(m.group(1))))"
```

A new capability needs its triggers in the `description` as well as its route in
`SKILL.md`. The description is the only thing an agent sees before deciding to
load the skill, so a route nothing routes to is dead weight.

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
