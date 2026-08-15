## Why

The corpus describes repository layout and configuration — which files exist,
what they contain, how they are named. It says nothing about how code inside a
repository is arranged, what coverage is expected, or which Go version is
supported.

Several of those are uniform today only because repositories were created by
copying one another. Every Go repository targets 100% coverage in its
`codecov.yml`; every one ships goreleaser; all five state "the latest two major
Go versions" in prose. None of it is required, so none of it holds.

Package layout has already diverged: `nats-client` and `nats-server` have only
`pkg/`, `osapi-orchestrator` has `internal/` and `pkg/`, and `gohai` and `osapi`
have `cmd/` as well. Nothing records when each applies.

## What Changes

- Establish the `code-architecture` capability, covering package layout,
  coverage expectations, the supported Go version, and release tooling.
- Record when `cmd/`, `internal/`, and `pkg/` apply, so a new repository does
  not have to infer it.
- Require the coverage target and the release mechanism, which are uniform today
  and held by nothing.

Test framework conventions stay in each repository's `CONTRIBUTING.md`. They are
already written there, and they differ enough between a library and the main
product that specifying them centrally would misdescribe one of them.

## Capabilities

### New Capabilities

- `code-architecture`: how Go code is arranged within a repository, what
  coverage is expected, and which toolchain versions are supported.

### Modified Capabilities

None.

## Impact

- No repository changes. Every requirement records what is already true.
- Future repositories gain a rule to follow rather than a repository to copy.
