# Agent skills

osapi carries the skill an agent needs to operate it, compiled into the binary,
and `osapi init` writes it into a repository. The skill is short on purpose: it
tells the agent to ask the binary, through `osapi help --json` and
`osapi behavior describe --json`, rather than carrying a copy of the docs that
would be wrong after the next release.

This page covers the skill for operating hosts. A skill for building a new
behavior lives in the osapi repository instead, because building one is a change
to osapi's code. That one is not written yet; it is in
[the pivot plan](pivot.md).

## Where the skill lives

The files are under `cmd/resources/skills/`, one directory per skill, and
`cmd/resources/resources.go` embeds them with `//go:embed skills`. `go:embed`
only reaches files inside its own package's directory, which is why the package
exists. The skill's source is in the repository next to the code it describes,
and a release ships exactly the skill that matches it.

```
cmd/resources/skills/osapi/
  SKILL.md                  rules and a routing table
  references/behaviors.md   reading describe --json and building a request
  references/targets.md     --target: a host, _any, _all, a label
  references/errors.md      the error codes and what to do about each
```

`SKILL.md` is what the tool loads when a request matches its description. The
references load only when the routing table sends the agent to one, so a session
pays for the part it uses.

## What the skill tells an agent

Four rules, in `SKILL.md`:

1. Run `osapi help <command> --json` before a command and
   `osapi behavior describe <behavior> <method> --json` before a request, rather
   than relying on memory.
2. Pass `--json` to every command, and match a failure on its `code`. Exit 2
   means the call was wrong and retrying will not help.
3. Read the target with `get` or `list` before an update or a delete.
4. Check each host's `status` in a result, because a command against many hosts
   succeeds when some of them fail, and `skipped` is neither.

They rely on [help as JSON](cli.md#help-as-json-for-agents), the
[error document](cli.md#errors-go-through-one-handler) and
[behavior describe](behaviors.md#inspecting-behaviors-from-the-cli). A change to
any of those is a change to what the skill says, in the same pull request.

## `osapi init`

```sh
osapi init                              # claude, in the current directory
osapi init --tool claude --tool codex   # both tools
osapi init ./ops-repo --json
```

For each tool it writes the skills to the directory the tool reads, and a short
section in the file the tool reads every session:

| `--tool` | Skills                  | Instructions |
| -------- | ----------------------- | ------------ |
| `claude` | `.claude/skills/osapi/` | `CLAUDE.md`  |
| `codex`  | `.agents/skills/osapi/` | `AGENTS.md`  |

The section sits between `<!-- osapi:begin -->` and `<!-- osapi:end -->`. It
names the version, says to use the skill, and repeats the first two rules.
`init` rewrites what is between the markers and nothing else, and appends the
section when there are no markers, so the repository's own instructions survive
every run.

Running `init` again is the upgrade. Each file is reported as `created`,
`updated`, `unchanged` or `removed`. A file inside osapi's own skill directory
that this version no longer ships is removed, so a renamed reference does not
linger with stale advice. Other skills in the same tools directory are not
osapi's and are not touched.

`init` needs no config file and no controller. The installer is
`internal/skills`, and it writes through the same filesystem abstraction as the
rest of the CLI, so its tests run against memory.

## What will surprise somebody

**The skill and the binary can disagree on another machine.** The skill in a
repository is the one the `osapi` that last ran `init` shipped. An agent running
a newer `osapi` reads older advice until somebody runs `init` again. The section
in `CLAUDE.md` names the version it was written for, which is the only signal.

**Codex reads `.agents/skills`, not `.codex/`.** That is the path the shared
agent-skills layout uses, and the one swamp writes for Codex as well.
