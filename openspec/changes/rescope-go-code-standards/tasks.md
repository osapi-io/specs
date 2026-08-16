## 1. Record the rescope

- [x] 1.1 Establish what each requirement is: policy no tool reports on,
  something a tool already enforces, or a convention a reader applies
- [x] 1.2 Write the `go-code-standards` delta removing the five formatting
  requirements and widening `Mocks are generated` to exclude a double that
  carries a real implementation
- [x] 1.3 Write the `shared-contributor-documentation` capability
- [x] 1.4 Record the decisions and their rejected alternatives in design.md

## 2. Establish the shared fragment

Nothing is removed from a repository until the fragment that replaces it exists
and can be fetched.

- [ ] 2.1 `osapi-justfiles` — write the shared Go conventions fragment: file
  naming, `types.go` for types only, test file naming, table-driven suites,
  suite naming, the `export_test.go` pattern, and worked signature examples.
  Verified by the fragment containing every rule removed from
  `go-code-standards` by this change
- [ ] 2.2 `osapi-justfiles` — add the recipe that fetches it, following the
  pattern the `justfiles` capability records for recipes. Verified by a fresh
  checkout of a consumer producing the file
- [ ] 2.3 Confirm the fetched path is ignored rather than committed in every
  consumer, and that no formatter or linter runs against it

## 3. Return the conventions to each repository

One repository per pull request, each fetching the fragment and stating its own
conventions beside it.

- [ ] 3.1 `gohai` — restore the shared conventions via the fragment. It is on
  `main` with them removed (osapi-io/gohai#163), so it goes first
- [ ] 3.2 `osapi-orchestrator` — supersede the held removal
  (osapi-io/osapi-orchestrator#76) with the fragment, and close it
- [ ] 3.3 `osapi` — replace the pointer in its root `CONTRIBUTING.md`
  (osapi-io/osapi#450) with the fragment
- [ ] 3.4 `nats-client` — replace its restated copy with the fragment
- [ ] 3.5 `nats-server` — replace its restated copy with the fragment

## 4. Let the configuration speak for what it enforces

- [ ] 4.1 Remove the hand-maintained linter list from every repository's
  contributor documentation, naming `.golangci.yml` instead. Verified by no
  repository's prose enumerating linters
- [ ] 4.2 Confirm the removed lists were wrong in the same way everywhere —
  `goimports` named as a linter, `unused` omitted — so the reason for removing
  them is recorded rather than asserted

## 5. Resolve the mocks finding

- [ ] 5.1 `osapi` — record `mockPKISigner` as a real implementation under the
  widened requirement, rather than converting it. It signs with a generated
  ed25519 key pair, and a generated mock would replace that with a canned return
- [ ] 5.2 `gohai` — replace `fakeCollector` with a generated mock, or state why
  the collector interface is better served by a real implementation
- [ ] 5.3 `osapi-orchestrator` — replace `mockRenderer` with a generated mock,
  and correct `CONTRIBUTING.md`, which says the repository declares no mocking
  library while hand-rolling one

## 6. Verification

- [ ] 6.1 Confirm every rule removed from `go-code-standards` is stated in the
  fragment or enforced by a tool, and that none was dropped
- [ ] 6.2 Confirm each of the five repositories holds the conventions on disk,
  readable without fetching another repository
- [ ] 6.3 Confirm no convention is stated both in the fragment and in a
  repository's own section
- [ ] 6.4 Confirm `go-code-standards` retains only requirements no tool reports
  on
- [ ] 6.5 Confirm `specify-go-code-standards` tasks 2.2, 2.3, 2.4, and 3.6 are
  reconciled with this change rather than left describing the pointer-only
  destination it replaces
