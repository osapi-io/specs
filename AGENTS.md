# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers prerequisites, setup, the workflow end to
end, and every convention — all of which apply to agents exactly as they apply
to people. This file carries only what is specific to agents.

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

Before starting work in a component, read its `.specify/memory/constitution.md`,
then the rest of `.specify/memory/`. That is where completed work is
consolidated, and it is more current than any prose written about the component
elsewhere.

Nothing in this repository authorizes work that the constitution forbids. When
you cannot satisfy both a request and the constitution, say so rather than
picking one silently.

## The planning boundary

@CONTRIBUTING.md gives the workflow under "The lifecycle of a change". Two
things in it bind agents specifically:

**Producing planning artifacts ends the response.** Do not edit code in the same
response that runs `speckit-specify`, `speckit-plan`, or `speckit-tasks`, even
when the request was phrased as "build" or "fix". The request that triggered
planning does not authorize implementation.

**A merged spec is the authorization; a branch is not.** Wait for the spec PR to
merge before implementing against it.

## Commit trailer

When committing via Claude Code, end the message with:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
