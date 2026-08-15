## 1. Record the standard

- [x] 1.1 Audit the configuration of the main product, UI, utility, and
  documentation repositories
- [x] 1.2 Write the `non-library-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Convert

- [x] 2.1 `osapi` — add `delete-merged-branch-config.yml`
- [x] 2.2 `osapi-justfiles` — add `.mise.toml` pinning `just` and `uv`
- [x] 2.3 `osapi-ui` — create `.github`: workflows for its toolchain,
  dependabot, labeler, repos.json

## 3. Verification

- [x] 3.1 Confirm every repository has the four management files
- [x] 3.2 Confirm every repository runs checks on pull requests
- [x] 3.3 Confirm no repository carries configuration for a toolchain it does
  not use
