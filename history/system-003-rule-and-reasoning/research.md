# Research: where a rule lives and where its reason lives

**Feature**: `003-rule-and-reasoning` | **Date**: 2026-09-30

## 1. How many constitutions compose this fragment?

**Decision**: seven, not six. FR-016's count is corrected in this change.

**Rationale**: composition reads each project's own `.specify/charter/state.yml`
rather than `.charter/manifest.yml`, and all seven projects list
`global/documentation`:

```sh
for d in components/*/ system/; do grep -c 'global/documentation' $d.specify/charter/state.yml; done
# 1, seven times
ls components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md | wc -l   # 7
```

FR-016's command counts only `components/*/`, which is right about components
and wrong about the task. `system` is a project like any other, which its own
CONTRIBUTING says in as many words, and `system`'s constitution carries the
`global/documentation` marker.

**Why it matters more than one file**: recomposing six would leave `system`'s
own constitution stating a rule `system` wrote and does not carry.
`osapi-justfiles`' baseline recorded the same shape of error, where "the six"
and "the repositories" were used interchangeably and produced a wrong consumer
count. This is that confusion in a different place, which is the argument for
the fragment being composed rather than described.

## 2. Should the fragment say "memory"?

**Decision**: no. It says "wherever that repository's design is recorded".

**Rationale**: three things, in order of weight.

A constitution is read by contributors who do not use Spec Kit.
`.specify/memory/` is a Spec Kit directory, and a rule binding every repository
should not depend on the tool the rule was written with.

`global/baseline` already names memory and is the fragment whose subject is the
corpus. This paragraph's subject is conventions. Naming memory here puts the
same noun in two fragments with different jobs.

And the tool-configuration clause two paragraphs down says prose describing a
tool's settings drifts while continuing to read as authoritative. A fragment
that names a tool's directory is subject to that clause.

**Cost**: a reader who does not know where design is recorded has one
indirection. `global/baseline` answers it in the same constitution.

**Alternatives considered**: "the corpus", rejected because it is this
organization's jargon and the spec's own reading found "the corpus" undefined in
all six baselines. "In `.specify/memory/`", rejected for the reasons above.

## 3. Is the test a question or a definition?

**Decision**: a question, stated imperatively, applying to one statement at a
time.

**Rationale**: the spec's FR-007 says the axis is consequence rather than
grammar. A definition invites sorting by form, which is what produced the
problem: three of gohai's headings are marked MANDATORY and that is not what
makes them rules, while `osapi`'s stdin rule is a paragraph of explanation and
omitting it lets somebody ship the thing GHSA-6gc6-px2x-q95j describes.

**Alternatives considered**: a two-column table of examples in the fragment.
Rejected under FR-010: the fragment carries the rule and the test, not the
evidence, and a table of examples is evidence that would need maintaining in
seven composed copies.

## 4. What is not resolved

The gap FR-017 records stands unchanged: nothing checks that a rule in memory is
also stated in its repository. Planning looked for a mechanism and found none
that does not require knowing which statements are rules, which is the judgement
the test exists to make. A checker that counted links, or headings, or the word
"must", would pass on documents that fail the actual rule, which is worse than
no checker because it would read as coverage.

Recorded rather than solved, and the spec already says it may not be
automatable.
