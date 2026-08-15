## Context

See proposal.md - Why.

`go-library-standards` covers four repositories that could be compared against
each other. These four could not — each is the only one of its type — so nothing
surfaced their gaps.

| Repository        | Type          | `.github` contents                                    |
| ----------------- | ------------- | ----------------------------------------------------- |
| `osapi`           | Main product  | codecov, dependabot, labeler, repos.json              |
| `osapi-ui`        | UI            | **none — the directory does not exist**               |
| `osapi-justfiles` | Utility       | delete-merged-branch, dependabot, labeler, repos.json |
| `specs`           | Documentation | delete-merged-branch, dependabot, labeler, repos.json |

Findings:

- `osapi-ui` has no `.github` directory: no workflows, no dependabot, no
  labeler, no repository manifest. It is the only repository in the organization
  with no CI.
- `osapi` is missing `delete-merged-branch-config.yml`, which the other seven
  have.
- `osapi-justfiles` has no `.mise.toml`, though its recipes need `just` and
  `uv`. Required now by `repo-standards`.
- `osapi-justfiles` and `specs` already agree on `dependabot.yml` and
  `delete-merged-branch-config.yml`, and differ on `labeler.yml` only because
  they define different labels.

## Goals / Non-Goals

**Goals**

- Hold a one-of-a-kind repository to a standard, rather than to whatever it
  happened to be created with.
- Make the absence of CI a defect rather than a characteristic.

**Non-Goals**

- Building `osapi-ui`'s CI. That is real work — lint, build, and test for a
  front-end toolchain — and is tracked rather than performed here.
- Writing `osapi-ui`'s README content, which is 20 lines and documents nothing.
- Go library configuration, covered by `go-library-standards`.

## Decisions

### One capability for four types, not four capabilities

Each of these types has one repository. Four capabilities would each hold one or
two requirements, and the requirements they would hold are mostly the same:
every repository needs management files, every repository needs CI. What differs
is the toolchain, which is expressed as a condition inside a requirement rather
than as a separate capability.

*Alternative considered:* one capability per type, symmetrical with
`go-library-standards`. Symmetry is not worth four near-empty documents, and the
shared requirements would have to be repeated in each.

*Alternative considered:* fold everything into one configuration capability
covering all five types. Go libraries have enough specific requirements — badge
order, coverage exclusions, recipe surface — to stand alone, and mixing
toolchains in one document makes each harder to read.

### Require CI by outcome, not by workflow list

`osapi-ui` needs a front-end build; `specs` needs markdown formatting and
specification validation. Naming specific workflow files would specify something
false for one of them. The requirement is that checks run and what they must at
minimum cover.

*Alternative considered:* enumerate the required workflows, as is effectively
true for the Go libraries where all ten match. That works when repositories
share a toolchain and fails immediately here.

### State which toolchain files must be absent

The audit found the toolchain files each repository carries to be correct —
`osapi` has `.air.toml` and a compose file, `specs` has neither. Recording that
as a requirement makes a future stray file a defect, and stops a standardization
pass from copying Go configuration into a repository with no Go in it.

*Alternative considered:* say nothing about absence, only presence. A standard
that only adds files is how a documentation repository ends up with a
`.golangci.yml` nobody reads.

## Risks / Trade-offs

- **`osapi-ui` fails this standard the day it lands, and will for a while.** →
  Tracked as a task with the work named, rather than left as an unstated gap.

- **"CI appropriate to the toolchain" is not mechanically checkable.** → It is
  weaker than the Go library requirements deliberately; the alternative is a
  requirement that is precise and wrong for one of the four.

- **A one-of-a-kind repository has nothing to be compared against.** Adding a
  second UI repository would immediately surface differences this standard does
  not cover. → Expected; that is when the requirements get sharper.

## Migration Plan

1. `osapi` — add `delete-merged-branch-config.yml`.
2. `osapi-justfiles` — add `.mise.toml` pinning `just` and `uv`.
3. `osapi-ui` — create `.github` from scratch. Substantial, and last.

`specs` already conforms.

## Open Questions

- Does `osapi-ui` remain a separate repository? It is embedded into the `osapi`
  binary at build time, and its README documents nothing. If it is folded in,
  this standard stops applying to it.
- Should `repos.json` be required in `osapi-sdk`, which is deprecated but still
  exists and still drifts?
