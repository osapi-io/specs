# Implementation Plan: A rule and the reason for it live in different places

**Branch**: `docs/003-plan-and-tasks` | **Date**: 2026-09-30 | **Spec**:
[spec.md](spec.md)

## Summary

Add a paragraph to `global/documentation` distinguishing a rule from its
reasoning, and recompose every constitution that composes that fragment. No
repository's documentation changes here. The fragment text is decided below,
verbatim.

Planning found one defect in the merged spec: FR-016 counts six constitutions
and there are seven.

## Technical Context

**Language/Version**: none. Markdown and YAML.

**Primary Dependencies**: the `specify` CLI pinned in the root justfile,
`speckit-charter-compose` per project, mdformat.

**Storage**: N/A

**Testing**: `just test`, which runs mdformat, just-fmt, skill-lint,
`memory-check` over 69 counts and `memory-docs` over 26 documents.

**Target Platform**: N/A

**Project Type**: charter

**Performance Goals**: N/A

**Constraints**: `global/documentation` stays under 25 lines. No em dashes, no
"MANDATORY", no evidence in the fragment.

**Scale/Scope**: one fragment, **seven** composed constitutions, one memory
document in `system`.

## Constitution Check

| Principle     | Verdict | Note                                                                                                                                                    |
| ------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Documentation | passes  | This feature is that principle gaining a clause. The new paragraph does not weaken the existing three.                                                  |
| Verification  | passes  | Composition is verified by grep across all seven constitutions rather than by assuming the tool ran.                                                    |
| Tooling       | passes  | The `specify` CLI stays pinned. Nothing new is installed.                                                                                               |
| Correction    | passes  | The requirement is written from `osapi`'s existing practice, which is what this principle asks for. Planning invoked it once more, for the count below. |
| Workflow      | passes  | Spec merged before planning. Plan and tasks are one review unit, which is what the lifecycle asks and what gohai's 002 did not do.                      |
| Repositories  | passes  | The fragment and the design live here. The compliance work lives in `osapi`.                                                                            |
| Tracking      | passes  | Two follow-on items have owners named in the spec and need no issue while this task list is live.                                                       |
| Baseline      | passes  | The new paragraph is compatible with the one-statement rule, by separating the two statements rather than permitting a second.                          |

### The defect planning found

FR-016 states "Constitutions to recompose | 6" with
`ls components/*/.specify/memory/constitution.md | wc -l`. That command is right
and the number is the wrong number for the task: `system` composes
`global/documentation` too, and its constitution carries the same marker.

```sh
ls components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md | wc -l   # 7
grep -c 'global/documentation SECTION' system/.specify/memory/constitution.md                     # 1
```

Seven projects list the fragment in their own `state.yml`, which is what
composition reads:

```sh
for d in components/*/ system/; do grep -c 'global/documentation' $d.specify/charter/state.yml; done   # 1 seven times
```

Recomposing six would leave `system`'s own constitution stating a rule `system`
wrote and does not carry, which is the shape of defect this programme keeps
finding. The task list recomposes seven. FR-016's figure is amended in the same
change, because it is a count in a merged specification and correcting it is not
a change of intent.

## The fragment text

This is the deliverable. It goes into
`.charter/fragments/global/documentation.md` as the **third** paragraph, after
"the same words" and before the tool-configuration clause.

```markdown
A rule and the reason for it are two statements, and they live in different
places. The rule is stated where somebody about to break it is standing, in the
repository, short enough to check against a diff. The reason is stated once
wherever that repository's design is recorded. Ask whether somebody who cannot
read this would make a wrong change: if they would, it is a rule and belongs in
the repository; if it only changes whether they understand why, it is reasoning
and belongs with the design.
```

Six lines, taking the fragment from 14 to 22.

### Why that position

A reader meets the paragraphs in order, and the first two establish that a
repository states its conventions and states them identically to its siblings.
The new paragraph narrows that: it says what a convention's statement contains
and what it does not. Putting it third leaves the tool-configuration clause
last, which is the strongest of the four and reads as the exception it is.

Before the tool clause rather than after it, because the tool clause is a case
where the rule is not stated in prose at all, and a reader who has just been
told where a rule goes is the right reader for an exception to it.

### Why it does not say "memory"

"Wherever that repository's design is recorded" rather than "in memory". Three
reasons.

A constitution is composed into repositories whose contributors do not use Spec
Kit, and `.specify/memory/` is a Spec Kit directory. `global/baseline` already
names memory, and it is the fragment about the corpus; this one is about
conventions. And a fragment that names a tool's directory is a fragment that has
to change if the tool does, which is the drift the tool-configuration clause two
paragraphs down exists to prevent.

The cost is one indirection for a reader who does not know where design is
recorded. `global/baseline` tells them, in the same constitution.

### Why the test is a question rather than a definition

"Ask whether somebody who cannot read this would make a wrong change" is
imperative and applies to one statement at a time. A definition would invite
sorting by grammar, and the spec's FR-007 is explicit that grammar is the wrong
axis: "MANDATORY" in a heading does not make something a rule, and a paragraph
of explanation is not reasoning if omitting it lets somebody ship a
vulnerability.

## Project Structure

### Documentation (this feature)

```
system/specs/003-rule-and-reasoning/
├── spec.md              merged at specs#220
├── plan.md              this file, carrying the fragment text
├── research.md          Phase 0: the count defect, and what was rejected
├── data-model.md        Phase 1: rule, reasoning, and the test
└── tasks.md             the work in order
```

### Source (what the implementation touches)

```
.charter/fragments/global/documentation.md    the paragraph
components/*/.specify/memory/constitution.md  six recomposed
system/.specify/memory/constitution.md        the seventh
system/.specify/memory/spec.md                the design, one agreement added
system/specs/003-rule-and-reasoning/spec.md   FR-016's count corrected
```

## How SC-003 is run

A fresh reader, given **only** the amended fragment and the list of ten rules
from FR-002 with no indication of which are which, sorts them and says where
each goes.

They are given: the fragment's text, and the ten rules as one-line statements.
They are not given the spec, the corpus, or any repository.

**A pass** is the ten sorted with a stated reason per item, and the reason
referring to consequence rather than to how the rule is worded.

**A failure** is either sorting by wording, which means the test does not
discriminate and the paragraph needs rewriting, or asking for the reasoning
before sorting, which means the test cannot be applied to a rule in isolation
and is therefore not usable at the moment somebody needs it.

This is the only check that the test works. Everything else in this feature
checks that a paragraph landed in seven files.

## Complexity Tracking

| Thing                                                              | Why it is not simpler                                                                                                                                            |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Seven recompositions rather than one edit                          | The constitutions are generated. Editing one is lost on the next compose, which `global/tooling` names.                                                          |
| A fragment paragraph rather than a rule in `system`'s memory alone | A rule that binds every repository is a fragment by the placement test in CONTRIBUTING, and memory holds the design.                                             |
| Correcting FR-016 inside this change                               | It is a count in a merged specification and the number is wrong, not changed. Correcting intent would need its own pull request; correcting a miscount does not. |
