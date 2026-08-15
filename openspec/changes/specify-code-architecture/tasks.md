## 1. Record the architecture

- [x] 1.1 Survey package layout, coverage targets, Go versions, and release
  tooling across the five Go repositories
- [x] 1.2 Write the `code-architecture` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Bring repositories into compliance

- [ ] 2.1 `gohai` — add `just::fmt` to `ready`, which CI checks and the recipe
  does not fix
- [ ] 2.2 `osapi-orchestrator` — same
- [x] 2.3 `osapi-orchestrator` — merge the pending action version bumps, which
  account for the workflow drift

Verification 3.1 failed: no repository declares a coverage target. The shared
`go.just` reports gaps but never exits non-zero, so coverage can fall without
any check failing.

All four measured libraries are already at 100% once `.coverignore` is applied,
so the target holds what exists rather than demanding new tests.

- [ ] 2.4 `osapi-justfiles` — add a `unit-cov-check` recipe to the `go` module
  that fails when total coverage is below `JUST_COVERAGE_TARGET` (default 100),
  reading the profile `unit-cov` already filtered
- [ ] 2.5 `osapi-justfiles` — comment the variable to name `codecov.yml` as the
  other declaration
- [ ] 2.6 All five Go repositories — add `codecov.yml` declaring the same
  target, commented to name `JUST_COVERAGE_TARGET`
- [ ] 2.7 All five — name the filtered profile explicitly in the codecov upload
  step, which currently passes no file and relies on auto-discovery
- [ ] 2.8 All five — add `unit-cov-check` to `test`, so CI and `just test` fail
  together
- [ ] 2.9 `osapi` — measure coverage; it was not measured with the others
- [ ] 2.10 All five — state in `CONTRIBUTING.md` that coverage is gated at 100%
  and name the recipe that checks it. The rule lives in the corpus; how to run
  it is contributor-facing
- [ ] 2.11 Confirm the check fails a build when coverage drops, rather than only
  reporting it

## 3. Verification

- [ ] 3.1 Confirm every Go repository declares the coverage target
- [ ] 3.6 Confirm both declarations state the same number
- [ ] 3.2 Confirm every repository publishing a binary configures goreleaser
- [ ] 3.3 Confirm no repository carries a top-level directory outside the
  documented set
- [ ] 3.4 Confirm `ready` addresses every check CI runs, in every repository
- [ ] 3.5 Confirm workflows of the same type differ only where the build
  requires it
