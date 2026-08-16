# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers the workflow, the operating model,
formatting, and every convention — all of which apply to agents exactly as they
apply to people. This file carries only what is specific to agents.

## Running tools

Invoke tools through `mise`, not from your path:

```bash
mise exec -- just test
```

`mise` is active in a person's shell and supplies the versions `.mise.toml`
declares. An agent's shell has no activation, so a bare `just` resolves to
whatever is installed globally — usually an older version.

The symptom is a check that fails here and passes in continuous integration, on
a file nobody edited. When that happens, establish which version ran before
treating the failure as real.

## Running a change

Invoke the skill for every step. Never drive the `openspec` CLI yourself, and
never assemble a change by hand — the CLI is what the skill runs, and the guards
live in the workflow around it.

| Step    | Skill                     |
| ------- | ------------------------- |
| Explore | `openspec-explore`        |
| Propose | `openspec-propose`        |
| Apply   | `openspec-apply-change`   |
| Update  | `openspec-update-change`  |
| Sync    | `openspec-sync-specs`     |
| Archive | `openspec-archive-change` |

The `/opsx:*` slash commands in @CONTRIBUTING.md are the same instructions in
the form a person types. You cannot type them; invoke the skill instead.

The procedure is in @CONTRIBUTING.md under "Running a change". Follow it rather
than improvising: propose, merge, apply, archive — each step its own pull
request, except documentation-only changes where propose and archive belong in
one.

## Read the corpus first

Before starting work in any repository, read `openspec/specs/` for the
capabilities that bind it. `openspec/specs/repo-standards/` binds every
repository; the rest bind by type, recorded in the classification.

Requirements are not advice. A repository that does not satisfy one is
non-conformant, and work that leaves it that way is unfinished.

## When you find something

Before editing any repository, answer: **which requirement authorizes this?**

If a requirement covers it, the fix is compliance work — cite the requirement in
the pull request. If none does, propose the change first. Do not fix it and
write the requirement afterwards; that produces a corpus that describes what
already happened rather than what was agreed.

See @CONTRIBUTING.md under "When you find something".

## Planning boundary

`openspec-propose` produces planning artifacts and then stops. Do not edit code
in the same response, even when the request asks you to build or fix something.
Wait for an explicit instruction to apply.

Applying waits for the proposal PR to **merge**, not to exist. An open branch is
not an agreement.

If applying shows the requirement is wrong, stop and correct the requirement in
its own PR, then wait for that to merge before resuming. Do not change the
requirement and the code in one response: it produces a rule written to describe
code that already exists, and buries the rule change where nobody reviews it.
See @CONTRIBUTING.md under "Running a change".

## Writing artifacts

Do not write an artifact yourself. The propose skill retrieves each one's
template, its rules, and the artifacts to read first, then writes to them in
dependency order. Assembling one by hand produces something that validates and
does not conform — `just validate` checks structure, not conformance.

`openspec/config.yaml` carries project context and per-artifact rules that are
injected into every generation. Apply them as constraints; never copy them into
the output.

## Applying a change

- A task is checked only when its behavior is fully implemented — not partially,
  not deferred, not done in some repositories and not others.
- Scope beyond the task is surfaced, not absorbed. If a task needs more than the
  spec describes, or you are narrowing it to fit, stop and say so.
- A blocker pauses the work. Unclear task, design issue, error — report it and
  wait rather than guessing.
