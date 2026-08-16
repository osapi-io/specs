## 1. Record the capability

- [x] 1.1 Survey what each repository states against what its code does
- [x] 1.2 Write the `go-code-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point each repository at the capability

The capability has to exist in the corpus before a repository can rely on the
pointer alone. It did not until task 2.0 synced it, so the four conversions
below kept their local copy and the pointer led nowhere.

Applying this section is what established that the destination was wrong. A
pointer resolves across a repository boundary, over a network, for every reader,
and `gohai` spent a period citing a capability the corpus did not hold.
`rescope-go-code-standards` replaced it: each repository states the shared
conventions in full, in the same words, and the corpus keeps only what no tool
reports on.

- [x] 2.0 `specs` — sync `go-code-standards` into `openspec/specs/` so the
  pointer resolves. Every repository named it as the source while it existed
  only inside this change, where a reader following the link would not find it
- [x] 2.1 `gohai` — `CONTRIBUTING.md` keeps its collector-specific conventions
  and drops the shared ones (osapi-io/gohai#163)
- [x] 2.2 `nats-client` — `Function signatures` and `Go patterns` move from
  `Code style` to `Code standards`, stated in full (osapi-io/nats-client#133)
- [x] 2.3 `nats-server` — the same (osapi-io/nats-server#94)
- [x] 2.4 `osapi-orchestrator` — stated in full, and the duplication between its
  own `Code standards` and `Testing` sections resolved
  (osapi-io/osapi-orchestrator#77). The removal-only pull request that preceded
  it was closed unmerged
- [x] 2.5 `osapi` — `CLAUDE.md` dropped `Code Standards`, and the conventions
  duplicated into `development.md` and `testing.md` now resolve to the root
  `CONTRIBUTING.md`, which points at this capability rather than restating it
  (osapi-io/osapi#450)

## 3. Verification

- [x] 3.1 Confirm no `types.go` contains a function
- [x] 3.2 Confirm no repository holds a generically named file
- [x] 3.3 Confirm every test package uses a table-driven suite
- [ ] 3.4 Confirm no mock is hand-written where an interface is mocked. The
  original count of three came from a search for structs named `mock`, `fake`,
  or `stub`, which missed every double named for what it does. A full scan of
  test-file structs carrying two or more methods found twenty-nine. Sixteen are
  testify suites, five stand in for stdlib interfaces, one is an
  `export_test.go` alias, and one is a real channel helper. Five are genuine
  violations — four `collector.Collector` doubles in `gohai` and `mockRenderer`
  in `osapi-orchestrator` — and two are met in the code but were forbidden by
  the requirement until `rescope-go-code-standards` widened it. Tracked there as
  section 5
- [ ] 3.5 Confirm no test uses an exported alias to re-cover behavior the
  caller's own test already reaches. Not yet established: 65 `export_test.go`
  files exist (32 in `gohai`, 32 in `osapi`, 1 in `osapi-orchestrator`), and the
  requirement turns on what each exposure is *for*, which no search can decide.
  This needs a file-by-file audit
- [x] 3.6 Confirm no shared convention is stated in two places. Superseded by
  `rescope-go-code-standards`, which decided the opposite: a shared convention
  is stated in every repository it binds, identically, because a repository has
  to be readable on its own. What this task was aimed at — copies that disagree
  — is now the thing `repo-standards` forbids and the standardization pull
  requests removed. The five `Code standards` and `Test file conventions` blocks
  hash identically
