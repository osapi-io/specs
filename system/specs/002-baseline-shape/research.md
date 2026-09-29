# Research: One shape for every component baseline

**Feature**: `002-baseline-shape` | **Date**: 2026-09-29

Phase 0. The specification left six things to planning. Each is decided here
with its reason, so the task list reads as work rather than as a series of
judgement calls.

## Decision 1: the fragment's wording

**Decision**: a new fragment at `.charter/fragments/global/baseline.md`, listed
in `.charter/manifest.yml` so composition picks it up, reading:

```markdown
# Baseline

A repository's memory states what the repository is before it states what was decided
about it. What it is, where it sits among the others, how it is built, what a consumer
may depend on, what was measured and the command that measures it again, where its own
prose and its code disagree, and what the inventory leaves out.

Memory filled only by archived features records a sequence of changes. It answers what
was decided and never what the thing is, so a reader arriving at it learns how one
mechanism works before learning what the repository is for. That is the state osapi's
memory was in after five features: 1,840 lines, no statement of purpose, no dependency,
no architecture.

A count is written with the command that produces it. A number alone is a claim that
was true when somebody typed it, and nothing marks the moment it stops being true.
```

**Rationale**: it matches the existing seven in shape — the rule flatly, then
the failure it came from, then the generalisation. It matches their length: 14
lines against their 11 to 36. And the middle paragraph names a real event rather
than a hypothetical, which is what `global/correction` requires of a
requirement: "Write a requirement from evidence the repository already carries."

The last paragraph is deliberately a second rule rather than more context. The
counts-with-commands discipline is the one piece of the shape that is
mechanically checkable, and a fragment that omitted it would leave the most
enforceable part as advice.

**Alternatives considered**: folding this into `global/documentation`, which
already governs where a rule is written down. Rejected — that fragment is about
not restating a rule in two places, and this one is about a document being
incomplete in a particular way. Merging them would make both vaguer. Also
considered: naming the seven sections in the fragment. Rejected — the fragment
is the enforceable residue, not a summary, and a seven-item list in a
constitution invites editing the list rather than reading the specification.

## Decision 2: where the map lives

**Decision**: `system/.specify/memory/plan.md`, in a new section
`## The Repository Map`. Not `spec.md`.

**Rationale**: the split already in use across every project's memory is that
`spec.md` holds what must be true and `plan.md` holds the current implemented
state. A dependency graph is current state: it changes when a `go.mod` changes,
and no requirement is violated when it does. The *rule* that each baseline
states its own edges is a requirement and lives in `spec.md` as FR-002; the
*graph* is the state and lives in the plan.

**How it stays true, given each baseline also states its edges.** Three things,
and the third is what makes it more than a promise:

1. The map carries the commands that produce it — `grep osapi-io */go.mod` for
   the Go edges and the justfile fetch for the build edge — so it is
   re-derivable rather than remembered.
2. Each baseline states its own edges independently (FR-002), so the map has six
   witnesses rather than being the only record.
3. [quickstart.md](quickstart.md) makes the disagreement checkable: the map and
   the six baselines must agree, and a mismatch means one of them is stale
   rather than leaving a reader to guess which.

**Alternatives considered**: a `map.md` file of its own in memory. Rejected —
`speckit-archive-run` consolidates a known set of files, and a file outside that
set is one nothing folds into, which is how the previous system accumulated
fourteen directories nobody read. Also considered: no central map, edges only.
Rejected by FR-019 — distributed edges never compose into a picture, and a
reader wanting the graph would have to read six documents first.

## Decision 3: eleven units, and which is which

**Decision**: eleven, enumerated in [plan.md](plan.md). Nine new features, one
amendment, and this feature.

**Rationale**: the arithmetic is worth stating because two of the six
repositories do not take the full pair. `osapi` needs a baseline and no move —
the backfill relocated its documentation across three features already.
`osapi-justfiles` needs a baseline and no move — it has no documentation pages
at all. So it is six baselines and four moves, not six and six, and one of the
baselines is an amendment rather than a new feature.

**Alternatives considered**: one feature per repository, doing baseline and move
together. Rejected, and this is FR-026's whole point: osapi did the move without
ever writing the baseline, and the result is memory that never says what the
repository is. Combining them invites the same shortcut, because the move is the
visible half.

## Decision 4: gohai's amendment is one amendment plus one feature

**Decision**: `gohai`'s existing baseline is **amended** to add sections 2 and 3
and the doc-page classification. Its move is a **separate new feature**. Two
units, of different kinds.

**Rationale**: the baseline is merged and archived, so adding to it is a
correction to a merged statement — its own pull request, ahead of the work that
depends on it, which is what the Correction principle requires and what this
session has done four times already. The move is new work against that corrected
baseline, so it is a feature.

Concretely the amendment adds:

| To gohai's baseline                         | Why it is missing                                 |
| ------------------------------------------- | ------------------------------------------------- |
| Section 2, where it sits                    | The shape did not exist when it was written       |
| Section 3, architecture                     | Its FR-016 excluded architecture **deliberately** |
| The doc-page classification of all 68 pages | FR-025 did not exist                              |

The second row is the one to read twice. gohai's baseline did not omit
architecture by oversight; it stated the exclusion as a decision. That is why
this was findable at all, and it is why the amendment reverses a judgement
rather than filling a blank.

**Alternatives considered**: re-specifying gohai's baseline as a new feature and
superseding the old one. Rejected — the old one is correct about everything it
states, and superseding it would retire requirements that still hold to fix two
that are missing.

## Decision 5: the fragment lands after the first baseline

**Decision**: compose the fragment after `osapi`'s baseline merges, before the
remaining four are written. [plan.md](plan.md) states it; the reasoning is here.

**Rationale**: both ends fail, and they fail differently.

- **Fragment first** binds six repositories to a shape nothing has been written
  against. The shape is the hypothesis; a constitution is where you record a
  settled rule, not where you test one. Correcting a composed fragment means
  recomposing six constitutions.
- **Fragment last** means five baselines were written against a specification
  rather than a binding rule. That is precisely the condition that produced
  gohai's idiosyncratic first attempt — there was a goal and no rule, so the
  writer's judgement filled the gap and excluded architecture.

`osapi` is the right proof because FR-029 already puts it first for a different
reason: it is the dependency hub, so its "where it sits" is what every other
baseline's edges are stated against. One baseline written to the shape shows the
shape is writable against the hardest case — 2,739 Go files and 221
documentation pages — and the fragment then binds the remaining four.

**Alternatives considered**: composing after two baselines, for a second data
point. Rejected as false precision: if osapi's baseline can be written to the
shape, the shape is writable, and a second one delays the rule without testing
anything new.

## Decision 6: how anyone tells the programme worked

**Decision**: two checks, neither automatable, both in
[quickstart.md](quickstart.md).

**Rationale**: the outcome is not "eleven units merged". It is that the corpus
answers two questions it cannot answer today.

- **SC-001, the reading.** Somebody who has read none of the baselines reads all
  six and states what each repository is for and every dependency edge. This is
  the goal in one sentence, and it is the check that a set of six conforming
  documents actually composes into a map rather than six correct documents that
  share a template.
- **SC-008, the search.** No contributor rule is stated in both a repository and
  the corpus. This is the one-statement rule applied across repositories instead
  of within one, and it is what distinguishes a finished programme from six
  inventories written beside the documentation they were supposed to replace.

**The limitation, stated rather than left implied.** The reading proves the
answers are in the text; it does not prove a person would find them pleasant to
read, and an agent reading six documents in sequence is more patient than a new
contributor. Every reading in this repository so far has carried that caveat and
found real gaps anyway — five across the osapi backfill and three in gohai's own
documentation — so it is worth running while being honest about what it
establishes.
