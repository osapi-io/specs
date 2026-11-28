# Contributing

This repo is the design record for [osapi-io]. It has no product code. The
documents under `components/` describe how each repository operates. You change
these documents.

## How work happens here

This repo is doc-driven. You design something when you write the page. Then you
build it in its repository. Then you correct the page where the build showed an
error.

Before the build, the page is the design. After the build, it is the
description. It is the same page in the two stages, and that is the purpose.
There is no separate spec that somebody changes into documentation later,
because that change is where the two become different.

Thus a change here is one of three things:

- A new subject: a new page under the component, with a link from its README.
- A change to how something operates: an edit to the page that already covers
  it.
- An agreement between repositories: an edit to `ARCHITECTURE.md`. If each
  repository must obey the agreement, add a rule to `CONSTITUTION.md`.

To select the component, ask one question. Is the subject how one repository
operates, or an agreement that two repositories must keep? Job retry logic is
the operation of osapi. osapi and osapi-orchestrator both depend on the subject
names, but neither owns them. Thus the subject names go in `ARCHITECTURE.md`.

## Keep the descriptions in sync

Each part of osapi-io that a person or an agent builds on describes itself as
data, and a binary prints that data. The parts are each DSL of osapi
(`osapi dsl behavior`, `endpoint`, `command` and `chain`), the Go SDK
(`osapi sdk`), and gohai's collectors (`gohai collector` and
`osapi agent collector`). Each has the same four commands, each with `--json`:
`list`, `get --name`, `spec get` and `validate`.

A change to one of these parts is a change to its data. Thus the commands, the
generated pages and the skills agree with the build. Each change obeys these
rules:

- Change the data, not a copy. A spec term, a check, a doc comment or an example
  is the source. A page or a skill that repeats it goes stale.
- A skill sends the agent to the commands. It does not copy their output.
- A part that describes itself has the four commands. A new part gets them in
  the same change.
- osapi mounts gohai's own command, and does not copy it. A change to the
  collectors goes in gohai first, then a gohai tag, then osapi.
- The page of the part says that it describes itself, and names the commands.

A reviewer refuses a change that breaks one of these rules.

## Issues

The rule is [Tracking](CONSTITUTION.md#tracking). In practice:

Open an issue in the repository where the change goes. A finding about the code
of osapi is an osapi issue, not an issue here, because the person who fixes it
looks there. An issue here is for the design record itself:

- a page that is incorrect
- a subject with no page
- a rule that two places state

Open an issue when the work is larger than the current change. A one-line fix
that you find when you edit a page is part of that change. A provider that
decides idempotency incorrectly is not part of it. If you make the change larger
to include it, the fix is hidden in a diff about a different subject.

Give the evidence. The counts and commands that found the problem go in the
issue, for the same reason that they go in a page. A reader who cannot show the
problem again must trust you. In six months, you must also trust yourself.

Do not open an issue for a problem that an attacker can use, because an issue is
public when you open it. Make a draft advisory on the repository that it
affects.

### Labels

Each issue gets its labels when you open it. A reader finds work by label, and
an issue without labels is found only by its title. Before 21 November 2026, 225
of the 272 issues of the organization had no label.

| Label                    | When                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| `bug`                    | The code does not do what its page or its contract says                                    |
| `enhancement`            | New work: a feature, a migration, a new rule                                               |
| `documentation`          | A page or a doc is incorrect or missing, and the code is correct                           |
| `chore`                  | A change that no caller sees: a refactor, a cleanup, a test, CI                            |
| `tracker`                | An issue that groups others as sub-issues, such as osapi-io/osapi#964                      |
| `decision`               | The owner must choose before work starts. The issue gives the choices and a recommendation |
| `architecture`           | Long-term design of how the system fits together. Only the owner starts it                 |
| `blocked`                | The work waits on a different issue                                                        |
| `side-finding`           | Found during work on a different subject, and filed so that work stays its size            |
| `component/<part>`       | The part of the repository that the change goes in, such as `component/behavior-dsl`       |
| `needs-standards-review` | A pull request waits for its standards review                                              |
| `standards-reviewed`     | The standards reviewer passed the pull request                                             |
| `needs-code-review`      | A pull request waits for its code review                                                   |
| `code-reviewed`          | The code reviewer passed the pull request                                                  |

The last four labels are for pull requests, not issues. Only a reviewer adds a
passed label ([pr-review-model](.claude/skills/pr-review-model/SKILL.md)).

Give each issue one of the first six labels: its type. Add `blocked` and
`side-finding` when they apply. Add one or more `component/` labels in a
repository that has more than one part: osapi, gohai, osapi-lab,
osapi-orchestrator and this repository. In this repository, the component is the
organization component that the page is about, such as `component/osapi`, or
`component/skills`. To add a component, create the label with a description that
names its directories, and add it to the table below.

An agent does not pick an `architecture` issue, and a sweep does not list it as
work that is left. Examples are workflows, secret management and extensions. An
agent works on one only when the owner names it.

A `blocked` issue says what it waits on in three places. The label finds it.
GitHub's blocked-by link connects the two issues, so the issue that blocks shows
what it blocks. A `Blocked by:` line in the body names the issue, or the event
that is not an issue, such as a release:

```bash
gh issue edit "$n" --repo "osapi-io/$r" --add-label blocked
gh api -X POST "repos/osapi-io/$r/issues/$n/dependencies/blocked_by" \
  -F issue_id="$(gh api "repos/osapi-io/$r/issues/$blocker" -q .id)"
```

When the work that blocks it closes, remove `blocked`. A work item of a tracker
is a GitHub sub-issue of the tracker, not a line of a checklist.

`kind/` labels are for pull requests. The labeler sets them from the paths that
a pull request changes. Do not put them on issues.

| Repository         | Components                                                                                                                                                      |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| osapi              | `behavior-dsl`, `endpoint-dsl`, `command-dsl`, `validation`, `behaviors`, `agent`, `auth`, `controller`, `job`, `cli`, `sdk`, `ui`, `telemetry`, `ci`, `skills` |
| gohai              | `collectors`, `schema`, `ci`                                                                                                                                    |
| osapi-lab          | `image`, `hub`, `ci`                                                                                                                                            |
| osapi-orchestrator | `ops`, `engine`, `ci`                                                                                                                                           |
| specs              | one for each directory of `components/`, and `skills`, `constitution`                                                                                           |

## Prerequisites

```bash
brew install mise gh
mise trust && mise install
just fetch
just test
```

[mise] installs `just` and `uv` from `.mise.toml`. Install `gh` separately.
`mise` gets `gh` through `aqua`, and the attestation check of `aqua` fails for
that package.

## What a page looks like

Read [components/osapi/job-system.md](components/osapi/job-system.md) for the
shape. [CONSTITUTION.md](CONSTITUTION.md) has the rules. You will need these
rules first:

- Explain the system to a person who must work on it. `/document` has the voice
  and runs `unslop`. Use it. Do not write a page by hand.
- Write each sentence in Simplified Technical English, as
  [the constitution](CONSTITUTION.md) requires of each repository. `/ste-100`
  checks it.
- State a fact one time. Link to it from each other location that needs it.
- When there was a tradeoff, say what it was.

`just test` checks that each link works. It also fails on the signs of a bad
page that a script can find: an em dash, "MUST", a requirement identifier, a
user story. The skills check the voice and the STE. You must obey the last two
rules yourself.

## Before you commit

```bash
just test
```

That command checks the markdown format, the justfile lint, the skills, the
links and anchors, and the documentation contract. `just md-fmt` fixes the
format.

[mdformat] changes two things and does not tell you. Thus write them correctly
the first time:

- GitHub alert syntax (`> [!WARNING]`) becomes a plain blockquote, and GitHub
  does not show it as an alert.
- mdformat changes link definitions to lowercase and sorts them.

## Branches and commits

Make a branch from `main` as `type/short-description`. Use the
[Conventional Commits] type: `docs/add-firewall-page`,
`fix/correct-retry-count`.

A commit subject has 50 characters or fewer. Use the imperative, start with a
capital letter, and do not end with a period. Wrap the body at 72 characters.
Say what changed and why, not how.

If possible, keep a PR to one commit. Tell what changed and why in the
description. A reviewer must not need the diff to find the reason.

## AI usage

People write this repo with AI help, and the workflow expects it. The
[AI Usage Policy](AI_POLICY.md) applies. Tell which tool you used. You must be
able to explain your page without the tool.

[conventional commits]: https://www.conventionalcommits.org
[mdformat]: https://pypi.org/project/mdformat/
[mise]: https://mise.jdx.dev
[osapi-io]: https://github.com/osapi-io
