## 1. Record the capability

- [x] 1.1 Survey what each repository states against what its code does
- [x] 1.2 Write the `go-code-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point each repository at the capability

The capability has to exist in the corpus before a repository can rely on the
pointer alone. It did not until task 2.0 synced it, so the four conversions
below kept their local copy and the pointer led nowhere.

- [x] 2.0 `specs` — sync `go-code-standards` into `openspec/specs/` so the
  pointer resolves. Every repository named it as the source while it existed
  only inside this change, where a reader following the link would not find it
- [x] 2.1 `gohai` — `CONTRIBUTING.md` keeps its collector-specific conventions
  and drops the shared ones (osapi-io/gohai#163)
- [ ] 2.2 `nats-client` — `CONTRIBUTING.md` still restates `Function signatures`
  and `Go patterns` under `Code style`
- [ ] 2.3 `nats-server` — `CONTRIBUTING.md` still restates `Function signatures`
  and `Go patterns` under `Code style`
- [ ] 2.4 `osapi-orchestrator` — `CONTRIBUTING.md`
  (osapi-io/osapi-orchestrator#76, open)
- [x] 2.5 `osapi` — `CLAUDE.md` dropped `Code Standards`, and the conventions
  duplicated into `development.md` and `testing.md` now resolve to the root
  `CONTRIBUTING.md`, which points at this capability rather than restating it
  (osapi-io/osapi#450)

## 3. Verification

- [x] 3.1 Confirm no `types.go` contains a function
- [x] 3.2 Confirm no repository holds a generically named file
- [x] 3.3 Confirm every test package uses a table-driven suite
- [ ] 3.4 Confirm no mock is hand-written where an interface is mocked. Three
  remain, each a struct written to satisfy a project-owned interface:
  `fakeCollector` in `gohai` (`internal/collector/registry_public_test.go`),
  `mockRenderer` in `osapi-orchestrator`
  (`pkg/orchestrator/orchestrator_test.go`), and `mockPKISigner` in `osapi`
  (`internal/job/client/signing_public_test.go`). `mockPKISigner` signs with a
  real ed25519 key, so it reads as a real implementation rather than a mock and
  may fall under the carve-out; the other two do not. `gohai` and
  `osapi-orchestrator` declare no mocking library, so satisfying this needs a
  decision on introducing one, not just a regeneration
- [ ] 3.5 Confirm no test uses an exported alias to re-cover behavior the
  caller's own test already reaches. Not yet established: 65 `export_test.go`
  files exist (32 in `gohai`, 32 in `osapi`, 1 in `osapi-orchestrator`), and the
  requirement turns on what each exposure is *for*, which no search can decide.
  This needs a file-by-file audit
- [ ] 3.6 Confirm no shared convention is stated in two places. All four Go
  libraries restated the capability rather than only pointing at it, each
  closing with "the specification wins where they disagree" — which acknowledges
  the duplication instead of removing it. Their conversions under tasks 2.1 to
  2.4 did half of what design.md's migration asks: they added the pointer and
  kept the copy. `osapi` points without restating (osapi-io/osapi#450), and
  `gohai` now does too (osapi-io/gohai#163). `osapi-orchestrator` is in flight;
  `nats-client` and `nats-server` restate under `Code style` as
  `Function signatures` and `Go patterns`, and have no pull request yet
