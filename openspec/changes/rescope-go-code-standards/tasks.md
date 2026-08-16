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

Applying this section disproved the requirement it was applying.
`Mocks are generated` said a hand-written double "drifts from its interface
silently" while a generated one breaks at compile time. Adding a method to
`collector.Collector` was measured against both: each stopped satisfying it, and
each reported the same error at the point it was used, because Go checks
interface satisfaction structurally at every assignment.

Its replacement first drew the line at whether a test asserts on the
interaction. That line requires judgment at every call site, produces a
different answer per author, and leaves both forms in the codebase with no way
to say which is right. The rule is now a bright line: a double for an interface
this organization defines is generated, with three narrow exceptions where
generating buys nothing.

The order matters. The rule is recorded first, then stated in every repository
it binds, and only then are the implementations changed — so no repository is
asked to follow a rule it does not carry.

- [x] 5.0 Widen the requirement for a recorder on an unjoinable goroutine and
  for stdlib interfaces. Both were being met in the code and forbidden by the
  requirement
- [x] 5.1 Replace `Mocks are generated`, recording the measurement that
  disproved it
- [x] 5.2 Replace the interaction test with a bright line, and permit a
  constructor returning a configured generated mock so that call sites stay as
  short as the struct literals they replace
- [x] 5.3 Specify where a generated mock lives. The corpus named the generator
  but not the layout, and the layout had drifted: roughly forty sites use
  `<package>/mocks/` invoked through `go tool`, while `gohai` uses
  `internal/executor/gen/` invoked through `go run`. `gen` already means
  API-generator output in about twenty-five `osapi` directories

### State the rule where it binds

- [ ] 5.4 Add the mocking convention to the shared `Code standards` section in
  all five Go repositories: the `mocks` package, the `go tool` directive, the
  `*.gen.go` destination, and the three exceptions. Verified by the section
  hashing identically in all five

### Fix the implementations

- [ ] 5.5 `gohai` — replace `fakeCollector`, `errCollector`, `cycleCollector`,
  and `failingCollector` with a generated `collector.Collector` mock and a
  constructor that configures it, so the roughly fifty call sites stay readable
- [ ] 5.6 `gohai` — move `internal/executor/gen/` to `internal/executor/mocks/`
  and invoke the generator through `go tool` rather than `go run`
- [ ] 5.7 `osapi-orchestrator` — replace `mockRenderer` with the generated
  `MockRenderer` in `pkg/orchestrator/mocks/`. It records eight call flags and
  the tests assert `s.True(m.planStartCalled)` and its siblings, which proves
  something was called rather than that it was called correctly
- [ ] 5.8 `osapi` — `captureStore` becomes a generated mock. It was recorded as
  relying on the unjoinable-goroutine exception, and the goroutine is real, but
  checking how the test copes with it found seven `time.Sleep(50ms)` calls. A
  generated mock closes a channel from `DoAndReturn`, so the test joins the
  write instead of waiting out a guess: generated and deterministic, where the
  exception was protecting neither
- [ ] 5.8a `osapi` — rename `mockPKISigner`. It stays hand-written: the test
  asserts `ed25519.Verify(signer.pubKey, payload, envelope.Signature)`, so a
  scripted double returning canned bytes would make the assertion vacuous. It is
  a real signer with a generated key pair, and only its name suggested otherwise
- [ ] 5.8b Confirm no double claims an exception it does not need. The
  exceptions exist for cases where generating buys nothing, not as somewhere to
  put a double that is inconvenient to convert
- [ ] 5.9 Confirm no hand-written struct satisfies an interface this
  organization defines, that every generated mock sits in a `mocks` package
  beside the code it mocks, and that each remaining hand-written double names
  which exception it relies on

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
