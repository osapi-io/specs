# Implementation Plan: Move gohai's contributor documentation into the corpus

**Branch**: `docs/gohai-plan-and-tasks` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

**Status**: **Blocked on a constitution gate.** Phase 0 is complete and the
design below is drafted, but the Constitution Check fails on
`global/documentation` in a way this feature cannot resolve for itself. No
`tasks.md` is produced, because the task list differs depending on which way the
conflict resolves. See [research.md](research.md) for the analysis and what is
owed.

## Summary

Move the design rules out of gohai's `docs/methodology.md` into a new memory
document, leave the procedure and the per-collector reference data where they
are, and make every citation resolve. Roughly 215 lines of 769 move. No
collector changes and no OCSF changes.

Planning settled the two things the spec left open, and hit one thing the spec
did not anticipate.

## Technical Context

**Language/Version**: none. Markdown only.

**Primary Dependencies**: mdformat for formatting, `just memory-check` for
counts, `just memory-docs` for the documentation contract.

**Storage**: N/A

**Testing**: `just test` in this repository, which runs mdformat over everything
outside `.claude` and `.specify`, 69 counts in memory against their commands,
and 26 memory documents against the contract. `just test` in gohai for its own
markdown.

**Target Platform**: N/A

**Project Type**: documentation

**Performance Goals**: N/A

**Constraints**: memory carries no `FR-` labels, no `MUST`, no user stories, no
em dashes. Every count in memory needs a command that reproduces it.

**Scale/Scope**: one new memory document of roughly 215 lines, three reduced or
re-cited pages in gohai, one `CONTRIBUTING.md` sentence, one `docs/README.md`
table.

## Constitution Check

| Principle     | Verdict     | Note                                                                                                                                                    |
| ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Documentation | **FAILS**   | See below. This is the gate that blocks the plan.                                                                                                       |
| Verification  | passes      | Every count moved carries a command; the three tier counts were measured rather than carried, and all three were wrong.                                 |
| Tooling       | passes      | No tool version changes. mdformat and the two checkers already run.                                                                                     |
| Correction    | **invoked** | Applying the spec showed the spec is too coarse. Under this principle the specification is corrected first, in its own change, before the plan settles. |
| Workflow      | passes      | Spec Kit throughout. The spec merged before planning began.                                                                                             |
| Repositories  | passes      | The corpus statement merges here, the reduction lands in gohai's own PR.                                                                                |
| Tracking      | passes      | No issue is needed; this feature's task list tracks the work once it exists.                                                                            |
| Baseline      | passes      | The new document is a subject beside `spec.md`, which is the tree shape the fragment asks for.                                                          |

### Why Documentation fails

`global/documentation` opens: *"A repository states in full the conventions
binding it. A reference to guidance held elsewhere does not stand in place of
stating them: a reviewer reading a pull request in a browser, a contributor
working offline, and an agent with a single checkout each see only that
repository."*

Three of the things this feature moves are conventions binding a contributor,
stated as such in the page, with the word MANDATORY on two of them:

- use the upstream library for what it covers, and extend on top rather than
  replacing it
- never roll your own parsing when a library covers it
- no `//go:build` tag anywhere in collector code

Moving those into this repository leaves a contributor with only gohai checked
out unable to read the conventions binding their change, which is the exact harm
the fragment names. Leaving them stated in gohai and *also* stating them here is
two statements of one rule, which `global/baseline` and the whole programme
forbid.

**Neither fragment resolves the conflict.** `global/documentation` is about
conventions and tool settings. `global/baseline` is about what memory is and how
it is shaped. Nothing says which governs a rule that is both a convention
binding a contributor and a description of the architecture.

**It is not new, and not gohai's.** osapi's 005 moved the same kind of rule off
its site into the corpus, and osapi's `CONTRIBUTING.md` states none of them:

```sh
cd ~/git/osapi-io/osapi
grep -cE 'strict-server|no build tags|upsert|idempot|provider contract' CONTRIBUTING.md   # 0
```

So three merged osapi features are in the same tension and nobody noticed, which
is what a fourth application of the rule is for.

### The proposed resolution, which `system` must ratify

Distinguish the **rule** from its **reasoning**, and let each live once:

| Kind          | Example                                   | Lives in          |
| ------------- | ----------------------------------------- | ----------------- |
| The rule      | "no `//go:build` tag in collector code"   | gohai, imperative |
| The reasoning | why, what it buys, what breaks without it | the corpus        |

That is one statement of the rule and one statement of the reasoning, not two
statements of either. A contributor with one checkout reads the rule and can
comply. A contributor who wants to know why follows one link.

This is a change to `global/documentation`, so it recomposes into six
constitutions and belongs to `system` in its own feature, for the reason 002's
FR-037 gives about fragments. Until it is ratified, this plan's mapping of which
headings move cannot be final, because the answer changes for three headings.

## Project Structure

### Documentation (this feature)

```
components/gohai/specs/002-move-contributor-docs/
├── spec.md              merged at specs#218
├── plan.md              this file
├── research.md          Phase 0: the measured counts, and the conflict
├── data-model.md        Phase 1: what each kind of content is, and where it goes
└── checklists/
    └── requirements.md  merged at specs#218
```

### Source (what the implementation touches)

```
components/gohai/.specify/memory/
├── spec.md                      gains a link, loses one exclusion
└── architecture/
    └── collectors.md            NEW, the moved design rules

# in the gohai repository, its own PR, after the above merges
docs/methodology.md              reduced to the reference tables
docs/adding-a-collector.md       nine steps kept, rules replaced by links
docs/ocsf-validation.md          unchanged
docs/README.md                   three rows reworded
CONTRIBUTING.md                  line 8 reworded, one citation added
```

## What planning settled

**The section order of `collectors.md`**, and what its first line answers. Every
other memory document opens with what the thing is. This one is about a layer
rather than a repository, so it opens with what a collector is *for* relative to
the libraries it wraps: gohai is an aggregator, and a collector's job is to
reshape a well-maintained source into a typed struct. Order: what a collector
wraps and why → how a library is chosen → what an extension may do → compiling
everywhere → what a field is called → what is checked against Ohai.

**The library decision order stays a numbered list.** Seven positions, each with
what it is canonical for. It is an ordered decision procedure rather than
reference data: the order is the content, and a table would present seven
equals.

**The extension pattern's code block moves.** Six lines of Go showing the
library call followed by the extension on top. `global/baseline` names a code
block as documentation, and this one states the rule more clearly than a
sentence would.

**The per-collector library stack table does not move**, which the spec settled,
and planning adds the reason it is not a close call: it has 62 rows keyed by
collector, the same key as the catalogue, and its reader is the same reader.

**SC-002 is checked by a reading, and the reader is a fresh agent** given the
reduced pages and the new document and asked one question: name any rule stated
in both. That is the same check every baseline in the programme used, and it is
the only one that catches a restatement in different words.

**The two PRs, in order.** The corpus statement merges here first, then gohai's
reduction. That is the sequence osapi's backfill proved: reducing the page first
would leave the rule stated nowhere for as long as the corpus PR sits in review.

## Complexity Tracking

| Thing                                     | Why it is not simpler                                                                                                                                      |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A new `architecture/` directory for gohai | 215 lines of one subject in a 220-line entry point makes the entry point half about that subject.                                                          |
| Two PRs across two repositories           | `global/repositories` puts the corpus here and the code there, and FR-026 of osapi's 005 fixes the order.                                                  |
| A blocked plan rather than a decided one  | The Correction principle. Deciding a constitutional conflict inside a feature plan is how a rule gets changed where nobody reviews it as a change of rule. |
