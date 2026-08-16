## ADDED Requirements

### Requirement: Agent guidance says how to invoke the repository's tools

`AGENTS.md` SHALL state that tools are invoked through the version manager the
repository declares, rather than from the shell's path.

A person working in a repository has that version manager active in their shell,
so the declared version is what they get. An agent runs commands in a shell
without it, and gets whatever happens to be installed — a different version,
silently.

The failure this produces is misleading rather than obvious: a check fails for
the agent and passes for everyone else, on a file nobody changed, and the
difference is invisible in the output.

#### Scenario: An agent runs a formatter

- **WHEN** an agent runs a repository's format check
- **THEN** it invokes it through the version manager, so the result matches what
  continuous integration reports

#### Scenario: An agent sees a failure nobody else sees

- **WHEN** a check fails for an agent and passes in continuous integration on
  the same commit
- **THEN** the version the agent invoked is the first thing to establish, before
  the failure is treated as real

#### Scenario: A repository declares no version manager

- **WHEN** a repository has no version manager configuration
- **THEN** that is a defect under the requirement that a tool a repository
  invokes is declared
