# Agent skills

osapi carries the skill an agent needs to operate it, compiled into the binary,
and `osapi init` writes it into a repository. The skill is short on purpose: it
tells the agent to ask the binary, through `osapi help --json` and
`osapi behavior get --json`, rather than carrying a copy of the docs that would
be wrong after the next release.

This page covers the skill for operating hosts. A skill for building a new
behavior lives in the osapi repository instead, because building one is a change
to osapi's code. That one is not written yet; it is in
[the migration plan](behavior-migration.md).

## Where the skill lives

The files are under `cmd/resources/skills/`, one directory per skill, and
`cmd/resources/resources.go` embeds them with `//go:embed skills`. `go:embed`
only reaches files inside its own package's directory, which is why the package
exists. The skill's source is in the repository next to the code it describes,
and a release ships exactly the skill that matches it.

Two skills, because the requests that trigger them differ. `osapi` changes hosts
through osapi; `osapi-operations` runs osapi itself. A request to start the
controller should not load the guide to sysctl, and the other way round.

```
cmd/resources/skills/osapi/
  SKILL.md                  rules and a routing table
  references/behaviors.md   reading behavior get --json and building a request
  references/targets.md     --target: a host, _any, _all, a label
  references/errors.md      the error codes and what to do about each

cmd/resources/skills/osapi-operations/
  SKILL.md                  rules and a routing table
  references/components.md  the NATS server, controller and agent, together or apart
  references/config.md      config list, get and validate; precedence; required keys
  references/tokens.md      generating and checking tokens; unauthorized versus forbidden
  references/health.md      health, agent list, a missing host, a stuck job
```

`SKILL.md` opens with YAML frontmatter, `name` and `description`, which is how
the tool decides to load it. `cmd/resources/resources_public_test.go` fails a
skill without it, and `md_extra_excludes` keeps mdformat out of the directory:
mdformat rewrote the frontmatter into a heading once, and the installed skill
silently never loaded.

A third skill is for changing osapi rather than using it, so it is not embedded:
`.claude/skills/build-a-behavior/` in the osapi repository, loaded by a session
working in a checkout. `.agents/skills` there links to `.claude/skills`, so a
Codex session in the checkout loads it too. It routes to the sources that cannot
drift rather than restating them: `go doc ./internal/behavior` for the
definition's options, `osapi behavior new` for the layout, `behavior get` and
`validate` for what registered, and `internal/behaviors/sysctl` as the
reference. What it adds is the decisions to settle with the user before writing
anything, the order of the work, the examples-as-tests rule, the parity row when
migrating a domain, what each test failure means, and what the platform cannot
express yet.

The decisions come first because each one is a declaration someone will depend
on: whether something close exists already, whether the behavior is served or
internal, which platforms it runs on, whether it requires an internal behavior
or should split one out under the rule of two, what is an input and what is a
setting, what runs with sudo or is a secret, and whether the request is a
workflow across hosts, which belongs to osapi-orchestrator. The skill asks only
what the request leaves open, recommends an answer to each, and has defaults for
a user with no opinion.

The skill is procedure and judgment, not a catalog. The platform describes
itself, so the skill sends an agent to `behavior list`, `behavior get` and
`go doc` for what every behavior, building block and option is, and to believe
them over the skill. A capability that is not there is a gap the agent reports,
not one the skill lists ahead of time: the `apptoken` eval found that
`managedfile` could not set a file's owner, and once it could, `behavior get`
said so with no change to the skill. The one catalog it keeps is the short list
of what cannot be expressed yet, because finding those by building costs a
session, and it shrinks as `behavior validate` learns to say them.

The skill is self-contained: what an agent needs beyond the code and the CLI is
in its own `references/`, loaded only when a step sends it there, rather than in
the docs site, which can move or drift without the skill noticing.
`references/services.md` covers how a behavior uses the platform: each service a
provider gets (filesystem, commands, files osapi owns, secrets, settings), how
the fake host stands in for it in tests, which provider to copy for each kind of
state, and the input checks the probes enforce. `references/migrating.md` has
the steps for moving a hand-written domain: move the provider and its tests
unchanged, wrap them, and account for every hand-written handler test case
before the cutover deletes it. The docs site links to these files rather than
keeping a copy. `SKILL.md` adds the questions that pick the pattern, such as
where the truth about the thing lives and what "already done" looks like.

The "Not yet" list names what a behavior cannot express, such as an action
method like `restart` or a resource with two keys, so an agent asked for one
says so and stops rather than wiring around the platform. It is the same list as
[the migration plan](behavior-migration.md)'s blockers, and shrinks as they are
built.

`evals/` holds the requests the skill is measured on and `run.sh`, which runs
each in a fresh session and checks the result with commands rather than by
reading it.

`SKILL.md` is what the tool loads when a request matches its description. The
references load only when the routing table sends the agent to one, so a session
pays for the part it uses.

## What the skill tells an agent

Four rules, in `SKILL.md`:

1. Run `osapi help <command> --json` before a command and
   `osapi behavior get --name <behavior> --method <method> --json` before a
   request, rather than relying on memory.
2. Pass `--json` to every command, and match a failure on its `code`. Exit 2
   means the call was wrong and retrying will not help.
3. Read the target with `get` or `list` before an update or a delete.
4. Check each host's `status` in a result, because a command against many hosts
   succeeds when some of them fail, and `skipped` is neither.

`osapi-operations` has its own five: ask the binary (`help --json`,
`config list --json`), run `config validate` before starting, read the config in
effect rather than the file because the environment wins, never print a secret,
and pass `--json`. They rely on the
[config commands](configuration.md#the-binary-describes-its-own-settings).

The `osapi` skill's rules rely on
[help as JSON](cli.md#help-as-json-for-agents), the
[error document](cli.md#errors-go-through-one-handler) and
[behavior get](behaviors.md#inspecting-behaviors-from-the-cli). A change to any
of those is a change to what the skill says, in the same pull request.

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
