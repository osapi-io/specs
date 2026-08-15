## 1. Record the architecture

- [x] 1.1 Survey package layout, coverage targets, Go versions, and release
  tooling across the five Go repositories
- [x] 1.2 Write the `code-architecture` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Bring repositories into compliance

- [x] 2.1 `gohai` — add `just::fmt` to `ready`, which CI checks and the recipe
  does not fix
- [x] 2.2 `osapi-orchestrator` — same
- [x] 2.3 `osapi-orchestrator` — merge the pending action version bumps, which
  account for the workflow drift

Verification 3.1 failed: no repository declares a coverage target. The shared
`go.just` reports gaps but never exits non-zero, so coverage can fall without
any check failing.

All five repositories containing Go measure 100% once `.coverignore` is applied,
so the target holds what exists rather than demanding new tests.

- [x] 2.4 `osapi-justfiles` — add a `unit-cov-check` recipe to the `go` module
  that fails when total coverage is below `JUST_COVERAGE_TARGET` (default 100),
  reading the profile `unit-cov` already filtered
- [x] 2.5 `osapi-justfiles` — comment the variable to name `codecov.yml` as the
  other declaration
- [x] 2.6 All five Go repositories — declare the same target in the existing
  `.github/codecov.yml`, commented to name `JUST_COVERAGE_TARGET`. It already
  declared a patch target; it lacked a project target, so Codecov compared
  against the base commit rather than 100%
- [x] 2.6a All five — remove that file's `ignore:` list. It was byte-identical
  across all five while `.coverignore` differs per repository, so it named
  neither repository's real exclusions. Inert, because `.coverignore` strips
  those files before upload — `nats-client` has 400 such lines — but a second
  declaration of what is excluded
- [x] 2.6b All five — keep `threshold: 0.05%`. At 0% Codecov's own rounding
  fails the status on an artifact; the exact check is `unit-cov-check`
- [x] 2.7 All five — name the filtered profile explicitly in the codecov upload
  step, which passed no file and relied on auto-discovery
- [x] 2.8 `osapi-justfiles` — point `go::test` at `unit-cov-check` instead of
  `unit-cov`, so all five gate through one line and CI and `just test` fail
  together. Safe: all five measure 100% filtered
- [x] 2.9 `osapi` — measure coverage; it was not measured with the others. It is
  99.9359%, not 100%: 9 uncovered statements across 7 functions
- [x] 2.9a `osapi-justfiles` — keep reading `go tool cover -func`; its ~0.05%
  rounding is bounded, and a declared target below 100% makes it explicit
- [x] 2.9b `osapi` — declare a 99.9% target overriding the org-wide 100, so the
  current level cannot decay
- [x] 2.10 Archive `osapi-sdk`, which is deprecated but still consumes the `go`
  module and still runs `just go::test`. Do this before 2.8, or flipping the
  gate turns an unmaintained repository red
- [x] 2.11 All five — state in `CONTRIBUTING.md` that coverage is gated at 100%
  and name the recipe that checks it. The rule lives in the corpus; how to run
  it is contributor-facing
- [x] 2.12 Confirm the check fails a build when coverage drops, rather than only
  reporting it

## 3. Verification

- [x] 3.1 Confirm every Go repository declares the coverage target
- [ ] 3.6 Confirm both declarations state the same number. Fails: `osapi`
  declares 99.9% in `codecov.yml` but its justfile export never reaches the shim
  `go` module, so the effective local target is 100. Unblocked by
  `converge-justfile-consumption` task 1.2
- [x] 3.2 Confirm every repository publishing a binary configures goreleaser
- [x] 3.3 Confirm no repository carries a top-level directory outside the
  documented set
- [x] 3.4 Confirm `ready` addresses every check CI runs, in every repository
- [x] 3.5 Confirm workflows of the same type differ only where the build
  requires it
