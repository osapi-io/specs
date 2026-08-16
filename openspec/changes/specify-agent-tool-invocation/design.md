## Context

`.mise.toml` declares the version of each tool a repository uses. Shell
activation puts those versions on the path when a person enters the directory.
An agent shelling out has no activation, so `just` resolves to whatever is
installed globally.

The versions then differ between the agent, the person, and continuous
integration, on the same commit.

## Goals / Non-Goals

**Goals:**

- An agent runs a repository's checks at the versions that repository declares.
- When versions do differ, the failure is recognisable as a version problem
  rather than investigated as a defect in the code.

**Non-Goals:**

- Changing how any recipe is written. The problem belongs to one class of
  consumer; the recipes are shared by all of them.
- Detecting the mismatch automatically. Nothing here fails when an agent uses
  the wrong version — the guidance is what makes it avoidable.

## Decisions

### Say it in AGENTS.md rather than solving it in tooling

`AGENTS.md` exists for guidance that applies to agents and not to people. This
is exactly that: a person cannot hit the problem, and an agent hits it
constantly.

*Alternative considered:* make every recipe invoke tools through the version
manager, so the path does not matter. Rejected — it spreads a workaround for one
consumer across every recipe in every shared module, and runs the version
manager on machines where the shell already resolved correctly.

*Alternative considered:* rely on the agent noticing. It did not — three times
in one session, each time diagnosing the repository rather than the invocation,
and once writing the wrong diagnosis into a pull request description.

### State the symptom, not just the instruction

The requirement names what the failure looks like: a check that fails for the
agent and passes in continuous integration, on a file nobody edited.

*Alternative considered:* state the instruction alone and keep the file short.
Rejected because an instruction is read before the work, while the problem is
recognised during it — and the failure is convincing enough to send someone
investigating the wrong thing.

## Risks / Trade-offs

- **An agent never reads `AGENTS.md`.** → `CLAUDE.md` points at it and Claude
  Code loads that file by name, so the guidance is reached without the agent
  choosing to look for it.

- **Guidance cannot be enforced, so the wrong version can still be used.** → The
  symptom is stated next to the instruction, so the mistake stays recognisable
  after the fact even when the instruction was skipped.

- **`osapi` has no `AGENTS.md`, so the guidance has nowhere to land there.** →
  Its contributing-guide conversion creates one, and this change's task for that
  repository waits on it rather than working around it.

- **A repository adopts a different version manager and the instruction goes
  stale.** → The requirement is about invoking tools at the versions a
  repository declares, not about one tool, so the instruction can change without
  the requirement changing.

## What applying found

`osapi` has no `AGENTS.md` at all — the only repository without one, already
tracked as part of its contributing-guide conversion. The guidance lands there
when that file exists.

`osapi-justfiles` publishes the `md` module and did not consume it. Its eleven
markdown files — the root README and every module's — were formatted by nothing,
while every repository fetching from it had them formatted. It now imports
`md.just` like the rest.
