## Why

An audit of every non-deprecated repository — files, directories, workflow and
recipe contents, and the claims made in documentation — found that documentation
describing tooling has drifted from what the tooling does, in the same way
documentation describing dependencies had.

`system-architecture` requires documented dependencies to match `go.mod`. The
same failure appears in tooling, planning, and generated artifacts, where no
requirement covers it:

- `nats-client` and `nats-server` document `golang/mock` as the mocking library.
  Their `go.mod` declares `go.uber.org/mock`, and their `deps` recipe installs
  the deprecated `golang/mock/mockgen` as a tool alongside it.
- `gohai` documents that "osapi uses the deprecated `golang/mock`". `osapi` uses
  `go.uber.org/mock`.
- `gohai` tells agents its plans live in `docs/superpowers/`. That directory
  does not exist, and neither does `docs/plans/`.
- `nats-client` and `nats-server` tell agents plans live in `docs/plans/`.
  Neither directory exists.
- `gohai` tracks `schemas/all-fields.txt`, an 803-row generated table that
  nothing in the repository references.

## What Changes

- Extend `system-architecture` so documentation describing tooling is held to
  the same standard as documentation describing dependencies.
- Correct the drifted claims and remove the orphaned artifact.
- Fix the `deps` recipes installing a deprecated tool.

## Capabilities

### Modified Capabilities

- `system-architecture`: the requirement covering documented relationships is
  broadened to cover tooling and directories, not only module dependencies.

## Impact

- `nats-client`, `nats-server`: `deps` recipe stops installing the deprecated
  mockgen; documentation names the library actually used.
- `gohai`: corrects its claim about `osapi`, points agents at a directory that
  exists, and drops the orphaned generated table.
- `osapi-orchestrator`: documents a mocking library or states it uses none.
