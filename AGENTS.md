# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers prerequisites, setup, how Spec Kit is
operated here, and every convention — all of which apply to agents exactly as
they apply to people. This file carries only what is specific to agents.

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

## Read the constitution first

Before starting work in a project, read its `.specify/memory/constitution.md`.
It is composed from `.charter/` and binds every project here.

Then read the rest of `.specify/memory/`. That is where completed work is
consolidated, and it is the standing description of how the component behaves —
more current than any prose written about it elsewhere.

## Invoke the skill, never the CLI

Each workflow step is a skill: `speckit-specify`, `speckit-plan`,
`speckit-tasks`, `speckit-archive-run`, and the rest under `.claude/skills/` in
each project. Invoke the skill.

The `specify` CLI provisions a project — it initializes, and it installs
extensions. It does not run the workflow. See @CONTRIBUTING.md under "Operating
Spec Kit".

## Where the design goes, and where the code goes

This repository holds no product code. A feature's spec, plan, and tasks are
written here; the implementation lands in the component's own repository.

Do not edit code in the same response that produces planning artifacts, even
when the request asks you to build something. Wait for an explicit instruction
to implement.

## When applying shows the rule is wrong

Stop and correct the rule in its own change, then resume. Correcting the rule
and the code together produces a rule written to describe what was already done,
and buries the correction where nobody reviews it as a change of rule. This is
`global/correction` in the constitution.

## Commit trailer

When committing via Claude Code, end the message with:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
