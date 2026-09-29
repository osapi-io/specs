# Research: Building a domain

**Feature**: `005-building-a-domain` | **Date**: 2026-09-28

Phase 0. The specification left five things to planning. Each is decided here
with its reason, so that the task list can be read as work rather than as a
series of judgement calls.

## Decision 1: the corpus statement merges before the site reduction

**Decision**: two pull requests. The corpus half — this feature's planning
artifacts and the skill's citation rows — merges in `specs/` first. The site
half — the contributor page, the two deletions, the `system-architecture.md`
split — merges in `osapi/` second. Archival is third and comes after both.

**Rationale**: the two orders fail differently, and only one of the failures is
recoverable by waiting.

- **Corpus first** leaves a window where both the corpus and the site state the
  same rules. That window is visible, bounded by the second pull request, and
  during it a reader who consults either one gets a correct answer. This is the
  window [003's research Finding 3](../003-corpus-backfill/research.md)
  describes, and Subject A lived in it for a day.
- **Site first** leaves a window where neither states them. The page is gone and
  the skill's citations point at a corpus that has not merged, so `skill-lint`
  fails in `specs/` and a contributor arriving at the old address finds a
  redirect to a page whose citation table resolves to nothing. The authoritative
  statement does not exist anywhere. Nothing recovers that except merging the
  thing that should have gone first.

So the ordering is not a preference about tidiness. One order is a duplicate
answer and the other is no answer.

**Alternatives considered**: one pull request across both repositories is not
available — they are separate repositories, which is the constraint that makes
the sequence a decision at all. Landing the skill citations in the *second* pull
request instead of the first was considered and rejected: it would put a
`specs/` change in an `osapi/` pull request, and `skill-lint` runs in `specs/`.

## Decision 2: the walkthrough lives in `data-model.md`, not in `spec.md`

**Decision**: FR-005 requires the eight steps to be stated as a walkthrough
rather than as eight requirements. That walkthrough is written into
[data-model.md](data-model.md), which `speckit-archive-run` folds into
`.specify/memory/plan.md`. FR-004's three forced orderings stay in `spec.md` and
are folded into `.specify/memory/spec.md`.

**Rationale**: the split follows what each destination is for, and it survives
the thing that will change.

Memory's `spec.md` holds what must be true. Memory's `plan.md` holds how the
work is approached. A forced ordering — the OpenAPI specification before
generation, generation before the handler, the combined specification before the
SDK client — must be true, and stays true as long as the tooling does. The rest
of the sequence is how it is conventionally done, and a tool change rewrites it.
Putting the whole sequence in `spec.md` would mean renumbering requirements
every time `just generate` changes, which is the cost FR-005 was written to
avoid.

The practical test: if a step's position changed tomorrow, would a reader call
the corpus *wrong* or merely *dated*? Forced orderings would be wrong. The rest
would be dated. Only the first belongs in a requirement.

**Alternatives considered**: a separate `walkthrough.md` artifact in the feature
directory. Rejected because archival consolidates a known set of files, and a
file outside that set is a document nothing folds in — which is how the previous
system accumulated fourteen feature directories nobody read. What went into
`contracts/walkthrough.md` instead is the *definition* of the form, not the
content.

## Decision 3: what survives on the contributor page

**Decision**: `adding-an-api-domain.md` keeps its address and is rewritten to
roughly 60 lines with exactly three parts — what adding a domain involves, a
citation table into this specification, and a pointer to the `add-a-domain`
skill. The contents are fixed in [data-model.md](data-model.md).

**Rationale**: this is the one page in the whole backfill where a citation into
the corpus is correct, because its reader is a contributor. 003's FR-012 forbids
sending an *operator* to the corpus; it does not forbid sending a contributor
there, and pretending otherwise would leave this page unable to say anything.

The page cannot simply be deleted, for two reasons that pull in the same
direction. It is linked from the site's development section and from
`system-architecture.md`'s Further Reading, and it is the address a contributor
already has. Redirecting it to the corpus is not possible either: the corpus is
in another repository and is not published as a site.

**Alternatives considered**: keeping a longer summary. Rejected — a summary is a
second statement that drifts, which is the whole failure mode. Three parts and
no prose restating a rule.

## Decision 4: `system-architecture.md` splits at stated line ranges

**Decision**: lines 12–174 (Component Map, Entry Points, Layers) and 241–266
(Request Flow) move to the corpus and are removed from the page. Lines 1–11
(frontmatter and introduction), 175–240 (Health Checks with their endpoints and
CLI access), 267–309 (Security — authentication, authorization, CORS — and
External Dependencies) and the Further Reading list stay, with the list edited.

**Rationale**: stating the ranges makes the split reviewable. Subject A's split
was described by section name and the result was correct, but a reviewer had to
reconstruct the boundaries themselves. Line numbers are checkable against the
file as it stands today, and a range that no longer matches is itself a signal
that the page changed under the plan — which is how 004's Finding 2 was caught.

One consequence is worth naming: removing 241–266 leaves Health Checks (175–240)
directly followed by Security (267). Those read together, so the page does not
need a bridging paragraph. Removing 12–174 does leave the introduction followed
immediately by Health Checks, which is a larger jump, so the introduction takes
one sentence of editing rather than being left to read as a stub.

**Alternatives considered**: moving Security too, on the grounds that
authorization scopes matter to a contributor adding an endpoint. Rejected: an
operator configures roles and needs this page, and a contributor's need is
served by the corpus statement of what a handler must do. The same content
serving two readers is fine when only one of them is sent here.

## Decision 5: the SC-001 reading, and what it can prove

**Decision**: the reading is run by a fresh agent given **only**
`components/osapi/specs/005-building-a-domain/spec.md` and the four questions,
with no session context, no repository access, no site, no other specification
and an explicit instruction not to answer from its own knowledge of Go, REST or
OpenAPI. It returns ANSWERABLE or NOT ANSWERABLE per question, with the
requirements it used.

**Rationale**: the author cannot test their own corpus for completeness, because
they cannot forget what they know. An agent with no context is the available
approximation, and it is the method Subject A used — its
[T015](../004-job-system/tasks.md) is the worked example, and it found two real
gaps that the author had read past twice.

**The limitation, stated rather than left implied**: this proves the answers are
*in the text*. It does not prove a person would succeed. An agent reads
differently, is more literal, and does not get bored; a human reader might stop
at a heading and guess. So a pass here is necessary and not sufficient, and the
task list says so where the task is recorded rather than only here.

The four questions come from SC-001 and each was chosen because an unanswered
version of it breaks a domain: an incomplete domain, a generation step run out
of order, an unvalidated input, a broadcast handler returning the wrong shape.

**Alternatives considered**: asking a person. Not rejected — preferred, if one
is available, and the task permits it. The agent is the fallback that makes the
check runnable rather than aspirational.

## What was verified before writing any requirement

003's FR-009 requires each requirement checked against the repository. The
checks that found something are recorded as Gaps in the specification; the ones
that confirmed the page are listed here so the next reader knows they were run.

| Claim on the page                                  | Verified                                                      | Result                             |
| -------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------- |
| `JobClient` has four generic methods               | `internal/job/client/types.go:146,153,160,167`                | Confirmed                          |
| `WireProviderFacts` is called once, from the agent | `internal/provider/facts.go:64`, `internal/agent/agent.go:90` | Confirmed                          |
| The registry handles dispatch and facts wiring     | `internal/agent/registry.go:51,74`                            | Confirmed                          |
| `IsBroadcastTarget` accepts `_any`, `_all`, labels | `internal/job/subjects.go:306`                                | Confirmed                          |
| `cli.PrintKV` and `cli.PrintCompactTable` exist    | `internal/cli/ui.go:413,198`                                  | Confirmed                          |
| Step 8's four recipes exist                        | `just --list`                                                 | Confirmed, but incomplete — FR-024 |
| `node.validateHostname()` is a shared helper       | three `validate.go` files                                     | **Wrong** — FR-012                 |
| `sdk-standards` is a capability in this repository | `grep -rn sdk-standards`                                      | **Absent** — FR-019                |
| `api-guidelines.md` states five guidelines         | the page                                                      | **Six** — FR-014                   |
| `principles.md` states five principles             | the page                                                      | **Eight** — FR-022                 |

The last two are 003's record being wrong rather than the page having drifted:
003's line counts for all four pages match what is there today. It counted lines
correctly and counted items from memory, which is the same mistake Finding 1
made in its first version and the reason its own T002 exists.
