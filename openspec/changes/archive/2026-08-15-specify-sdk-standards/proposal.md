## Why

`osapi` publishes a Go SDK at `pkg/sdk/client`. `osapi-orchestrator` is built on
it: every operation it exposes is an SDK call, and it pins the module by
version. The rules that make the SDK usable by a second repository are written
down in two places inside `osapi`, and both are documentation rather than
requirements:

- `CLAUDE.md` states that method names MUST be clean verbs and never repeat the
  service name.
- `docs/docs/sidebar/sdk/guidelines.md` states that no generated type may appear
  in a public signature, that every exported result field needs a JSON tag, and
  how errors are wrapped.

Both bind a consumer that cannot see them. `osapi-orchestrator` has no way to
discover the contract it depends on except by reading another repository's
contributor documentation, and nothing detects a change to that contract until
the consumer breaks.

The rules hold today. Verified against the code: no service method stutters, no
public signature exposes a `gen` type, no exported result field lacks a JSON
tag, and `osapi-orchestrator` never imports `gen`. That is what makes this a
recording rather than a correction.

## What Changes

- Add an `sdk-standards` capability recording what the SDK guarantees its
  consumers.
- Leave both source documents in place, pointing at the capability.

## Capabilities

### Added Capabilities

- `sdk-standards`: the contract between `pkg/sdk` and the repositories built on
  it — method naming, type exposure, result shape, and error handling.

## Impact

- `osapi`: `CLAUDE.md` and `sdk/guidelines.md` state the rules once and point at
  the capability for the rest.
- `osapi-orchestrator`: can read the contract it depends on without reading
  another repository's contributor documentation.
