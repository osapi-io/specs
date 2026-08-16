## 1. Record the capability

- [x] 1.1 Survey what each repository states against what its code does
- [x] 1.2 Write the `go-code-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point each repository at the capability

- [x] 2.1 `gohai` — `CONTRIBUTING.md` keeps its collector-specific conventions
  and drops the shared ones (osapi-io/gohai#163)
- [x] 2.2 `nats-client` — `CONTRIBUTING.md`
- [x] 2.3 `nats-server` — `CONTRIBUTING.md`
- [x] 2.4 `osapi-orchestrator` — `CONTRIBUTING.md`
  (osapi-io/osapi-orchestrator#76)
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
- [x] 3.6 Confirm no shared convention is stated in two places. `nats-client`
  and `nats-server` point at the capability without restating it, and `osapi`
  now does the same. `gohai` and `osapi-orchestrator` pointed at it *and*
  restated it — `osapi-orchestrator` under `Function Signatures`, `Testing`,
  `Go Patterns`, and `Linting`; `gohai` under `Function Signatures` and its test
  conventions. Both closed with "the specification wins where they disagree",
  which acknowledges the duplication rather than removing it. Their conversions
  under tasks 2.1 and 2.4 did half of what the design's migration calls for:
  they added the pointer and kept the copy. The copies are now dropped
  (osapi-io/gohai#163, osapi-io/osapi-orchestrator#76), leaving each repository
  stating only what is its own
