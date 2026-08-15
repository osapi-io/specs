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
