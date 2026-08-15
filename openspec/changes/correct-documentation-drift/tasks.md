## 1. Record the requirement

- [x] 1.1 Audit files, directories, workflow bodies, recipe bodies, and
  documented claims across every non-deprecated repository
- [x] 1.2 Broaden the documented-relationships requirement to cover tooling and
  directories
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Fix the tooling

- [ ] 2.1 `nats-client` — `deps` installs `go.uber.org/mock/mockgen`, not the
  deprecated `golang/mock/mockgen`
- [ ] 2.2 `nats-server` — same
- [ ] 2.3 `nats-client`, `nats-server` — documentation names the library
  `go.mod` declares

## 3. Fix the documentation

- [ ] 3.1 `gohai` — remove the claim about which library `osapi` uses
- [ ] 3.2 `gohai` — point plans at a directory that exists, or drop the
  reference
- [ ] 3.3 `nats-client`, `nats-server` — same
- [ ] 3.4 `osapi-orchestrator` — state that it uses no mocking library

## 4. Repoint references orphaned by the CONTRIBUTING conversion

- [ ] 4.1 `gohai` — `docs/adding-a-collector.md` links twice to
  `../CLAUDE.md#done-definition-every-collector-every-time`; that content is now
  in `CONTRIBUTING.md` and `CLAUDE.md` is a seven-line pointer
- [ ] 4.2 `gohai` — `docs/collectors/kernel.md` and `docs/collectors/memory.md`
  justify decisions "per CLAUDE.md"; name the file that states the rule
- [ ] 4.3 `osapi` — `CLAUDE.md` says `printKV` and `printStyledTable` are in
  `cmd/ui.go`; they are in `internal/cli/ui.go` and `cmd/ui.go` does not exist

## 5. Remove the orphaned artifact

- [ ] 5.1 `gohai` — remove `schemas/all-fields.txt`, which nothing references

## 6. Verification

- [ ] 6.1 Confirm no documentation names a library the repository does not
  declare
- [ ] 6.2 Confirm no documentation points at a directory that does not exist
- [ ] 6.3 Confirm no repository describes another repository's tooling
- [ ] 6.4 Confirm every heading anchor referenced across files resolves
- [ ] 6.5 Confirm no reference cites `CLAUDE.md` for content that moved to
  `CONTRIBUTING.md`
