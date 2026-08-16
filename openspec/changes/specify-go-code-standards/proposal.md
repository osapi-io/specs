## Why

Five repositories write Go, and each states its own conventions. The rules are
the same rules — they are simply written down five times, in five files, with no
mechanism keeping them in agreement.

Surveying what each repository states against what its code does found no
conflict, and two rules already universal in practice but recorded in only some
of the repositories that follow them:

| Rule                                                        | Stated in | Followed by                         |
| ----------------------------------------------------------- | --------- | ----------------------------------- |
| Multi-line signatures, gofumpt, early returns, import order | 5 of 5    | all                                 |
| Table-driven testify suites                                 | 5 of 5    | every test package in all five      |
| `types.go` holds only types                                 | 2 of 5    | all — no violation in 64 files      |
| A file is named for what it holds                           | 3 of 5    | all — no `helpers.go` or `utils.go` |
| Generated mocks rather than hand-written                    | 2 of 5    | the four that mock anything         |
| `export_test.go` exposes only setters                       | 2 of 5    | where the pattern is used           |

A convention followed everywhere and written down twice is a convention that
survives by memory. The next repository copies whichever file it was started
from, and the rules that were only in the other file are lost without anyone
deciding to drop them.

## What Changes

- Add a `go-code-standards` capability recording the conventions all five
  repositories already follow.
- Each repository's `CONTRIBUTING.md` states what is specific to it and points
  at the capability for the rest.

## Capabilities

### Added Capabilities

- `go-code-standards`: how Go is written across the organization — signatures,
  file naming, test structure, mocking, and the style baseline.

## Impact

- `gohai`, `nats-client`, `nats-server`, `osapi-orchestrator`: `CONTRIBUTING.md`
  stops restating shared conventions.
- `osapi`: `CLAUDE.md` drops its `Code Standards` section, and the testing
  conventions duplicated into `development.md` resolve to one source — which is
  what `specify-documentation-homes` task 3.6 requires before a root
  `CONTRIBUTING.md` can be written.
