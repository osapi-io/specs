## Context

See proposal.md - Why.

A survey of the nine active repositories found:

| Item                                                            | Present in                                   |
| --------------------------------------------------------------- | -------------------------------------------- |
| `README.md`, `LICENSE`, `AI_POLICY.md`, `CLAUDE.md`, `justfile` | 9 of 9                                       |
| `docs/contributing.md`                                          | 8 of 9 (`specs` uses root `CONTRIBUTING.md`) |
| `CODE_OF_CONDUCT.md`                                            | 5 of 9                                       |
| `AGENTS.md`                                                     | 1 of 9 (`specs`)                             |

README length ranges from 20 lines to 321. Only `## 📄 License` appears in all
nine. `📦 Install` and `📦 Usage` are used for the same purpose in different
repositories, as are `🎯 Usage` and `📋 Examples`.

The `AGENTS.md` split is already established outside this organization, in
`stack`, `meshx`, `foo`, `mlb-sdk`, and `mlb-mcp`.

## Goals / Non-Goals

**Goals**

- A new repository can be created by following the standard rather than
  imitating an arbitrary existing one.
- Repositories of the same kind read alike, so a reader who knows one knows
  where to look in another.
- One location for contributing documentation, so guidance cannot drift between
  two files.

**Non-Goals**

- CI workflows, coverage configuration, and justfile recipe surface. They have
  drifted too, but they are a separate subject.
- Rewriting README prose. This change standardizes structure, not content.
- Reviving deprecated repositories.

## Decisions

### Classify by type rather than standardize one README

A Go library's README answers "how do I import this and what does it do." A
documentation repository's answers "what is this for and how do I work in it."
Forcing both into one section list produces empty sections in one and missing
ones in the other.

Types are drawn from what the repositories already are, not invented: four Go
libraries converge on the same shape, `osapi` is the product, `osapi-justfiles`
distributes assets, `specs` holds records.

*Alternative considered:* one universal README structure with optional sections.
Optional sections are how the current drift happened — `📦 Install` and `📦 Usage`
both exist because nothing said which to use when.

*Alternative considered:* no README standard at all, only the file list. The
survey shows the file list is the smaller problem; a 20-line README and a
321-line one both technically have a README.

### Fix the section vocabulary, not just the set

The observed drift is not repositories omitting sections — it is repositories
naming the same section differently. A fixed vocabulary with fixed emoji makes
the same content findable in the same place across repositories, and makes
non-compliance mechanically detectable.

*Alternative considered:* specify sections without emoji, treating them as
decoration. The emoji are already universal in this organization and act as
visual anchors when scanning; leaving them unspecified would invite a second
axis of drift.

### Root CONTRIBUTING.md over docs/

Eight repositories split contributing guidance across `docs/contributing.md` and
`docs/development.md`, and the boundary between them is not observable — both
describe setup and conventions. Consolidating removes the question of which file
a given instruction belongs in.

The root location is also what GitHub recognizes: it links `CONTRIBUTING.md`
from the new issue and pull request pages, which a file under `docs/` does not
get.

*Alternative considered:* keep the split, since eight of nine repositories
already do it. That is the larger group, but the split's boundary was already
unclear, and consolidating is a mechanical move rather than a rewrite.

*Alternative considered:* root `CONTRIBUTING.md` plus a separate root
`DEVELOPMENT.md`. `DEVELOPMENT.md` has no special standing with GitHub and
preserves the boundary problem in a new location.

### AGENTS.md with CLAUDE.md as a pointer

Agent guidance in a Claude-specific filename means adopting any other tool
requires either duplicating the file or renaming it across every repository. The
split is already proven in five repositories outside this organization.

*Alternative considered:* keep `CLAUDE.md` as the substantive file, since it is
what all nine repositories use today. It works only while one tool is used, and
the cost of changing later is the same migration, just deferred.

### Exempt the main product's README

`osapi` is the organization's landing page. Its README links sister projects and
orients a reader arriving at the organization, rather than describing a
consumable artifact. Forcing `Install` and `Features` onto it would misdescribe
what it is.

*Alternative considered:* bind it like everything else, for a rule with no
exceptions. A rule that requires rewriting the product's front page to satisfy a
consistency argument is optimizing the wrong thing.

### Record the classification in the spec, not the proposal

The type definitions alone do not tell anyone what type a given repository is.
Naming the repositories only in the proposal would leave the corpus saying
"every repository SHALL be one of four types" while the answer for any specific
repository lived in an archived document nobody reads to settle a question.

The classification is therefore a requirement. It goes stale when a repository
is added, and that staleness is the point — adding one becomes a change to this
capability rather than a judgment call.

*Alternative considered:* derive the type from the repository's contents. Two of
the four types are indistinguishable by contents — `osapi-justfiles` and `specs`
both hold markdown and a justfile — and `osapi` is a Go repository that is
deliberately not a Go library.

### Fix the CONTRIBUTING section names, not its whole shape

Converting the first repository produced two sections with the same purpose
under different names: `Before committing` in one repository and
`Finishing a change` in the other. That is the same drift the README vocabulary
requirement exists to prevent, reproduced one file over, because the standard
covered READMEs and stopped there.

The fix is a fixed opening and closing, with a free middle. The opening and
closing are the same questions for every repository — what do I install, what do
I run, how do I name a branch. The middle is where repositories genuinely
differ.

*Alternative considered:* prescribe the whole document. A `specs` contributor
needs the change workflow explained; an `osapi-justfiles` contributor needs
recipe conventions. Neither section belongs in the other repository.

*Alternative considered:* leave `CONTRIBUTING.md` unstructured, since its
content varies. That is what produced the drift being fixed.

### Leave AGENTS.md unstructured, deliberately

The two `AGENTS.md` files written so far share no headings, and that is correct:
one documents a planning boundary, the other warns that a shared recipe cannot
be tested locally. Neither applies to the other repository.

Stating explicitly that no structure is required makes this a decision rather
than an oversight, and stops a future reader from "fixing" it.

*Alternative considered:* require the same skeleton as `CONTRIBUTING`. It would
produce empty sections in every repository, which is how sections come to be
filled with filler.

## Risks / Trade-offs

- **Eight repositories change at once, or drift while converting.** → Convert
  one repository per change, starting with `osapi-justfiles`, so a partial
  rollout is visible rather than silent.

- **Inbound links to `docs/contributing.md` break.** Other repositories,
  READMEs, and `CLAUDE.md` files reference those paths. → Each conversion
  updates the links in its own repository; cross-repository references are
  checked as part of the final sweep.

- **A fixed vocabulary can be wrong for a repository nobody anticipated.** →
  Types are extensible; adding one is a change to this capability rather than an
  exception buried in a README.

- **The classification goes stale silently.** A repository added without a
  change to this capability is unclassified, and nothing detects it. → Worth a
  check that every repository in the organization appears in the table.

- **`osapi-ui` and `osapi-sdk` are effectively undocumented.** Both have 20-line
  READMEs. → `osapi-sdk` is deprecated and out of scope; `osapi-ui` needs
  content written, which this change does not do.

## Migration Plan

1. Convert `osapi-justfiles` first: consolidate `docs/contributing.md` and
   `docs/development.md` into root `CONTRIBUTING.md`, add `AGENTS.md`, reduce
   `CLAUDE.md` to a pointer, add the missing `.mise.toml`.
1. Convert the remaining repositories one at a time, in whatever order suits the
   work already happening in them.
1. Apply the README structure per type as each repository is converted.

`specs` already conforms and is the reference for the file layout. Rollback for
any repository is restoring the previous files from history.

## Open Questions

- Should `osapi-orchestrator` be a Go library or its own type? It is a Go
  package but its README documents targeting and operations more than an API,
  which is why it grew sections the library set does not have.
- Should the standard require `.mise.toml`? Eight of nine have it and
  `osapi-justfiles` does not, but it was not included in the file list because
  toolchain pinning is arguably part of the out-of-scope tooling subject.

### Pin tools whose output a check compares

`specs` and `osapi-justfiles` float `just`, `uv`, and `bun`. The language
runtimes are pinned — `go = "1.25"`, `node = "22"` — so the inconsistency is not
a policy, it is that runtimes felt like versions and tools felt like utilities.

`just` 1.45.0 reformats the committed justfile, so `just test` fails on `main`
locally. Nothing was committed to cause it. The check compares committed bytes
against generated bytes, which makes the generator an input to the check, and an
input to a check has to be a tracked version.

CI is green on the same commit. That is not reassurance — it is the second half
of the problem. No workflow in any of the seven repositories uses mise; every
one installs `just` with an unversioned `extractions/setup-just`, `bun` with
`oven-sh/setup-bun`, and Go and Node with their setup actions. So a repository
declares its toolchain twice, in two files that nothing reconciles, and right
now they disagree: the version a contributor gets from `mise install` fails a
check that the version CI gets still passes.

Pinning only `.mise.toml` would therefore have fixed nothing in CI, and would
have left the local-versus-CI split in place. The requirement binds every
provisioning path for that reason.

The rule is scoped to tools whose output is compared, rather than every tool. A
provisioner that floats cannot invalidate a committed file.

*Alternative considered:* pin everything. It adds Dependabot traffic for tools
where an upgrade cannot break a check.

*Alternative considered:* stop running formatters in check mode. That gives up
the guarantee that formatting is uniform, to avoid maintaining one pin.

### Archive a repository, do not only deprecate it

Three repositories are outside this capability, and none is archived on GitHub.
Two say "Deprecated" at the top of their README; `osapi-io-taskfiles` says
nothing, though no repository consumes it and the organization moved to just.

An unarchived repository accepts issues, pull requests, and pushes, and appears
in the organization listing indistinguishable from a maintained one. The README
notice only reaches someone who already opened it.

`osapi-io-taskfiles` should also name `osapi-justfiles`, because a reader who
arrives at a superseded repository needs to be sent somewhere, not just warned.

*Alternative considered:* delete them. Archiving keeps the history and the
inbound links working, at no cost.

### A modified fetched file is an override, not a stray

`osapi` tracked `.just/remote/react.mod.just`, a path that looks exactly like a
fetched artifact, and it was removed on that basis. The build broke: the module
is a three-line shim whose only content is a working directory, upstream points
it at the repository root, and `osapi`'s React application lives in `ui/`. Its
first line said so — "Local override: run react recipes in the ui/ directory."

The rule this change states is right; the evidence for applying it was the path
rather than the content. A committed copy that differs from what the fetch
returns is a fork someone made deliberately, and removing it removes the reason
it was committed.

It is still a defect. It is a different defect: a shared module carrying a value
that varies per consumer, which forces the consumer to fork the file to change
one string. The fix is for the module to take the directory as configuration —
which `converge-justfile-consumption` already requires — after which there is
nothing to override and nothing to track.

*Alternative considered:* have the fetch write the override after downloading.
That keeps a per-repository value in a fetch recipe instead of a tracked file,
and still leaves the module unable to serve a consumer with a different layout.

### The task runner is a tool like any other

Five repositories run every check through `just` and none declares it in
`.mise.toml`: `osapi`, `gohai`, `osapi-orchestrator`, `nats-client`,
`nats-server`. `specs` and `osapi-justfiles` do, and they are the two that never
diverged from continuous integration.

Where it is undeclared, `mise` has nothing to resolve and the shell falls
through to whatever is installed — Homebrew's 1.45.0 here. Continuous
integration installs its own through a setup action. The two are not the same
version, and they disagree about formatting: 1.45 writes a boolean setting as
`set allow-duplicate-variables := true`, a newer one writes
`set allow-duplicate-variables`, and each rejects the other's form. A justfile
formatted locally then fails the check in continuous integration, on a file
nobody touched.

This was diagnosed twice as a policy question — whether to pin versions or float
them — before the actual cause turned out to be that the tool was never declared
at all. Pinning a version in a file that does not mention the tool would have
changed nothing.

*Alternative considered:* leave it undeclared and require developers to install
a matching version. It is a convention with nothing enforcing it, and the
failure it produces looks like a formatting error rather than a version
mismatch.
