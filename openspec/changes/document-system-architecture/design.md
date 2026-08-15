## Context

See proposal.md - Why.

The dependency graph as it actually exists:

```
osapi-orchestrator ──> github.com/retr0h/osapi/pkg/sdk/client   (pinned pseudo-version)
osapi ─────────────┬─> osapi-io/nats-client                     (pinned pseudo-version)
                   └─> osapi-io/nats-server                     (pinned pseudo-version)
gohai ─────────────>   nothing in this organization
```

No repository uses a `replace` directive. Module paths:

| Repository           | Declared module path                     | Matches location |
| -------------------- | ---------------------------------------- | ---------------- |
| `gohai`              | `github.com/osapi-io/gohai`              | yes              |
| `nats-client`        | `github.com/osapi-io/nats-client`        | yes              |
| `nats-server`        | `github.com/osapi-io/nats-server`        | yes              |
| `osapi-orchestrator` | `github.com/osapi-io/osapi-orchestrator` | yes              |
| `osapi`              | `github.com/retr0h/osapi`                | **no**           |

`osapi` moved into the organization without its module path following. The
repository at `github.com/osapi-io/osapi` exists, so `go get` against the
location a reader would try does not resolve.

## Goals / Non-Goals

**Goals**

- The dependency graph is written down, so a description of it can be checked
  rather than believed.
- A module resolves at the location it lives.

**Non-Goals**

- Changing how dependencies are versioned. Pinned pseudo-versions work.
- Creating dependencies that do not exist. `gohai` is not consumed by `osapi`
  today; this change records that rather than changing it.

## Decisions

### Name the capability `module-dependencies`

An earlier draft called it `system-architecture`. That name is already taken:
`osapi` publishes `docs/sidebar/architecture/system-architecture.md`, which maps
its packages, layers, and request path. This capability is about neither — it
covers Go module paths and how repositories declare dependencies on one another.

Two documents named for the same thing, describing different things, is how a
reader ends up reading the wrong one.

*Alternative considered:* keep the name and rename osapi's document. The
document is correct about its own subject, and it is published on a site with
existing links.

### Require module path to match repository location

`go get github.com/osapi-io/osapi` fails today. A reader who finds the
repository cannot import it by the path they found it at, and has to read
`go.mod` to discover the real one.

*Alternative considered:* leave it, since Go resolves whatever `go.mod` declares
and `osapi-orchestrator` already imports the working path. That accepts a
permanent trap for anyone who has not read `go.mod`, and the mismatch becomes
harder to fix as more consumers appear.

### Require documentation to match declared dependencies

Three documented relationships were wrong, and all three were plausible:
`replace` directives that had been removed, an embedding relationship that was
planned, and a consumer that never materialized. None was detectable without
reading `go.mod`.

*Alternative considered:* rely on review. The claims survived every review they
went through, because a reviewer checks whether prose reads correctly, not
whether it matches a manifest.

### Do not require a `replace` directive

The removed documentation described `replace` as the linking mechanism. It is
not, and requiring it would break builds for anyone without every sibling
repository cloned.

*Alternative considered:* require `replace` for local development, as the
documentation once implied. That is a developer convenience, not an
architecture, and it belongs in a repository's own contributing guide if it is
wanted at all.

## Risks / Trade-offs

- **The module rename touches roughly 1,180 files.** Mechanical, but it is a
  breaking change: `osapi-orchestrator` imports the current path in 53 files. →
  Sequenced below; `osapi` renames and publishes first.

- **Anything else importing `github.com/retr0h/osapi` breaks silently.** → Only
  `osapi-orchestrator` is known; a search outside the organization is worth
  doing before renaming.

- **Recording the graph makes it stale the moment it changes.** → The
  requirement is that documentation matches `go.mod`, not that the graph is
  copied into prose; the table above lives in this design document, which is
  archived rather than maintained.

## Migration Plan

1. `osapi` renames its module to `github.com/osapi-io/osapi` and updates its own
   imports — roughly 1,077 Go files plus 47 documentation and configuration
   references.
1. `osapi` merges and publishes, so the new path resolves.
1. `osapi-orchestrator` updates its `require` and its 53 importing files.
1. `gohai`'s README is corrected to describe the relationship it has rather than
   the one intended.

Rollback for step 1 is reverting the rename; consumers pinned to the old
pseudo-version continue to resolve until they move.

## Open Questions

- Is anything outside the organization importing `github.com/retr0h/osapi`? The
  rename breaks it without warning.
- Should `gohai` be consumed by `osapi`, as its README describes? That is a
  design question, not a documentation one, and is out of scope here.
