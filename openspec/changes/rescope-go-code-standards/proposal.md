## Why

The five repositories carrying Go code state the same conventions five different
ways, and one of them no longer states them at all.

`Function signatures` sits under `Code style` in `nats-client` and
`nats-server`, under `Code standards` in `osapi-orchestrator`, and nowhere in
`gohai` or `osapi`. Casing disagrees — `Function Signatures` against
`Function signatures`, `Go Patterns` against `Go patterns`. `gohai` nests
`Go Patterns` under `Testing`. `Code standards` exists in three of five. A
reader comparing two repositories cannot tell whether a difference in the
document means a difference in the rule.

`go-code-standards` was written to end that, but it states Go formatting as
corpus requirements. Formatting is not externally observable behavior, which is
the level `config.yaml` says a requirement sits at, and the strain shows in the
scenarios written to fit the format: "a parameter is added, the diff shows one
added line" is a rationale for a preference, not a behavior anything exhibits.

It also has not ended the duplication. Every Go repository lists the linter set
as "errcheck, errname, goimports, govet, prealloc, predeclared, revive,
staticcheck". Each `.golangci.yml` enables `unused`, which no prose mentions,
and configures `goimports` under `formatters` rather than as a linter. Five
hand-maintained copies of one stale approximation of a file sitting beside them.

Applying the capability exposed the last problem. `gohai` dropped its local copy
while `go-code-standards` existed only inside an unarchived change, so for a
period the rules were stated in one place and that place was unreachable. A
repository has to be readable on its own.

## What Changes

- `repo-standards` fixes the middle of `CONTRIBUTING.md`, as it already fixes
  the opening and closing. `Setup`, `Project structure`, `Code style`,
  `Code standards`, and `Testing` become named sections in a defined order, with
  anything a repository invents for itself placed after `Testing`.
- Headings become sentence case everywhere, resolving `Function Signatures`
  against `Function signatures` and the rest.
- A repository SHALL state the conventions binding it **in full**, rather than
  naming a capability in another repository. Where a convention is common, every
  repository states it in the same words.
- A rule a tool enforces is named rather than reproduced, so the linter list
  stops being maintained by hand in five places.
- **BREAKING** `go-code-standards` is reduced to what no tool reports on: mocks
  are generated, and a test does not re-cover behavior through an exported
  alias. Signature layout, file naming, suite naming, table-driven structure,
  and the style baseline leave the corpus for `CONTRIBUTING.md`.
- `Mocks are generated` gains a scenario distinguishing a scripted stand-in from
  a double that carries a real implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `repo-standards`: fixes the middle sections of `CONTRIBUTING.md`, requires
  sentence-case headings, requires a repository to state its conventions in
  full, and stops prose from restating what a tool enforces
- `go-code-standards`: removes the five requirements that state formatting a
  tool enforces, and widens `Mocks are generated`

## Impact

Every repository carrying Go code:

- `gohai` — on `main` with its shared conventions removed (osapi-io/gohai#163);
  this change determines what returns
- `osapi-orchestrator` — the equivalent removal is open and held as a draft
  (osapi-io/osapi-orchestrator#76), and is superseded by this change
- `nats-client`, `nats-server` — still carry their copies, under the wrong
  headings
- `osapi` — points at the capability rather than stating the conventions
  (osapi-io/osapi#450)

Neither `repo-standards` nor `go-code-standards` was in `openspec/specs/` when
the repositories began pointing at them. `go-code-standards` has since been
synced (osapi-io/specs#88); `repo-standards` has not, and this change cannot
modify it until it is.

`specify-go-code-standards` tasks 2.2, 2.3, 2.4, 3.4, and 3.6 are open and point
at the pointer-only destination this change replaces.
