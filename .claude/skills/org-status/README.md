# org-status

Answers "what needs my attention across [osapi-io]?" without opening eight
browser tabs.

## Install

Nothing to install. The skill lives in this repository and any skills-aware
agent working from the repository root finds it. It needs the [gh] CLI,
authenticated.

Security alert queries need one scope a stock `gh auth login` does not grant:

```bash
gh auth refresh -h github.com -s security_events
```

Without it the alert endpoints return 403, which the skill reports as "the token
cannot see them" rather than as a clean result.

## Usage

Ask in plain language, or invoke it directly with `/org-status`.

| Ask | You get |
| --- | --- |
| `any open PRs?` `anything waiting on review?` | Every open PR, human and bot separated, oldest first |
| `any dependabot PRs?` | Just the version bumps |
| `any security alerts?` `is CI green?` | Alert counts and default-branch health |
| `any open PRs in gohai?` | Only the repositories you name |
| a pasted `/security` URL, `are we exposed?` | A triage verdict for that repository |
| `fix it` `dismiss them` `bump it` | The fix for that verdict, shown before it runs |

Reading is the default. `fix` is the only path that writes, it always shows the
verdict and the exact command first, and it confirms even when you have already
said fix, because you would be approving a verdict you have not seen.

## How it works

The repository list comes from `gh repo list osapi-io` on every run, never from
a file here, so a new repository is covered the day it is created. The reasoning
is in
[.charter/fragments/global/repositories.md](../../../.charter/fragments/global/repositories.md).

`SKILL.md` routes and holds the output contract. One reference file loads for
the category you asked about, and nothing else enters context.

Alerts are triaged, not counted. Dependabot knows a vulnerable version is in
`go.mod`; it does not know whether the vulnerable code runs. Each alert resolves
to upgrade available, not affected, exposed with no patch, or already dismissed,
and the fix follows from which.

## Documentation

| File | Covers |
| --- | --- |
| [SKILL.md](SKILL.md) | Repository resolution, routing, the output shape |
| [references/pull-requests.md](references/pull-requests.md) | Open PRs, author filtering, draft and mergeable and review state |
| [references/security.md](references/security.md) | Dependabot, code-scanning and secret-scanning alerts, required scopes |
| [references/triage.md](references/triage.md) | The four verdicts, how to establish each, the fix for each |
| [references/quality.md](references/quality.md) | Default-branch checks, named workflows, release state, coverage |

Format details are in the [Agent Skills specification].

## Contributing

See the [Contributing](../../../CONTRIBUTING.md) guide. Run `just skill-lint`
after editing, and keep `SKILL.md` a router: an explanation of how to run a
query belongs in a reference file, which loads only when the question calls for
it.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[gh]: https://cli.github.com
[mit]: ../../../LICENSE
[osapi-io]: https://github.com/osapi-io
