# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers prerequisites, setup, the workflow end to
end, and every convention. All of it applies to agents exactly as it applies to
people. This file has only what is specific to agents.

## Running tools

Invoke tools through `mise`, not from your path:

```bash
mise exec -- just test
```

`mise` is active in a person's shell and supplies the versions `.mise.toml`
declares. An agent's shell has no activation, so a bare `just` resolves to
whatever is installed globally, usually an older version.

The symptom is a check that fails here and passes in continuous integration, on
a file nobody edited. When that happens, establish which version ran before
treating the failure as real.

## Read the constitution first

Before starting work in a project, read its `.specify/memory/constitution.md`,
then the rest of `.specify/memory/`. That is where completed work is
consolidated, and it is more current than any prose written about it elsewhere.

Read `system/.specify/memory/` too when the work touches how repositories fit
together. A component's memory describes only its own behavior, so an agreement
between components is not in it and its absence there is not evidence the
agreement does not exist.

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

**Choose the project before writing anything.** @CONTRIBUTING.md gives the test
under "Where a change belongs". Guessing puts a design where nobody looks for
it, which is harder to notice than putting it nowhere.

**A merged spec is the authorization; a branch is not.** Wait for the spec PR to
merge before implementing against it.

## Writing memory

`.specify/memory/` is documentation, not a specification. `global/baseline` in
every constitution says what that means; two things bind mechanically:

**Run `unslop` over anything you write into `.specify/memory/` before committing
it.** It is a user skill and it applies to prose in this repository the way
`mdformat` applies to formatting. Em dashes are the tell it catches most often
here, and requirement prose survives conversion as bold labels restating the
line after them.

**Never carry feature scaffolding into memory.** No `FR-` labels in the body, no
`MUST`, no user stories, no acceptance scenarios, no success criteria, and no
per-paragraph source footer. Those belong to the feature that produced the
knowledge. Memory names the feature once, at the end.

The calibration is the architecture documentation this organization already
wrote: `osapi/docs/docs/sidebar/architecture/system-architecture.md` explains
why its liveness probe checks nothing, in one sentence, next to the liveness
probe, and then tells the reader what to use instead. Reason about the system,
stated once, beside the thing it explains. Nothing about the document.

## Commit trailer

When committing via Claude Code, end the message with:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
