## Why

An agent working in these repositories runs commands in a shell where `mise` is
not active. It therefore gets whatever version of a tool happens to be on the
path, not the version the repository declares.

This produced three false failure reports in one session: a formatter check
reported as broken when the repository was correct and the agent's `just` was
two minor versions behind what `.mise.toml` resolves. Each looked like a real
defect, and one was carried into a pull request description before being caught.

A person does not hit this, because `mise` activates in their shell when they
enter the directory. It is specific to agents, which is what `AGENTS.md` is for.

## What Changes

- `AGENTS.md` states that tools are invoked through the repository's version
  manager

## Impact

- `repo-standards` — one added requirement
- Seven repositories' `AGENTS.md`
