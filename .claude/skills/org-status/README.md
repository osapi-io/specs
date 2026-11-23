# org-status

Answers "what needs my attention across [osapi-io]?", and you do not need to
open eight browser tabs.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. It needs the [gh] CLI,
authenticated.

Security alert queries need one scope a stock `gh auth login` does not grant:

```bash
gh auth refresh -h github.com -s security_events
```

Without it the alert endpoints return 403, which the skill reports as "the token
cannot see them" rather than as a clean result.

A read needs nothing more. A merge, a rebase, the dismissal of an alert and the
deletion of a branch are writes. Thus they need push access to the repository
that they act on.

## Usage

Ask in plain language, or invoke it directly with `/org-status`.

| Ask                                                          | You get                                                                                                                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `any open PRs?` `anything waiting on review?`                | Every open PR, human and bot separated, oldest first                                                                                                    |
| `any dependabot PRs?`                                        | Just the version bumps                                                                                                                                  |
| `what issues are open?` `what is left to work?`              | Open issues per repository, minus the ones a pull request already closes                                                                                |
| `any security alerts?` `is CI green?`                        | Alert counts, default-branch health, Go version drift                                                                                                   |
| `any stale branches?`                                        | Remote branches classified by whether deleting them loses work                                                                                          |
| `are the examples out of date?`                              | Nested modules Dependabot does not watch                                                                                                                |
| `any open PRs in gohai?`                                     | Only the repositories you name                                                                                                                          |
| a pasted `/security` URL, `are we exposed?`                  | A triage verdict for that repository                                                                                                                    |
| `fix it` `dismiss them` `bump it`                            | The fix for that verdict, shown before it runs                                                                                                          |
| `is #631 safe?` `could any PR be malicious?`                 | A vetting verdict: provenance, files, typosquats, release age, known-malicious versions                                                                 |
| `have we been hacked?` `do we depend on anything malicious?` | A compromise audit: access, commit authors, every lockfile against OSV, Action advisories, release tags, then missing cooldowns and unwatched lockfiles |
| `merge the open PRs` `work the queue`                        | The merge order, a rebase for each bump, and a verdict for anything red                                                                                 |

Reading is the default. Two paths write, and they differ in what they ask of
you.

`fix` always shows the verdict and the exact command first. It asks for
confirmation also when you already said fix, because without it you approve a
verdict that you did not see.

`merge` merges only what is already green. It reports a failed check with its
cause. It does not rebase and hope, because a rebase cannot fix the usual
failure here.

The skill's `allowed-tools` grants those writes for the turn that invokes it,
and the grant clears on your next message. A queue that spans turns is invoked
again, which is deliberate: each turn restates the intent.

## How it works

The repository list comes from `gh repo list osapi-io` on each run, never from a
file here. Thus the skill covers a new repository on the day that somebody makes
it. The reason is in [the constitution](../../../CONSTITUTION.md#repositories).

`SKILL.md` routes and holds the output contract. One reference file loads for
the category you asked about, and nothing else enters context.

Issues and task lists answer different questions. Thus the skill does not treat
them in the same way. An issue is an intent that nobody works on. The Spec Kit
task list tracks work in progress. The skill reports an issue with an open pull
request as in progress, not as remaining work.
[The constitution](../../../CONSTITUTION.md#tracking) states the division.

Alerts are triaged, not counted. Dependabot knows a vulnerable version is in
`go.mod`; it does not know whether the vulnerable code runs. Each alert resolves
to upgrade available, not affected, exposed with no patch, or already dismissed,
and the fix follows from which.

Read a red bump in the same way. `mergeable` and the check rollup answer
different questions. The failure that occurs again and again here is the tidy
gate of the repository, not the dependency. The bump leaves the module untidy.
Or the committed root module was already untidy, because `go get -tool` moved
the dependencies of the linter upstream. A rebase fixes neither. Thus find the
cause before you queue anything.

## Documentation

| File                                                       | Covers                                                                                                               |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md)                                       | Repository resolution, routing, the output shape                                                                     |
| [references/pull-requests.md](references/pull-requests.md) | Open PRs, author filtering, draft and mergeable and review state                                                     |
| [references/issues.md](references/issues.md)               | Open issues, what a pull request already has in hand, trackers, closing one                                          |
| [references/security.md](references/security.md)           | Dependabot, code-scanning and secret-scanning alerts, required scopes                                                |
| [references/triage.md](references/triage.md)               | The four verdicts, how to establish each, the fix for each                                                           |
| [references/branches.md](references/branches.md)           | Classifying remote branches as merged, abandoned, active or protected                                                |
| [references/modules.md](references/modules.md)             | Nested `examples/` modules: tidiness, go directive, dependency bumps                                                 |
| [references/quality.md](references/quality.md)             | Default-branch checks, Go version drift, named workflows, release state                                              |
| [references/vetting.md](references/vetting.md)             | Supply-chain checks on a pull request: impersonation, stray files, typosquats, release age, known-malicious versions |
| [references/audit.md](references/audit.md)                 | Signs of compromise across the org, and the defences that should be in place                                         |
| [scripts/deps.sh](scripts/deps.sh)                         | Every locked dependency of a repository, from `go.sum`, `bun.lock` and `package-lock.json`                           |
| [scripts/osv-malicious.sh](scripts/osv-malicious.sh)       | Asks OSV about a dependency list and flags malicious or hijacked versions                                            |
| [scripts/resembles.py](scripts/resembles.py)               | Flags module paths that resemble one already depended on                                                             |
| [references/merging.md](references/merging.md)             | Merge order, Dependabot rebases, waiting on checks, why a rebase cannot fix a red bump                               |

Format details are in the [Agent Skills specification].

## Contributing

Refer to the [Contributing](../../../CONTRIBUTING.md) guide. Keep `SKILL.md` a
router. An explanation of how to run a query goes in a reference file, which
loads only when the question needs it. The output shape stays in `SKILL.md`,
because each route makes it. A reference with it loads on each run.

Do not run mdformat on this directory. `just md-fmt` already excludes
`.claude/**`. mdformat reads the first `---` as a horizontal rule, and changes
the YAML frontmatter into a heading. Then agents cannot find the skill, and
nothing reports it.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[gh]: https://cli.github.com
[mit]: ../../../LICENSE
[osapi-io]: https://github.com/osapi-io
