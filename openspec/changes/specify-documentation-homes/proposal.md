## Why

Every repository has a `docs/` directory and no two are organised alike. `gohai`
has `collectors/` and two how-to guides; `osapi-orchestrator` has `operations/`,
`features/`, and `plans/`; `nats-client` has a single directory named after its
package; `osapi` publishes a Docusaurus site. None has an index telling a reader
what is there.

More importantly, one category of document is now in two places. `osapi` holds
70 planning documents and `osapi-orchestrator` holds 6 — design records
describing what was going to be built and why. That is what this repository's
change archive now holds. Two homes for the same kind of document means two
places to look and no way to know which is current.

Nothing records which documents belong where, so each repository answered it
differently.

## What Changes

- Establish the `documentation` capability, recording what a repository's
  `docs/` holds and what belongs in the specification corpus instead.
- Require `docs/` to carry an index, so a reader can find what is there.
- Record that design records belong in the corpus. Existing planning documents
  in repositories are historical and stay where they are; new ones are changes.

## Capabilities

### New Capabilities

- `documentation`: what a repository documents locally, what the corpus holds,
  and how a repository's documentation is organised.

### Modified Capabilities

None. The corpus-versus-repository boundary for *engineering guidance* is
already recorded in `code-architecture`; this covers documentation generally.

## Impact

- `gohai`, `nats-client`, `nats-server`, `osapi-orchestrator`, `osapi`: each
  needs a `docs/README.md` index.
- `osapi`, `osapi-orchestrator`: `docs/plans/` stops receiving new documents.
  The 76 existing ones remain as history.
- No document is moved. Reference material, how-to guides, and user-facing
  documentation stay where they are.
