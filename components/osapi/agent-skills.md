# Agent skills

The osapi binary has the skills that an agent needs to operate osapi.
`osapi init` writes them into a repository. The skills are short on purpose.
They tell the agent to ask the binary, through `osapi help --json` and
`osapi behavior get --json`. They do not have a copy of the docs, because a copy
is incorrect after the next release.

This page covers the skills that operate hosts and osapi. The skill that builds
a new behavior is in the osapi repository, because a new behavior is a change to
the code of osapi. It is described below.

## Where the skill lives

The files are under `internal/skills/resources/skills/`, with one directory for
each skill. `internal/skills/resources.go` embeds them with
`//go:embed resources/skills resources/dev-skills`. `go:embed` gets only files
in the directory of its own package. Thus the files are in `resources/` of the
package that reads them. The osapi CONTRIBUTING states this rule for each
embedded file. The source of the skill is in the repository next to the code
that it describes. Thus a release ships exactly the skill that matches it.

There are two skills, because different requests start them. `osapi` changes
hosts through osapi. `osapi-operations` runs osapi itself. A request to start
the controller must not load the sysctl guide, and the opposite is also true.

```
internal/skills/resources/skills/osapi/
  SKILL.md                  rules and a routing table
  references/behaviors.md   reading behavior get --json and building a request
  references/targets.md     --target: a host, _any, _all, a label
  references/errors.md      the error codes and what to do about each

internal/skills/resources/skills/osapi-operations/
  SKILL.md                  rules and a routing table
  references/components.md  the NATS server, controller and agent, together or apart
  references/config.md      config list, get and validate; precedence; required keys
  references/tokens.md      generating and checking tokens; unauthorized versus forbidden
  references/health.md      health, agent list, a missing host, a stuck job
```

`SKILL.md` starts with YAML frontmatter, `name` and `description`. The tool uses
it to decide if it loads the skill. `internal/skills/resources_public_test.go`
fails a skill without it. `md_extra_excludes` keeps mdformat out of the
directory. One time, mdformat changed the frontmatter into a heading, and the
installed skill never loaded. Nothing reported it.

### The skill that builds a behavior

A third skill changes osapi. The binary also has it, in
`internal/skills/resources/dev-skills/build-a-behavior/`. The binary is the only
source of the skill. No repository keeps a copy.

`osapi init` does not install it, because only a checkout of osapi can build a
behavior. `osapi skill` serves each embedded skill:

```sh
osapi skill list                                         # each embedded skill
osapi skill get --name build-a-behavior                  # its SKILL.md
osapi skill get --name build-a-behavior --reference references/services.md
```

The osapi repository has a short pointer at
`.claude/skills/build-a-behavior/SKILL.md`. It has the frontmatter of the skill,
so that agents find it. Its body tells the agent to run
`go run . skill get --name build-a-behavior` and obey the output. It has no
rules of its own, so it cannot become different from the skill. `.agents/skills`
is a link to `.claude/skills`, so each coding agent in the checkout finds the
pointer.

It sends the agent to the sources that cannot become incorrect. It does not copy
them:

- `go doc ./internal/behavior` for the options of the definition
- `osapi behavior create` for the layout
- `behavior get` and `validate` for what registered
- `internal/behaviors/sysctl` as the reference

It adds these things:

- the decisions to make with the user before any code
- the order of the work
- the rule that examples are tests
- the cutover of a domain, in one change
- what each test failure means
- what the platform cannot express yet

The decisions come first, because each one is a declaration that other code will
use:

- if a close behavior already exists
- if the behavior is served or internal
- which platforms it runs on
- if it requires an internal behavior, or must split one out under the rule of
  two
- what is an input and what is a setting
- what runs with sudo, and what is a secret
- if the request is a workflow across hosts, which belongs to osapi-orchestrator

The skill asks only what the request does not tell. It recommends an answer to
each question. It has defaults for a user with no preference.

The skill gives a procedure and decisions. It is not a catalog. The platform
describes itself. Thus the skill sends an agent to `behavior list`,
`behavior get` and `go doc` to learn what each behavior, building block and
option is, and to believe them over the skill.

If a capability is not there, the agent reports the gap. The skill does not list
gaps before they occur. For example, the `apptoken` eval found that
`managedfile` could not set the owner of a file. After the fix, `behavior get`
showed the new capability, and the skill did not change.

The skill keeps one catalog: the short list of what the platform cannot express
yet. A session that finds these by trial loses its time. The list becomes
shorter when `behavior validate` learns to report them.

The skill is complete in itself. What an agent needs, other than the code and
the CLI, is in its own `references/`. The agent loads a reference only when a
step sends it there. The docs site can move or change, and the skill does not
see that. Thus the skill does not depend on the site.

- `references/services.md` tells how a behavior uses the platform. It covers
  each service that a provider gets (filesystem, commands, files that osapi
  owns, secrets and settings), how the fake host replaces it in tests, which
  provider to copy for each kind of state, and the input checks that the probes
  enforce.
- `references/migrating.md` has the steps to move a hand-written domain. Move
  the provider and its tests without changes. Wrap them. Find a replacement for
  each hand-written handler test case before the cutover deletes it.

The docs site links to these files and does not keep a copy. `SKILL.md` adds the
questions that select the pattern. Examples are: where is the truth about the
thing, and what does "already done" look like.

The "Not yet" list names what a behavior cannot express. Examples are an action
method like `restart`, or a resource with two keys. When an agent gets a request
for one, it says so and stops. It does not add code around the platform. This
list is the same as the blockers in [the migration plan](behavior-migration.md),
and it becomes shorter as people build them.

`test/skills/build-a-behavior/` has the requests that measure the skill, and
`run.sh`. They test the skill, so they are not part of it, and the binary does
not have them. `run.sh` runs each request in a new session and checks the result
with commands. Nobody reads the result to check it.

The tool loads `SKILL.md` when a request matches its description. A reference
loads only when the routing table sends the agent to it. Thus a session pays
only for the part that it uses.

## What the skill tells an agent

`SKILL.md` has four rules:

1. Run `osapi help <command> --json` before a command, and
   `osapi behavior method get --name <behavior> --method <method> --json` before
   a request. Do not use memory.
2. Give `--json` to each command, and match a failure on its `code`. Exit 2
   means that the call was incorrect, and a second try does not help.
3. Read the target with `get` or `list` before an update or a delete.
4. Check the `status` of each host in a result. A command against many hosts
   succeeds when some of them fail, and `skipped` is neither.

`osapi-operations` has its own five rules:

1. Ask the binary (`help --json`, `config list --json`).
2. Run `config validate` before you start a component.
3. Read the config in effect, not the file, because the environment has
   precedence.
4. Never print a secret.
5. Give `--json`.

They use the
[config commands](configuration.md#the-binary-describes-its-own-settings).

The rules of the `osapi` skill use
[help as JSON](cli.md#help-as-json-for-agents), the
[error document](cli.md#errors-go-through-one-handler) and
[behavior get](behaviors.md#inspecting-behaviors-from-the-cli). A change to any
of those is a change to what the skill says. Make the two changes in the same
pull request.

## `osapi init`

```sh
osapi init                              # claude, in the current directory
osapi init --tool claude --tool codex   # both tools
osapi init --path ./ops-repo --json
```

For each tool, it writes the skills to the directory that the tool reads. It
also writes a short section in the file that the tool reads in each session:

| `--tool` | Skills                  | Instructions |
| -------- | ----------------------- | ------------ |
| `claude` | `.claude/skills/osapi/` | `CLAUDE.md`  |
| `codex`  | `.agents/skills/osapi/` | `AGENTS.md`  |

The section is between `<!-- osapi:begin -->` and `<!-- osapi:end -->`. It names
the version, tells the agent to use the skill, and gives the first two rules
again. `init` writes again only what is between the markers. When there are no
markers, it adds the section at the end. Thus the instructions of the repository
stay after each run.

A second run of `init` is the upgrade. It reports each file as `created`,
`updated`, `unchanged` or `removed`. It removes a file in the skill directory of
osapi that this version does not ship. Thus a renamed reference with old advice
does not stay. Other skills in the same directory do not belong to osapi, and
`init` does not touch them.

`init` needs no config file and no controller. The installer is
`internal/skills`. It writes through the same filesystem abstraction as the rest
of the CLI, so its tests run in memory.

## What will surprise somebody

**The skill and the binary can be different on a different machine.** The skill
in a repository comes from the `osapi` that last ran `init`. An agent that runs
a newer `osapi` reads older advice until somebody runs `init` again. The section
in the instructions file names the version that wrote it. That is the only
signal.

**Codex reads `.agents/skills`, not `.codex/`.** That is the path of the shared
agent-skills layout. swamp also writes it for Codex.
