## Context

Five repositories write Go. Each states its conventions in its own
`CONTRIBUTING.md`, except `osapi`, which states them in `CLAUDE.md` and again in
`docs/docs/sidebar/development/development.md`.

The survey that preceded this change compared what each repository states
against what its code does, rather than comparing the documents to each other.
That distinction produced the finding: nothing conflicts. Where a repository
does not state a rule, it follows the rule anyway.

## Goals / Non-Goals

**Goals.** State the shared conventions once. Leave each repository free to
state what is genuinely its own.

**Non-Goals.** Changing any code. Every requirement here describes what the five
repositories already do.

## Decisions

### Measured against the code, not the documents

Each rule was checked by counting:

| Rule                              | Measured                                                          |
| --------------------------------- | ----------------------------------------------------------------- |
| Table-driven suites               | every test package in all five repositories — 70, 1, 1, 2, and 72 |
| `types.go` holds only types       | 64 files, none containing a function                              |
| A file is named for what it holds | no `helpers.go` or `utils.go` in any repository                   |
| Generated mocks                   | four repositories mock; all four generate                         |

Two of these are stated in only two or three of the five repositories, and
followed by all five. That is what the capability is for: a rule surviving on
memory in the repositories that never wrote it down.

*Alternative considered:* reconcile the five documents against each other and
write the intersection. Rejected — the intersection would have dropped
`types.go` and the file-naming rule, which only some repositories state and all
five obey. Comparing documents finds what everyone wrote; comparing documents to
code finds what everyone does.

### Mocking is conditional, because one repository legitimately has none

`osapi-orchestrator` declares no mocking library and mocks nothing. It tests
against `httptest.Server` — a real HTTP server on a local port — so there is no
interface to substitute.

Written as "SHALL use gomock", the requirement would make a compliant repository
non-compliant, and the fix would be to introduce a dependency it does not need.
The requirement therefore binds the choice of mock rather than the choice to
mock: where an interface is replaced, the replacement is generated.

This is the second time this repository's testing approach has been mistaken for
an omission. A task in `correct-documentation-drift` asked it to "state that it
uses no mocking library", on the premise that silence meant something was
missing.

*Alternative considered:* require a mocking library everywhere for consistency.
Rejected — consistency in what a rule permits is not the same as consistency in
what a repository does, and the second is not worth a dependency.

### `export_test.go` constrains the purpose, not the mechanism

The first draft of this requirement banned exposing an alias to an unexported
function, allowing only setter functions. That was wrong, and applying it is
what showed why: ten such aliases exist across `gohai` and `osapi`, and the
pattern is idiomatic Go. Twenty-two standard library packages use it —
`net/http` alone exports `DefaultUserAgent`, `NewLoggingConn`, `ExportServeFile`
and more this way.

The rule came from `gohai`, where aliases had produced tests that re-covered
paths the caller's own test already exercised. That concern is real, but it is a
concern about what the test does, not about how the symbol was exposed. Banning
the mechanism outlawed an idiom in order to prevent a misuse of it.

The requirement now names the misuse: a test SHALL NOT use an exported alias to
re-cover behavior the caller's test already reaches. Exposing a pure helper with
its own contract — `BytesToString`, `ParseOffset` — is exactly what the pattern
is for, and a scenario says so.

*Alternative considered:* keep the ban and remove the ten aliases. Rejected —
that would have rewritten eleven working call sites to satisfy a rule the
language's own standard library does not follow.

### The reason is stated with the rule

Several requirements carry a sentence explaining what goes wrong without them —
why a hand-written mock is worse than a generated one, why an untagged seam
attracts a duplicate test, why `helpers.go` accumulates.

A rule whose cost is invisible is one a future contributor relaxes in good
faith. Stating the failure makes the rule arguable on its merits rather than
enforced by authority.

## Risks / Trade-offs

- **A repository legitimately needs an exception and becomes non-conformant.** →
  Requirements state conditions rather than absolutes wherever a legitimate
  exception exists; mocking is the worked example, since one repository mocks
  nothing and declares no mocking library.

- **Nothing enforces these rules, so a repository can drift without failing a
  check.** → They are stated once where every repository can be held to them,
  which is what makes drift reviewable. A rule no linter can check is a reason
  to write it down, not a reason to leave it unwritten.

- **A rule universal in practice today stops being universal.** → Each was
  measured against every repository before being written, so a future exception
  arrives as a change to the requirement rather than as silent non-conformance.

## Migration Plan

No code changes. Each repository's `CONTRIBUTING.md` drops the shared
conventions and points at the capability. `osapi` additionally resolves the
duplication between `CLAUDE.md` and `development.md`, which
`specify-documentation-homes` task 3.6 requires before a root `CONTRIBUTING.md`
can be written.

## Open Questions

None. The suite naming convention was left open in the first draft and is now a
requirement — applying the change is what settled it. Removing the convention
from four repositories while the capability did not state it would have deleted
a rule all five follow, which answered the question more clearly than the
argument about whether the capability was already long enough.
