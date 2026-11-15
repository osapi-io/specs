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
- Give each count with the command that gives it. The command must work alone.
- State a fact one time. Link to it from each other location that needs it.
- When there was a tradeoff, say what it was.

`just test` checks the counts, and that each link works. It also fails on the
signs of a bad page that a script can find: an em dash, "MUST", a requirement
identifier, a user story. The skills check the voice and the STE. You must obey
the last two rules yourself.

## Before you commit

```bash
just test
```

That command checks the markdown format, the justfile lint, the skills, the
links and anchors, each count against its command, and the documentation
contract. `just md-fmt` fixes the format.

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
