## 1. Record the standard

- [x] 1.1 Audit thirteen shared configuration files across the four Go libraries
  and record which match, which differ, and why
- [x] 1.2 Write the `go-library-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Convert the libraries

One pull request per library, satisfying this capability and `repo-standards`
together so each repository is touched once.

- [x] 2.1 `gohai` — add the mocks coverage exclusion
- [x] 2.2 `nats-client` — add `.worktrees/` to `.gitignore`, add the `generate`
  recipe
- [x] 2.3 `nats-server` — add `.worktrees/` to `.gitignore`, add the `generate`
  recipe
- [x] 2.4 `osapi-orchestrator` — add the `go reference` badge, add the mocks
  exclusion, stop ignoring `docs/bun.lock`

## 3. Verification

- [x] 3.1 Confirm every file required to match is byte-identical across the four
  libraries
- [x] 3.2 Confirm no library ignores a lockfile
- [x] 3.3 Confirm `just ready` behaves identically in all four
