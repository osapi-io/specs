# Contributing

Contributions to specs are very welcome, but we ask that you read this document
before submitting a PR. It covers everything you need: prerequisites, setup, how
Spec Kit is operated here, and the conventions we hold PRs to.

## Before you start

- Read the [Code of Conduct](CODE_OF_CONDUCT.md). It applies to every
  interaction in this repo.
- **Check existing work** — Is there an existing PR? Is there a feature already
  underway under a component's `specs/` covering the same ground? Please make
  sure you consider/address these before starting a new one.
- **Design before you implement** — This repo exists so that the thinking
  happens first. Write the spec and get agreement on it before writing the
  implementation in the target repository.

## Prerequisites

- **[mise]** — Provisions every other tool from `.mise.toml`. This is the only
  dependency you install yourself:

  ```bash
  brew install mise
  ```

  Then [activate it in your shell][mise-activate] so tools land on `PATH` when
  you `cd` into the repo.

Everything below is provisioned by `mise install` (see [Setup](#setup)):

- **[just]** — Task runner. `just test` runs every check CI runs.

- **[uv]** — Python package runner. Nothing Python is installed here: both
  [mdformat] and the [Spec Kit] CLI are fetched and run by `uvx` at the version
  the justfile pins.

### Claude Code

If you use [Claude Code] for development, install these plugins from the default
marketplace:

```
/plugin install commit-commands@claude-plugins-official
/plugin install superpowers@claude-plugins-official
```

- **commit-commands** — provides `/commit` and `/commit-push-pr` slash commands
  that follow the project's commit conventions automatically.
- **superpowers** — provides structured workflows for planning, TDD, debugging,
  code review, and git worktree isolation.

The `speckit-*` skills come from Spec Kit itself. They are generated into each
project's `.claude/skills/` and committed, so they work as soon as you clone the
repo — no per-developer setup.

## Setup

```bash
mise trust       # approve .mise.toml (once)
mise install     # just, uv
just fetch       # shared justfile modules
```

Verify:

```bash
just test        # runs every check CI runs
```

## Repository layout

This is a [Spec Kit] monorepo. It holds no product code — only the design record
and the durable knowledge behind [osapi-io].

```
.charter/                    # shared constitution fragments (the registry)
├── manifest.yml
└── fragments/global/        # fragments every component composes

DEPENDENCIES.md              # how the repositories relate

components/
└── osapi/                   # a Spec Kit project
    ├── .specify/
    │   ├── memory/          # constitution + consolidated knowledge
    │   ├── charter/         # which fragments this component composed
    │   ├── extensions/      # charter, archive
    │   └── templates/
    ├── .claude/skills/      # speckit-* skills
    └── specs/               # features, in flight and merged
```

Each osapi-io component gets its own project directory under `components/`. The
component's code stays in its own repository; what lives here is what was agreed
and why.

## Operating Spec Kit

### Where the CLI comes from

The `specify` CLI is never installed. It is run through `uvx` at the version the
root justfile pins in `speckit_version`:

```bash
just spec osapi extension list
```

That wraps `uvx --from specify-cli==<pinned> specify` with `SPECIFY_INIT_DIR`
set to `components/<name>`, so `just spec <component> <args>` addresses one
component without changing directories.

Pinning it is deliberate: `specify` writes templates and scaffolding into
`.specify/`, and an unpinned CLI would rewrite committed files differently
depending on who ran it. This is `global/tooling` in the constitution.

### The CLI provisions; the skills do the work

Two different things share the name "Spec Kit", and confusing them is the most
common way to go wrong here:

|               | The `specify` CLI                            | The `speckit-*` skills       |
| ------------- | -------------------------------------------- | ---------------------------- |
| **Run by**    | `just spec <component> …`                    | Claude Code, invoked by name |
| **Does**      | Initializes a component, installs extensions | Runs the change workflow     |
| **How often** | Once per component, then rarely              | Every change                 |

**Never drive the workflow with the CLI.** Invoke the skill.

### Adding a project

```bash
mkdir components/<name>
just spec <name> init --here --force --non-interactive --integration claude
just spec <name> extension add charter --from \
  https://github.com/Fyloss/spec-kit-charter/archive/refs/tags/v0.6.1.tar.gz
just spec <name> extension add archive --from \
  https://github.com/stn1slv/spec-kit-archive/archive/refs/tags/v1.3.0.tar.gz
```

Both extensions are installed from a tagged source tarball rather than by
catalog name. The catalog resolves to the default branch, so a catalog install
would give a different project a different version of the extension.

Then point it at the shared registry and compose its constitution — invoke
`speckit-charter-config`, answering `../../.charter` for the registry, then
`speckit-charter-compose`.

### The constitution

Every component's `.specify/memory/constitution.md` is composed from
`.charter/`, not hand-written. Editing it directly is lost the next time it is
composed.

To change what binds every project, edit the fragment in `.charter/fragments/`
and recompose. The fragments are mandatory in `manifest.yml`, so every component
takes all of them.

Each fragment states a rule this organization arrived at by getting it wrong
first. A rule invented to fill out a template is noise, and `global/correction`
says as much — write requirements from evidence the repository already carries.

### The lifecycle of a change

`main` is protected, so each stage below is its own pull request. Every skill
runs against one component: invoke it from that component's directory, or set
`SPECIFY_INIT_DIR=components/<name>` so it writes to the right component.

| Stage        | Invoke                | Produces                                                   | PR?        |
| ------------ | --------------------- | ---------------------------------------------------------- | ---------- |
| 1. Specify   | `speckit-specify`     | `spec.md` — what must be true, and why                     | yes        |
| 2. Clarify   | `speckit-clarify`     | resolved ambiguities, folded into `spec.md`                | same PR    |
| 3. Plan      | `speckit-plan`        | `plan.md` — the approach, checked against the constitution | same PR    |
| 4. Tasks     | `speckit-tasks`       | `tasks.md` — the work, in order                            | same PR    |
| 5. Analyze   | `speckit-analyze`     | a consistency report across the three                      | no         |
| 6. Implement | —                     | code, in the component's own repository                    | yes, there |
| 7. Archive   | `speckit-archive-run` | consolidated `.specify/memory/`                            | yes        |

#### Starting a change

Run `speckit-specify` against the component the change belongs to. It creates
`components/<name>/specs/###-slug/` and writes `spec.md` there.

Pick the component by where the code will land. A change that alters osapi's
behavior is an osapi feature even when it also touches nats-client — see
"Changes that span components" below.

Then work stages 2 through 4 in the same branch. They are one unit of review:
splitting them means reviewing an approach against a spec that has not been
agreed, or a task list against a plan nobody read. Run `speckit-analyze` last
and fix what it reports before asking for review.

**Do not implement yet.** Producing planning artifacts ends the work; the
request that triggered them does not authorize code, however it was phrased.

#### Closing a change

1. **Merge the spec PR.** This is the agreement. A branch is not one, and
   implementation written against an unmerged spec is written against your own
   opinion.

2. **Implement** in the component's own repository, in that repository's own PR.
   Link it to the spec PR. Nothing here changes during implementation.

3. **Merge the implementation.** The change is now real but not yet recorded.

**When implementing shows the spec is wrong — stop.** Correct the spec in its
own PR here, wait for it to merge, then resume. Correcting both at once produces
a spec written to match code that already exists, and hides the correction
inside an implementation diff where nobody reviews it as a change of rule. This
is the failure the whole workflow exists to prevent, and it is not a sign the
process failed — a spec that gets corrected under contact is worth more than one
nobody tested.

#### Making it evergreen

Archiving is the step that turns a finished change into standing knowledge. Skip
it and the feature directory becomes a record of something that happened, which
is what the previous system accumulated 14 of.

Run `speckit-archive-run <feature-dir>` once the implementation has merged. It
consolidates the feature into `components/<name>/.specify/memory/` — merging
into `spec.md` and `plan.md`, recording supersessions in `changelog.md`, and
adding `[Source: ...]` refs so every line can be traced to the feature that
produced it.

It asks before deleting anything a later feature replaced. Read those prompts:
confirming a supersession removes the old requirement permanently, and declining
records an unresolved contradiction that the next archival raises again.

What survives is memory, not the feature directory. Memory is what the next
change reads first, so a component's memory — not its code, and not prose
written about it elsewhere — is the answer to "how does this behave today".

#### Changes that span components

A feature belongs to exactly one component: the one whose behavior changes. When
a change requires work in several repositories, that is a property of the
implementation, not a reason to split the spec.

Name every affected repository in the spec, implement across them, and archive
once, into the owning component. A fact about how the repositories relate —
rather than about any one of them — belongs in `DEPENDENCIES.md` at the root.

### Why memory, not a docs tree

`.specify/memory/` is where completed work is consolidated, and it is what a
skill reads first. It is Spec Kit's own directory for durable project knowledge
— nothing to do with Claude Code's memory.

That is also why there is no `docs/` tree here. A second place to write things
down becomes the place that goes stale, because nothing reads it and nothing
regenerates it.

## What goes where

Prose that restates something a file already says is prose that will eventually
contradict it. Before writing documentation, place it:

| The thing                     | Lives in                     | Never in                     |
| ----------------------------- | ---------------------------- | ---------------------------- |
| A rule binding every project  | `.charter/fragments/`        | A project's own constitution |
| How a component behaves today | its `.specify/memory/`       | A prose overview             |
| Why a change was made         | the feature's spec           | A commit message alone       |
| A tool version                | `.mise.toml` or the justfile | Prose naming the version     |

A rule a tool already enforces is never restated as prose. The configuration is
the statement of record; documentation names where it lives. This is
`global/documentation` in the constitution — which each project composes, so it
binds work here too.

## Before committing

Artifacts are markdown, so they are subject to the same formatting checks as
everything else here. Before opening a pull request, run:

```bash
just test
```

That runs what CI runs — markdown formatting and justfile lint. `just md-fmt`
fixes formatting failures.

Two things [mdformat] rewrites silently, so write them correctly the first time:

- GitHub alert syntax (`> [!WARNING]`) is reflowed into a plain blockquote and
  stops rendering as a callout. Use bold text instead.
- Link definitions are lowercased and sorted.

`.claude/` and `.specify/` are excluded from formatting. Those files are
vendored or generated, and formatting them produces churn that the next
`specify init --force` discards.

## Branching

All changes should be developed on feature branches. Create a branch from `main`
using the naming convention `type/short-description`, where `type` matches the
[Conventional Commits] type:

- `feat/add-health-endpoint-spec`
- `fix/correct-retry-scenario`
- `docs/update-readme`
- `chore/update-dependencies`

When using Claude Code's `/commit` command, a branch will be created
automatically if you are on `main`.

## Commit messages

Follow [Conventional Commits] with the 50/72 rule:

- **Subject line**: max 50 characters, imperative mood, capitalized, no period
- **Body**: wrap at 72 characters, separated from subject by a blank line
- **Format**: `type(scope): description`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
- Summarize the "what" and "why", not the "how"

Try to write meaningful commit messages and avoid having too many commits on a
PR. Most PRs should likely have a single commit (although for bigger PRs it may
be reasonable to split it in a few). Git squash and rebase is your friend!

## Submitting a PR

- **Describe your changes** — Ensure that you provide a comprehensive
  description of your changes.
- **Issue/PR links** — Link any previous work such as related issues or PRs, and
  link the implementation PR in the target repo when there is one. Please
  describe how your changes differ to/extend this work.
- **Draft PRs** — If your changes are incomplete, but you would like to discuss
  them, open the PR as a draft and add a comment to start a discussion. Using
  comments rather than the PR description allows the description to be updated
  later while preserving any discussions.

## AI usage

This repo is written with AI assistance and the workflow assumes it. All
contributions are still subject to the [AI Usage Policy](AI_POLICY.md) —
disclose the tool you used, and make sure you can explain what your spec says
without the aid of AI tools.

## FAQ

> I want to contribute, where do I start?

All kinds of contributions are welcome, whether it's a typo fix or a new
feature. You can also contribute by commenting on open specs — review is the
most valuable thing you can give a spec.

> I'm stuck, where can I get help?

If you have questions, feel free to open a [Discussion] on GitHub.

[claude code]: https://claude.ai/code
[conventional commits]: https://www.conventionalcommits.org
[discussion]: https://github.com/osapi-io/specs/discussions
[just]: https://just.systems
[mdformat]: https://pypi.org/project/mdformat/
[mise]: https://mise.jdx.dev
[mise-activate]: https://mise.jdx.dev/getting-started.html
[osapi-io]: https://github.com/osapi-io
[spec kit]: https://github.com/github/spec-kit
[uv]: https://docs.astral.sh/uv/
