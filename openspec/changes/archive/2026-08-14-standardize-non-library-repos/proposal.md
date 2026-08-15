## Why

`go-library-standards` covers the four Go libraries. The remaining four
repositories — one main product, one UI, one utility, one documentation — were
audited the same way, and the gaps are larger.

`osapi-ui` has no `.github` directory at all: no workflows, no dependabot, no
labeler, no repository manifest. It is the only repository in the organization
with no CI. `osapi` is missing `delete-merged-branch-config.yml`, which every
other repository has. `osapi-justfiles` has no `.mise.toml` despite requiring
`just` and `uv` to run its recipes.

Each of these types has only one or two repositories, so nothing was ever
compared against anything and the gaps went unnoticed.

## What Changes

- Establish the `non-library-standards` capability, covering the configuration a
  main product, UI, utility, or documentation repository carries.
- Require the repository management files every repository already has, so a
  repository without them is a defect rather than an oversight.
- Require CI appropriate to the repository's toolchain, which for `osapi-ui`
  means having any at all.
- Record which files are specific to a type and legitimately absent elsewhere.

## Capabilities

### New Capabilities

- `non-library-standards`: the configuration carried by repositories that are
  not Go libraries — main product, UI, utility, and documentation.

### Modified Capabilities

None. Files required of every repository regardless of type live in
`repo-standards`; Go library configuration lives in `go-library-standards`.

## Impact

- `osapi-ui`: create `.github` entirely — workflows, dependabot, labeler,
  repository manifest. Substantial work, tracked but not performed by this
  change.
- `osapi`: add `delete-merged-branch-config.yml`.
- `osapi-justfiles`: add `.mise.toml` pinning `just` and `uv`.
- `specs`: already conforms.
