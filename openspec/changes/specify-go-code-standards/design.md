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

### `export_test.go` is constrained by what it may expose

The restrictive form came from `gohai`, where aliases exposing unexported
functions had produced tests that re-covered paths the caller's own test already
exercised, and pinned intermediate steps so they could not be changed without
rewriting tests.

The reasoning is not specific to collectors. An alias makes an internal step
directly callable, and a directly callable step attracts a test. The requirement
therefore applies organization-wide.

It constrains what such a file may contain rather than requiring one to exist,
so the two repositories that do not use the pattern are unaffected, and the two
that use it heavily cannot use it to introduce test-only seams.

*Alternative considered:* leave it to `gohai`, since only two repositories use
the file. Rejected — a rule stated only where it was learned is a rule the next
repository discovers by making the same mistake.

### The reason is stated with the rule

Several requirements carry a sentence explaining what goes wrong without them —
why a hand-written mock is worse than a generated one, why an untagged seam
attracts a duplicate test, why `helpers.go` accumulates.

A rule whose cost is invisible is one a future contributor relaxes in good
faith. Stating the failure makes the rule arguable on its merits rather than
enforced by authority.

## Risks / Trade-offs

- **A repository may need an exception.** The requirements state conditions
  rather than absolutes where a legitimate exception exists — mocking is the
  worked example.
- **These rules are testable only by reading code.** Nothing here is enforced by
  a linter. That is a reason to write them down, not a reason not to.

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
