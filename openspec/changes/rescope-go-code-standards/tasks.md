## 1. Record the rescope

- [x] 1.1 Survey the five Go repositories' `CONTRIBUTING.md` headings and
  establish where they disagree
- [x] 1.2 Establish what each `go-code-standards` requirement is: policy no tool
  reports on, something a tool already enforces, or a convention a reader
  applies
- [x] 1.3 Write the `repo-standards` delta fixing the middle sections, requiring
  sentence-case headings, requiring a repository to state its conventions in
  full, and stopping prose from restating what a tool enforces
- [x] 1.4 Write the `go-code-standards` delta removing the five formatting
  requirements and widening `Mocks are generated`
- [x] 1.5 Record the decisions and their rejected alternatives in design.md
- [x] 1.6 `specs` — sync `repo-standards` into `openspec/specs/`. It was not
  there, so this change's delta had nothing to land on and the repositories
  citing it pointed at a capability the corpus did not hold. Merged from the
  `standardize-repository-layout` and `specify-agent-tool-invocation` deltas: 16
  requirements, 44 scenarios, `openspec validate --specs` passing

## 2. Write the shared sections once

- [x] 2.1 Draft the shared `Code standards` text — `Function signatures`,
  `File naming`, `Go patterns` — with the worked examples that left the
  capability. Verified by the draft covering every rule this change removes from
  `go-code-standards`
- [x] 2.2 Draft the shared `Testing` text — `Test file conventions`, suite
  naming, table-driven cases, and the `export_test.go` pattern
- [x] 2.3 Confirm the draft states no rule that `.golangci.yml` or a formatter
  already enforces, naming the configuration instead

## 3. Apply to each repository

One pull request per repository, each landing the same shared text under the
same headings in the same order. Landed as osapi-io/gohai#164,
osapi-io/nats-client#133, osapi-io/nats-server#94,
osapi-io/osapi-orchestrator#77, and osapi-io/osapi#452.

- [x] 3.1 `gohai` — restore the shared conventions, move `Go patterns` out from
  under `Testing`, and rename `Package Structure` to `Project structure`. It is
  on `main` with the conventions removed, so it goes first
- [x] 3.2 `osapi-orchestrator` — supersede and close the held removal
  (osapi-io/osapi-orchestrator#76), and fold `Project Structure` and
  `Package Structure` into one `Project structure`
- [x] 3.3 `nats-client` — move `Function signatures` and `Go patterns` from
  `Code style` to `Code standards`
- [x] 3.4 `nats-server` — the same
- [x] 3.5 `osapi` — replace the pointer with the shared text, keeping its own
  `Logging`, `Lifecycle`, and `Filesystem access` sections
- [x] 3.6 Move every repository-specific section after `Testing`, and convert
  every heading to sentence case

## 4. Let the configuration speak for what it enforces

- [x] 4.1 Remove the hand-maintained linter list from all five repositories,
  naming `.golangci.yml` instead. Verified by no repository enumerating linters
  in prose
- [x] 4.2 Record that the removed lists were wrong in the same way everywhere —
  `goimports` named as a linter, `unused` omitted — so the reason is evidenced
  rather than asserted

## 5. Resolve the mocks finding

A full scan replaced the original count of three. Sixteen of the structs it
turned up are testify suites rather than doubles, five stand in for stdlib
interfaces, and one is a real channel helper. Five are genuine violations, and
two need the requirement to say something it did not.

- [x] 5.0 Widen `Mocks are generated` for the two cases applying exposed: a
  recorder for a dependency called from a goroutine the test cannot join, and a
  double for a stdlib interface. Both were being met in the code and forbidden
  by the requirement
- [ ] 5.1 `osapi` — record `mockPKISigner` as a real implementation and
  `captureStore` as a permitted recorder, rather than converting either.
  `captureStore` already states its reason where it is defined, which is what
  the widened requirement asks for
- [ ] 5.2 `gohai` — replace the four hand-written `collector.Collector` doubles
  with generated mocks: `fakeCollector` and `errCollector` in
  `internal/collector`, `cycleCollector` and `failingCollector` in `pkg/gohai`.
  The repository already declares `go.uber.org/mock` and generates a mock for
  `executor.Executor`, so this follows an established pattern rather than
  introducing one
- [ ] 5.3 `osapi-orchestrator` — replace `mockRenderer` with a generated mock
- [ ] 5.4 Confirm no hand-written double remains for an interface the
  organization owns, and that each permitted double states which carve-out it
  relies on

## 6. Verification

- [x] 6.1 Confirm the five `CONTRIBUTING.md` files carry the same `##` headings,
  in the same order, up to their repository-specific sections. All five run
  `Before you start`, `Prerequisites`, `Setup`, `Code style`, `Code standards`,
  `Testing`. `gohai`, `osapi-orchestrator`, and `osapi` also carry
  `Project structure`; the two NATS libraries omit it, which the requirement
  permits where a repository has nothing to say under a middle section
- [x] 6.2 Confirm every heading in all five is sentence case. The only remaining
  capitalized pair is `### Claude Code`, a proper noun the requirement exempts
- [x] 6.3 Confirm the shared sections are byte-identical across the five, so a
  difference in wording would mean a difference in rule. Verified by hashing
  each block: `Code standards` and `Test file conventions` each hash the same in
  all five repositories
- [ ] 6.4 Confirm every rule removed from `go-code-standards` is stated in all
  five repositories or enforced by a tool, and that none was dropped
- [ ] 6.5 Confirm `go-code-standards` retains only requirements no tool reports
  on
- [x] 6.6 Confirm `specify-go-code-standards` tasks 2.2, 2.3, 2.4, and 3.6 are
  reconciled with this change rather than left describing the pointer-only
  destination it replaces. 2.2, 2.3, and 2.4 are checked against the
  standardization pull requests; 3.6 is recorded as superseded, since a shared
  convention is now stated in every repository it binds rather than in one
