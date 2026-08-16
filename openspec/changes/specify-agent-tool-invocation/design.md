## Context

`.mise.toml` declares the version of each tool a repository uses. Shell
activation puts those versions on the path when a person enters the directory.
An agent shelling out has no activation, so `just` resolves to whatever is
installed globally.

## Decisions

### Say it in AGENTS.md rather than solving it in tooling

The alternative is to make every recipe invoke tools through the version manager
itself, so the path does not matter. That spreads a workaround for one consumer
across every recipe in every shared module, and it would run `mise exec` on
machines where the shell already resolved correctly.

`AGENTS.md` exists for guidance that applies to agents and not to people. This
is exactly that: a person cannot hit the problem, and an agent hits it
constantly.

*Alternative considered:* rely on the agent noticing. It did not — three times
in one session, each time diagnosing the repository rather than the invocation,
and once writing the wrong diagnosis into a pull request description.

### State the symptom, not just the instruction

The requirement names what the failure looks like: a check that fails for the
agent and passes in continuous integration, on a file nobody edited. An
instruction alone is easy to skip; a described symptom is recognisable when it
happens, which is when the instruction is needed.
