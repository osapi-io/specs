## 1. Record the architecture

- [x] 1.1 Survey package layout, coverage targets, Go versions, and release
  tooling across the five Go repositories
- [x] 1.2 Write the `code-architecture` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Bring repositories into compliance

- [ ] 2.1 `gohai` — add `just::fmt` to `ready`, which CI checks and the recipe
  does not fix
- [ ] 2.2 `osapi-orchestrator` — same
- [ ] 2.3 `osapi-orchestrator` — merge the pending action version bumps, which
  account for the workflow drift

Verification 3.1 failed: no repository declares a coverage target. The shared
`go.just` reports gaps but never exits non-zero, so coverage can fall without
any check failing.

- [ ] 2.4 `osapi` — declare the 100% target in coverage configuration
- [ ] 2.5 `gohai` — same
- [ ] 2.6 `osapi-orchestrator` — same
- [ ] 2.7 `nats-client` — same
- [ ] 2.8 `nats-server` — same
- [ ] 2.9 Confirm the declared target fails a build when coverage drops, rather
  than only reporting it

## 3. Verification

- [ ] 3.1 Confirm every Go repository declares the coverage target
- [ ] 3.2 Confirm every repository publishing a binary configures goreleaser
- [ ] 3.3 Confirm no repository carries a top-level directory outside the
  documented set
- [ ] 3.4 Confirm `ready` addresses every check CI runs, in every repository
- [ ] 3.5 Confirm workflows of the same type differ only where the build
  requires it
