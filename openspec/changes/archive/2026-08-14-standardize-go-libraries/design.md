## Context

See proposal.md - Why.

Thirteen shared files were compared across `gohai`, `nats-client`,
`nats-server`, and `osapi-orchestrator`:

| File                                      | State                                   |
| ----------------------------------------- | --------------------------------------- |
| `.mise.toml`                              | identical                               |
| `.github/labeler.yml`                     | identical                               |
| `.github/delete-merged-branch-config.yml` | identical                               |
| `.github/workflows/*`                     | identical set, all ten                  |
| `.coverignore`                            | four variants — package paths differ    |
| `.goreleaser.yaml`                        | three variants — binary names differ    |
| `.github/dependabot.yml`                  | three variants — example modules differ |
| `.gitignore`                              | four variants                           |
| `justfile`                                | two variants                            |
| `.golangci.yml`                           | two variants                            |
| `.github/codecov.yml`                     | two variants                            |
| `LICENSE`                                 | three variants                          |
| `AI_POLICY.md`                            | four variants                           |
| `CODE_OF_CONDUCT.md`                      | present in two of four                  |

The last three are organization-wide policy and are handled in `repo-standards`,
not here.

Specific findings behind the requirements:

- `nats-client` and `nats-server` do not ignore `.worktrees/`; the other two do.
- `osapi-orchestrator` ignores `docs/bun.lock` while tracking it — the same
  inert rule already removed from `gohai` and `osapi`.
- `nats-*` exclude `**/mocks/*.go` from coverage; `gohai` and
  `osapi-orchestrator` do not.
- `gohai` and `osapi-orchestrator` have a `generate` recipe; `nats-*` do not.
- `osapi-orchestrator` is missing the `go reference` badge.
- `nats-client` alone sets `exclude-dirs: ./client` in `.golangci.yml`.

## Goals / Non-Goals

**Goals**

- A difference between two Go libraries is a decision someone recorded.
- A contributor moving between libraries finds the same commands and the same
  README shape.

**Non-Goals**

- CI workflows. They are already identical and need no requirement.
- Organization-wide boilerplate. That is `repo-standards`.
- Prescribing README prose beyond the badge row and the section structure
  already specified.

## Decisions

### Name the files permitted to vary, rather than only the ones that must match

A standard that lists what must match leaves every unlisted file ambiguous.
Naming the three files that may differ — and why — makes any other difference
answerable without a judgment call.

*Alternative considered:* require everything to match and grant exceptions as
they arise. `.coverignore` cannot match; it names packages that do not exist in
the other repositories. The exception list would grow immediately and
unrecorded.

### Require the mocks exclusion even where nothing is generated

Two libraries exclude generated mocks from coverage and two do not, which means
coverage numbers are not comparable between them. Requiring it everywhere makes
the number mean the same thing in each repository, and costs nothing where no
mocks exist.

*Alternative considered:* require it only where mocks exist. That is the current
state, and it is why the difference went unnoticed — each repository looked
locally correct.

### Require `generate` even where it does nothing

The value is that `just ready` behaves identically everywhere, so a contributor
does not have to check which recipes a given library defines. An empty recipe is
cheaper than a contributor discovering the difference by having their generated
code go stale.

*Alternative considered:* only where code is generated. That is the current
state, and it means `just ready` silently does less in two of four repositories.

### Allow lint directory exclusions, nothing else

`nats-client` excludes `./client` from linting. That is specific to its package
layout and cannot be shared. Everything else in `.golangci.yml` can be, and is.

*Alternative considered:* drop the exclusion for byte-identity. It exists for a
reason this audit did not establish, and removing it would turn a consistency
exercise into a lint change with unknown consequences.

## Risks / Trade-offs

- **A required file cannot be checked automatically.** Nothing detects a library
  drifting from the baseline. → The audit that produced this capability was
  manual and took a session; it should become a check.

- **`.golangci.yml` identity is asserted, not enforced.** Two repositories could
  diverge in a way that is not a directory exclusion. → Same mitigation.

- **`osapi-orchestrator` may not be a Go library.** Its type is an open question
  in `repo-standards`. → If it is reclassified, these requirements stop binding
  it, and its differences become that type's problem.

## Migration Plan

One pull request per library, each satisfying this capability and
`repo-standards` together so a repository is touched once:

1. `gohai` — `CODE_OF_CONDUCT.md`, mocks coverage exclusion.
2. `nats-client` — `.worktrees/`, `generate` recipe.
3. `nats-server` — `.worktrees/`, `generate` recipe.
4. `osapi-orchestrator` — `CODE_OF_CONDUCT.md`, `go reference` badge, mocks
   exclusion, stop ignoring `docs/bun.lock`.

## Open Questions

- Should a check enforce these, and where would it live? A shared workflow would
  need to read the specification, which nothing currently does.
- `osapi` is not a Go library but shares most of these files. Does it get its
  own capability, or inherit this one where it applies?
