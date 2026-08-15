## Context

See proposal.md - Why.

Findings from auditing files, directories, workflow bodies, recipe bodies, and
documented claims across every non-deprecated repository.

**Tooling documentation against reality**

| Repository           | Documentation says                        | Reality                             |
| -------------------- | ----------------------------------------- | ----------------------------------- |
| `nats-client`        | `golang/mock`                             | `go.mod`: `go.uber.org/mock v0.6.0` |
| `nats-server`        | `golang/mock`                             | `go.mod`: `go.uber.org/mock v0.6.0` |
| `gohai`              | "osapi uses the deprecated `golang/mock`" | `osapi` uses `go.uber.org/mock`     |
| `osapi-orchestrator` | nothing                                   | no mocking library                  |

`nats-client` and `nats-server` go further than stale prose: their `deps` recipe
runs `go get -tool github.com/golang/mock/mockgen` while `go.mod` declares
`go.uber.org/mock/mockgen`. Running `just deps` adds a deprecated tool
dependency.

**Documented directories against reality**

| Repository           | Tells agents plans live in | Exists                              |
| -------------------- | -------------------------- | ----------------------------------- |
| `gohai`              | `docs/superpowers/`        | no                                  |
| `nats-client`        | `docs/plans/`              | no                                  |
| `nats-server`        | `docs/plans/`              | no                                  |
| `osapi-orchestrator` | `docs/plans/`              | yes, 6 documents                    |
| `osapi`              | —                          | `docs/plans/`, 70 documents, 1.2 MB |

**Orphaned artifact**

`gohai/schemas/all-fields.txt` is an 803-row pipe-delimited table of collector
fields. Nothing in the repository references it — no Go file, no recipe, no
document.

## Goals / Non-Goals

**Goals**

- Documentation that names a tool, library, or directory names one that is
  actually there.
- `just deps` stops installing a deprecated tool.

**Non-Goals**

- Choosing a mocking library. Four repositories already use `go.uber.org/mock`;
  this records that rather than deciding it.
- Deciding what happens to the 70 planning documents in `osapi`. That is a
  question about where design history lives now that this repository exists, and
  it deserves its own change.

## Decisions

### Extend the existing requirement rather than add a new one

`system-architecture` already requires documented dependencies to match
`go.mod`. Tooling, directories, and libraries are the same failure with a
different object: a claim nothing checks, which drifts because nothing breaks
when it does.

*Alternative considered:* a separate capability for documentation accuracy. The
distinction between "documented dependency" and "documented tool" is not one a
reader would look for.

### Prohibit describing another repository's tooling

`gohai` states which mocking library `osapi` uses. Nothing updates that when
`osapi` changes, and nothing did — `osapi` migrated and the claim stayed.

*Alternative considered:* allow it with a requirement to keep it current.
Nothing can enforce that from the other repository, which is why it drifted.

### Do not decide the mocking library here

Four repositories use `go.uber.org/mock`; `osapi-orchestrator` uses none and
needs none. Recording what is already true is enough. Whether the fifth should
adopt one is a question for whoever adds its first mock.

## Risks / Trade-offs

- **Removing `all-fields.txt` may remove something someone uses outside the
  repository.** Nothing inside references it. → It is generated from the
  collectors; regenerating is possible if a consumer appears.

- **The `deps` fix changes what a tool installs.** A contributor with the
  deprecated mockgen already installed will not notice. → Both mockgen binaries
  generate compatible output; the tool declaration in `go.mod` is what governs.

## Migration Plan

1. `nats-client`, `nats-server` — `deps` installs `go.uber.org/mock/mockgen`;
   documentation names it.
1. `gohai` — remove the claim about `osapi`, point plans at a directory that
   exists or drop the reference, remove `schemas/all-fields.txt`.
1. `nats-client`, `nats-server` — point plans at a directory that exists or drop
   the reference.
1. `osapi-orchestrator` — state that it uses no mocking library, or adopt one.

## Open Questions

- What happens to `osapi`'s 70 planning documents and `osapi-orchestrator`'s 6
  now that design history lives in this repository's archive? Keeping both is
  two places to look for the same thing.
- Should `docs/` have a required shape? `gohai` has `collectors/`,
  `osapi-orchestrator` has `operations/` and `features/`, `nats-*` have a single
  directory named after the package, `osapi` has a Docusaurus site. None has a
  `docs/README.md` index.
