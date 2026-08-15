## Context

See proposal.md - Why.

Surveyed across the five Go repositories:

| Item                 | State                                                                                        |
| -------------------- | -------------------------------------------------------------------------------------------- |
| `codecov.yml` target | `100%` in all four libraries                                                                 |
| `.goreleaser.yaml`   | present in all five                                                                          |
| `go.mod`             | `1.25.7`, `1.25.0` — patch versions already differ                                           |
| Package layout       | `pkg` only (nats-\*), `internal`+`pkg` (orchestrator), `cmd`+`internal`+`pkg` (gohai, osapi) |

The first two are uniform because repositories were created by copying one
another, not because anything requires them.

## Goals / Non-Goals

**Goals**

- Consistency that currently exists by accident becomes consistency held by a
  rule.
- A new repository has something to follow rather than a repository to imitate.

**Non-Goals**

- Test framework conventions. Each repository's `CONTRIBUTING.md` already covers
  them, and a library's differ enough from the main product's that one central
  rule would misdescribe one of them.
- Changing any repository. Every requirement records what is already true.
- Prescribing package layout below the top level.

## Decisions

### Specify layout by who may import, not by a fixed directory set

Requiring every repository to have `cmd/`, `internal/`, and `pkg/` would force
empty directories on `nats-client`, which needs none of the first two. The
useful rule is what each directory means — public API, private code, entry
points — so a repository carries the ones it needs.

*Alternative considered:* require a fixed set. Two libraries would carry empty
directories to satisfy it.

*Alternative considered:* say nothing, since the layout is conventional Go. The
convention has already produced four different combinations across five
repositories, and nothing records which are deliberate.

### Record the 100% coverage target rather than assume it

All four libraries already declare it. Recording it means a repository lowering
its target is a visible change rather than a quiet edit to a YAML file nobody
reads.

*Alternative considered:* specify a lower floor, on the grounds that 100% is
aspirational. It is what every repository already declares; weakening it in the
corpus would be the corpus arguing with the code.

### Keep repository-specific methodology out of the corpus

`gohai` has a 400-line collector methodology: library decision order, the per-OS
struct pattern, the requirement to cross-reference Ohai's plugins. It is design,
and it is normative — a collector written without it is sent back. But it binds
one repository.

The test is whether another repository has to obey it. If yes, it is a
capability; if no, it belongs next to the code it governs.

*Alternative considered:* move all design into the corpus, so every design
decision goes through propose and review. A gohai contributor would then read
another repository to find gohai's own rules, and the corpus would grow to hold
implementation detail that changes with the code.

*Trade-off:* repository-local design does not go through the change process, so
it can shift without review. The rule above says what to do when such guidance
starts binding a second repository — at that point it becomes a capability.

### Require the pre-commit recipe to be sufficient

`gohai` and `osapi-orchestrator` run `just-lint` in CI but omit `just::fmt` from
`ready`. A contributor runs the recipe the guide tells them to run, commits, and
fails on formatting the recipe never touched. `nats-client` and `nats-server`
include it.

The rule is that `ready` is sufficient — not that it contains a particular list,
which would go stale as checks change.

*Alternative considered:* enumerate what `ready` must call. It would need
updating every time a check is added, and would be wrong for a repository whose
toolchain differs.

### Treat action-version lag as drift, not variation

Eight of ten workflows differ across the four libraries. Every one of those
differences is `osapi-orchestrator` pinning older action versions, with six
dependabot pull requests open against it. Only `release` differs for a real
reason — `gohai` builds on macOS and uses a different token.

Naming lag as non-conformance makes an unmerged queue visible as a standards
problem rather than as housekeeping.

The requirement deliberately names no version. Dependabot bumps these
continuously, so "the workflows pin v7" would be false by the next bump — and
the repositories that are behind today will be behind on different versions
tomorrow. The durable statement is that the queue is kept moving, not that any
particular version is current.

*Alternative considered:* require workflows to be byte-identical. `release`
legitimately differs, so the requirement would be false the day it landed.

## Risks / Trade-offs

- **Nothing enforces the coverage target across repositories.** Each declares it
  locally and could quietly lower it. → Same class of problem as every other
  requirement here; a check that reads the corpus would address all of them.

- **The Go version requirement will go stale.** "The two most recent major
  versions" is a moving target, and `go.mod` minimums already differ by patch
  version. → Stated as a policy rather than a pinned version, so it stays true
  as Go releases.

- **"Differ only where the build requires it" is a judgment call.** A repository
  could justify a difference that is really neglect. → The action-version
  scenario names the common case explicitly.

- **The boundary between corpus and repository docs is a judgment call.** →
  Stated as a test — does another repository have to obey it — rather than a
  list.

## Migration Plan

None. Every requirement records what is already true in every repository.

## Open Questions

- Should the corpus specify the CI workflow set? The ten Go workflows are
  identical across four repositories, which is the same accidental consistency
  this change addresses elsewhere. It was scoped out of `repo-standards`
  deliberately and has not been revisited.
- Should patch-level Go versions be aligned, or is the major-version policy
  enough?

### Accept two declarations of the target, and say so

The target has to be readable by two things that cannot read each other: the
coverage service, which evaluates a pull request server-side, and the local
recipe, which has to fail before anyone pushes. Deriving one from the other
means the justfile parses YAML, which is a parser in a shell recipe for the sake
of one integer.

So the number is written twice, and each site carries a comment naming the
other. This is a real duplication and it can drift; the mitigation is that it is
one integer, changed rarely, with a verification task that compares them.

*Alternative considered:* have the local recipe read the target out of
`codecov.yml`. One source, no drift — but it puts YAML parsing in a shared
justfile module used by every repository, and breaks if the service's config
schema changes.

*Alternative considered:* gate only in the service. That is the gap already
being closed for `just::fmt` — a recipe that passes locally while CI fails.

### Exclusions are defined once, applied before upload

`.coverignore` is the single exclusion list, and `unit-cov` strips those files
from the profile before anything else reads it. The coverage service therefore
needs no exclusion list of its own: the files never reach it.

This matters more than it looks. `nats-client` measures 17.3% on the raw profile
and 100% after `.coverignore`. Whichever profile the service uploads decides the
number, and the two answers are 83 points apart for the same commit. Today the
service auto-discovers and happens to find the filtered profile — the workflow
passes no file to it. That is an accident that currently works, so the workflow
names the profile explicitly.

*Alternative considered:* keep `.coverignore` for the local number and add a
matching `ignore:` list to the service config. Two exclusion lists in two
syntaxes, drifting silently, with an 83-point gap available when they disagree.

### Placement belongs to the documentation capability, not this one

An earlier draft of this change carried a requirement that the corpus hold only
what binds more than one repository. The `documentation` capability states the
opposite: what decides placement is whether text is a requirement or a
description, and a rule binding one repository is still a rule.

Both would have archived into the corpus asserting contradictory things about
the same decision. This change drops its version rather than restating a rule it
does not own — placement is one subject, and one capability owns it.

*Alternative considered:* keep both and scope this one to engineering guidance
specifically. Two requirements about where things live, differing in the test
they apply, is how a reader ends up able to justify either answer.

### One gate, five repositories, one number

Coverage binds every repository containing Go code. That is five: `osapi`,
`gohai`, `nats-client`, `nats-server`, and `osapi-orchestrator`. The other
repositories in the organization — `specs`, `osapi-justfiles` — contain no Go
and are unaffected. `osapi-sdk` still consumes the shared `go` module and still
runs `just go::test`, but it is deprecated; archiving it is what stops it being
a consumer, not the fact that its README says so.

Four of the five measure 100% once `.coverignore` is applied. `osapi` does not:

| Repository           | Raw    | After `.coverignore` |
| -------------------- | ------ | -------------------- |
| `osapi`              | 43.6%  | 99.9359%             |
| `gohai`              | 96.5%  | 100.0%               |
| `nats-client`        | 17.3%  | 100.0%               |
| `nats-server`        | 50.0%  | 100.0%               |
| `osapi-orchestrator` | 100.0% | 100.0%               |

`osapi` is 9 uncovered statements short across 7 functions. It was recorded here
as 100% because `go tool cover -func` rounds its `total:` line to one decimal
place, so 99.9359% prints as `100.0%`.

The check keeps reading that rounded figure. An earlier revision computed from
the profile's statement counts instead, on the reasoning that a gate reading a
rounded display has a tolerance nobody chose. That was rejected: the tolerance
is about 0.05%, it is bounded and knowable, and declaring a target below 100%
makes it explicit. Buying the last two decimal places costs arithmetic in a
shared recipe that every repository runs on every commit, and a shared module is
the worst place to put logic that has to be right.

What the rounding does mean is that `osapi` cannot be gated at 100% and be
honest about it — `-func` would report `100.0%` and pass. Hence the 99.9%
target: it states the level actually held, and the 9 statements are tracked to
be covered rather than rounded away.

The raw column is why the gate has to read the filtered profile and nothing
else. Four of the five would fail a 100% gate applied to the raw number, and
`nats-client` would fail by 83 points — not because it is under-tested, but
because the raw profile counts generated code, examples, and `main.go`.

The design that must hold:

1. **One exclusion list.** `.coverignore` is applied by `unit-cov` before
   anything reads the profile, so no second list exists to disagree with it.
1. **One profile.** The local check and the upload read the same filtered file,
   so both report the same number for the same commit.
1. **One invocation.** `just test` runs the gate, and CI runs `just test`. There
   is no separate CI coverage step that could diverge from what a contributor
   runs locally.
1. **One target per repository**, declared in the shared module's default and in
   that repository's `codecov.yml`, each commented to name the other.

Point 3 is the one most easily lost. A coverage step added directly to a
workflow would pass or fail on its own terms, and the local recipe would stop
predicting CI — the same defect being fixed for `just::fmt`, reintroduced.

### The second exclusion list was already there

The survey behind this change looked for coverage configuration at each
repository root and found none, which is how it concluded no repository declared
a target. Every repository had one at `.github/codecov.yml`, byte-identical
across all five, carrying its own `ignore:` list of `**/mocks/*.go` and
`**/*.gen.go`.

So the two-lists-that-can-drift problem this design set out to prevent already
existed, and the two lists had already drifted.

`.coverignore` differs per repository, correctly — `nats-client` excludes
`/mocks/` and `connect_wrapper.go`, `gohai` excludes `/cmd/`, `/examples/`,
`/gen/` and `main.go`. Each names what that repository actually has. The Codecov
list was byte-identical across all five and named neither set: one blanket
`**/mocks/*.go` and `**/*.gen.go` matching no repository's real exclusions.

It produced no discrepancy only because it was inert. `nats-client`'s raw
profile carries 400 lines from `pkg/client/mocks/*.gen.go`; `.coverignore`
strips every one before upload, so Codecov was excluding files it was never
sent. An exclusion that does nothing is still a second declaration of what is
excluded, and the first person to add a pattern to one and not the other gets
two different numbers.

The list is removed rather than reconciled, because reconciling would keep two
lists in agreement by hand — which is the failure this requirement exists to
rule out.

*Alternative considered:* keep it as defense in depth, in case a mock ever
reaches the profile. Defense in depth against your own exclusion list is a way
of saying you do not know which one is authoritative.

### A threshold absorbs rounding, not regression

Codecov rounds to two places and rounds down, so a change in statement count can
render a genuine 100% as 99.99%. At `threshold: 0%` that fails the status on an
artifact rather than on a regression, and the failure is indistinguishable from
a real one — which is how a team learns to ignore the check.

The threshold is therefore kept at 0.05%, the value the file already carried,
and applied to patch as well as project.

This does not weaken the gate, because the gate is not Codecov. `unit-cov-check`
compares integers against `JUST_COVERAGE_TARGET` and fails `just test` locally
and in CI. Codecov's status is the second opinion, and the tolerance exists so
its own rounding does not report a failure the coverage does not have.

*Alternative considered:* raise `precision` so rounding cannot bite. It moves
the boundary rather than removing it, and produces coverage numbers to more
decimal places than anyone reads.

### Covering osapi's last statements is a separate change

An earlier task list carried "cover the 9 uncovered statements, then raise both
declarations to 100". That is a forward reference: archiving verifies every task
is checked, so a task describing work this change does not do would block it
from ever archiving.

The requirement already permits a repository to hold a target below the
organization-wide one at the level it currently meets, and requires that target
to be raised rather than treated as settled. `osapi` at 99.9% satisfies it. The
9 statements are work for a change of their own.
