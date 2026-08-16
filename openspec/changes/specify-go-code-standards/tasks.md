## 1. Record the capability

- [x] 1.1 Survey what each repository states against what its code does
- [x] 1.2 Write the `go-code-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point each repository at the capability

- [ ] 2.1 `gohai` — `CONTRIBUTING.md` keeps its collector-specific conventions
- [ ] 2.2 `nats-client` — `CONTRIBUTING.md`
- [ ] 2.3 `nats-server` — `CONTRIBUTING.md`
- [ ] 2.4 `osapi-orchestrator` — `CONTRIBUTING.md`
- [ ] 2.5 `osapi` — `CLAUDE.md` drops `Code Standards`, and the conventions
  duplicated into `development.md` and `testing.md` resolve to one source

## 3. Verification

- [ ] 3.1 Confirm no `types.go` contains a function
- [ ] 3.2 Confirm no repository holds a generically named file
- [ ] 3.3 Confirm every test package uses a table-driven suite
- [ ] 3.4 Confirm no mock is hand-written where an interface is mocked
- [ ] 3.5 Confirm no `export_test.go` exposes an alias to an unexported function
- [ ] 3.6 Confirm no shared convention is stated in two places
