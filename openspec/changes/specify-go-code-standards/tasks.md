## 1. Record the capability

- [x] 1.1 Survey what each repository states against what its code does
- [x] 1.2 Write the `go-code-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point each repository at the capability

- [x] 2.1 `gohai` — `CONTRIBUTING.md` keeps its collector-specific conventions
- [x] 2.2 `nats-client` — `CONTRIBUTING.md`
- [x] 2.3 `nats-server` — `CONTRIBUTING.md`
- [x] 2.4 `osapi-orchestrator` — `CONTRIBUTING.md`
- [ ] 2.5 `osapi` — `CLAUDE.md` drops `Code Standards`, and the conventions
  duplicated into `development.md` and `testing.md` resolve to one source

## 3. Verification

- [x] 3.1 Confirm no `types.go` contains a function
- [x] 3.2 Confirm no repository holds a generically named file
- [x] 3.3 Confirm every test package uses a table-driven suite
- [ ] 3.4 Confirm no mock is hand-written where an interface is mocked
- [ ] 3.5 Confirm no `export_test.go` exposes an alias to an unexported
  function. Ten exist — four in `gohai`, which states the rule, and six in
  `osapi`. Eleven call sites depend on them
- [ ] 3.6 Confirm no shared convention is stated in two places
