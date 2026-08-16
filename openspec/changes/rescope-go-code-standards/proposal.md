## Why

`go-code-standards` states Go formatting conventions — multi-line signatures,
import grouping, error wrapping, early return — as corpus requirements. These
are not externally observable behavior, which is the level `config.yaml` says a
requirement sits at, and the strain shows in the scenarios written to satisfy
the format: "a parameter is added → the diff shows one added line" is a
rationale for a formatting preference, not a behavior anything can exhibit.

The duplication this was meant to end has not ended, and the written rule is
already wrong. Every Go repository's `CONTRIBUTING.md` lists the linter set as
"errcheck, errname, goimports, govet, prealloc, predeclared, revive,
staticcheck". Each `.golangci.yml` enables `unused`, which no repository's prose
mentions, and configures `goimports` under `formatters` rather than as a linter.
Five hand-maintained copies of one stale approximation of a file that already
declares the truth — the drift the capability was written to prevent, occurring
inside the capability's own subject.

Applying the capability exposed the third problem. `gohai` dropped its local
copy while `go-code-standards` existed only inside an unarchived change, so for
a period the rules were stated in exactly one place and that place was not
reachable. Removing a repository's copy is only safe when something reachable
answers in its place.

## What Changes

- **BREAKING** `go-code-standards` is reduced to the rules that are genuine
  cross-repository policy — decisions with consequences that no tool can check.
  Mocks being generated rather than hand-written, and a test not re-covering
  behavior through an exported alias, stay. Function signature layout, file
  naming, suite naming, table-driven structure, and the style baseline leave the
  corpus.
- Formatting rules a tool already enforces are enforced rather than written.
  `golangci-lint` and the formatters it runs are the statement of record; a rule
  a linter checks is not restated in prose anywhere.
- Conventions that remain prose — worked examples, the package names a
  repository uses for its external tests — return to `CONTRIBUTING.md`, where a
  contributor and an agent already read them without a second repository.
- A shared `CONTRIBUTING.md` fragment is distributed the way shared recipes
  already are, so one source produces the copy each repository holds on disk.

## Capabilities

### New Capabilities

- `shared-contributor-documentation`: how contributor guidance common to several
  repositories is distributed, so each repository holds a complete file on disk
  while one source governs its content

### Modified Capabilities

- `go-code-standards`: removes the requirements that state formatting a tool
  enforces, and narrows the capability's purpose to cross-repository policy

## Impact

Every repository carrying Go code, and the shared tooling repository that would
distribute the fragment:

- `gohai` — has already dropped its copy (osapi-io/gohai#163); this change
  determines what returns to it
- `osapi-orchestrator` — the equivalent removal is open and held
  (osapi-io/osapi-orchestrator#76)
- `nats-client`, `nats-server` — still carry their copies, untouched
- `osapi` — its root `CONTRIBUTING.md` points without restating
  (osapi-io/osapi#450)
- `osapi-justfiles` — would carry the shared fragment and the recipe that
  fetches it

`specify-go-code-standards` is in flight and its tasks 2.2, 2.3, 2.4, 3.4, and
3.6 are open. Those tasks convert the remaining repositories to a pointer-only
form; this change decides whether that conversion is the right destination
before two more repositories follow `gohai` into it.
