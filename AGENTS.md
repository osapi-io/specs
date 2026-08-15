# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers the workflow, the operating model,
formatting, and every convention — all of which apply to agents exactly as they
apply to people. This file carries only what is specific to agents.

## Running a change

The procedure, with commands, is in @CONTRIBUTING.md under "Running a change".
Follow it rather than improvising: propose, merge, apply, archive — each step
its own pull request, except documentation-only changes where propose and
archive belong in one.

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

`/opsx:propose` produces planning artifacts and then stops. Do not edit code in
the same response, even when the request asks you to build or fix something.
Wait for an explicit instruction to apply.

Applying waits for the proposal PR to **merge**, not to exist. An open branch is
not an agreement.

If applying shows the requirement is wrong, stop and correct the requirement in
its own PR, then wait for that to merge before resuming. Do not change the
requirement and the code in one response: it produces a rule written to describe
code that already exists, and buries the rule change where nobody reviews it.
See @CONTRIBUTING.md under "Running a change".

## Writing artifacts

Read `openspec/config.yaml` before generating any artifact. Its `context` and
`rules` are injected into every generation — apply them as constraints, and do
not copy them into the output.

Follow the artifact build order from `openspec status`, not the order the
templates happen to appear in.
