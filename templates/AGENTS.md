# AGENTS.md

Test: `just test` | Before you commit: `just ready`

<!-- The shared sections of every osapi-io AGENTS.md, in their order.
CONSTITUTION.md says how a repository uses them. A repository puts its own
sections between these. It does not rename, move or remove one. -->

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. It gives the prerequisites, the
setup, the code style, the test conventions and the pull request workflow. These
rules apply to agents and to people. This file has only the rules that are
specific to agents. They apply to each coding agent, for example Claude Code and
Codex.

## Running tools

Run tools through `mise`, not from your path:

```bash
mise exec -- just test
```

`mise` is active in the shell of a person. It supplies the versions that
`.mise.toml` declares. The shell of an agent does not activate `mise`. Thus a
bare `just` runs the version that is installed globally. That version is usually
older.

The symptom is a check that fails here but passes in CI, on a file that nobody
changed. If this occurs, find the version that ran. Do this before you accept
the failure as real.

## Where the rules come from

[CONTRIBUTING.md](CONTRIBUTING.md#before-you-start) names the design pages. If a
rule here and a design page do not agree, obey the design page. Say that they do
not agree. Do not use the code to decide.

## Commit trailer

When an agent commits, end the message with the trailer of its tool. A commit
from Claude Code ends with this text:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Another agent uses the trailer of its own tool, and the trailer names that tool.

## Task tracking

**The design is in the design pages.** Write or change the page in
[osapi-io/specs](https://github.com/osapi-io/specs) before you build. If the
build shows that the page is wrong, correct the page. A design page in this
repository becomes incorrect when the code changes. No check finds the
difference.
