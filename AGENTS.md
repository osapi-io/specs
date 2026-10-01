# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read [CONTRIBUTING.md](CONTRIBUTING.md) first, then
[CONSTITUTION.md](CONSTITUTION.md). This file has only what is specific to
agents.

## Running tools

Invoke tools through `mise`, not from your path:

```bash
mise exec -- just test
```

`mise` is active in a person's shell and supplies the versions `.mise.toml`
declares. An agent's shell has no activation, so a bare `just` resolves to
whatever is installed globally, usually an older version. The symptom is a check
that fails here and passes in continuous integration, on a file nobody edited.

## Read the documents before changing them

Read the component's page under `components/` and the subjects it links. That is
the standing description of how the component behaves and it is more current
than any prose written about it elsewhere.

Read [ARCHITECTURE.md](ARCHITECTURE.md) when the work touches how repositories
fit together. A component's page describes only its own behaviour, so an
agreement between components is not in it and its absence there is not evidence
the agreement does not exist.

Nothing here authorizes work the constitution forbids. When you cannot satisfy
both a request and the constitution, say so rather than picking one silently.

## Writing a page

**Run `unslop` over anything you write.** It applies to prose here the way
`mdformat` applies to formatting. Em dashes are the tell it catches most often.

**Use `/document` rather than writing a page by hand.** It carries the voice,
places the subject, and runs `unslop`.

**Place content in the subject it belongs to.** A component's README is an
index: what the repository is, and a table linking its subjects. Something about
queuing work goes in the page about queuing work, merged with what is there
rather than appended after it.

## Commit trailer

When committing via Claude Code, end the message with:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
