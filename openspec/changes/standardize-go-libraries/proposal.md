## Why

An audit of the four Go libraries compared thirteen shared configuration files
across `gohai`, `nats-client`, `nats-server`, and `osapi-orchestrator`. Only
three are byte-identical: `.mise.toml`, `.github/labeler.yml`, and
`.github/delete-merged-branch-config.yml`.

Some of that variation is legitimate — `.coverignore` names packages that
differ, `.goreleaser.yaml` names different binaries. Most is not. Two
repositories have no `CODE_OF_CONDUCT.md`. One excludes generated mocks from
coverage and another does not, for no stated reason. One is missing the
`go reference` badge. One still ignores `docs/bun.lock`, the defect already
fixed in `gohai` and `osapi`.

Nothing recorded which of these differences were deliberate, so each was
preserved by whoever touched the repository next.

## What Changes

- Establish the `go-library-standards` capability, covering the configuration
  files a Go library carries.
- Require a `.gitignore` baseline, and prohibit ignoring lockfiles.
- Require the badge set and its order, so a reader sees the same row in every
  library.
- Require the generated-mock coverage exclusion everywhere, rather than in two
  repositories out of four.
- Require a uniform justfile recipe surface, including `generate`.
- Record which files may vary and why, so a future difference is a decision
  rather than an accident.

The workflow set is already identical across all four and is left alone.

## Capabilities

### New Capabilities

- `go-library-standards`: the configuration files a Go library carries, which
  must match across libraries and which may vary.

### Modified Capabilities

None. Organization-wide file requirements live in `repo-standards`; this
capability covers only what is specific to a Go library.

## Impact

- `gohai`: add `CODE_OF_CONDUCT.md`, add the mocks coverage exclusion.
- `nats-client`: add `.worktrees/` to `.gitignore`, add the `generate` recipe.
- `nats-server`: add `.worktrees/` to `.gitignore`, add the `generate` recipe.
- `osapi-orchestrator`: add `CODE_OF_CONDUCT.md`, add the `go reference` badge,
  add the mocks coverage exclusion, and stop ignoring `docs/bun.lock`.
- `osapi`: not a Go library; unaffected.
