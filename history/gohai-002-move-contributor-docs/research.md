# Research: moving gohai's contributor documentation

**Feature**: `002-move-contributor-docs` | **Date**: 2026-09-30

Two questions the spec left open. The first is answered and produced a defect in
gohai. The second is not answerable by this feature.

## 1. Can the field-naming ladder's counts be measured?

**Decision**: yes, and the corpus states 107, 91 and 752 with their commands.

**Rationale**: `docs/methodology.md` states the three tiers as roughly 108, 74
and 768 fields, hedged with a tilde and no command, which is why FR-009 required
them measured or dropped. They are measurable: `schemas/field-mapping.md`
carries a `Tier` column for every one of its 950 rows.

| Tier                 | `methodology.md` says | Measured | Off by |
| -------------------- | --------------------: | -------: | -----: |
| T1, OCSF             |                  ~108 |      107 |      1 |
| T2, OTel semconv     |                   ~74 |       91 |     17 |
| T3, gohai convention |                  ~768 |      752 |     16 |
| **Total**            |               **950** |  **950** |  **0** |

```sh
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T1 +\|' schemas/field-mapping.md   # 107
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T2 +\|' schemas/field-mapping.md   # 91
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T3 +\|' schemas/field-mapping.md   # 752
grep -cE '^\| [a-z]' schemas/field-mapping.md                          # 950
```

**The finding is the shape of the error, not the error.** The total is exactly
right and every individual figure is wrong, T2 by 23 percent. Somebody moved
fields between tiers and preserved the sum without revising the prose, so a
check on the total would pass and has nothing to say. This is the second time in
the programme that a figure was **wrong when written or wrong when revised,
rather than stale**; `system`'s memory records the first.

The tilde is what let it through. A hedged number reads as an estimate and so
nobody expects it to be checkable, which is exactly why `global/baseline`
requires a count to carry its command and `just memory-check` fails one that
does not.

**Consequence for the implementation**: correcting `methodology.md`'s three
figures is part of the reduction rather than a separate change, because the page
is being rewritten anyway and leaving three wrong numbers in the part that stays
would be the remainder FR-027 of `system`'s 002 forbids. Recorded as a gap owned
by gohai.

**Alternatives considered**: stating the ladder without numbers. Rejected: the
distribution is the interesting fact. 752 of 950 fields follow neither standard,
which tells a contributor that the third tier is the common case and the first
two are the exception, and that is worth a reader's time in a way "three tiers"
is not.

## 2. Does moving a contributor convention into the corpus satisfy `global/documentation`?

**Decision**: not answerable here. The plan is blocked and `system` owes a
fragment change.

**Rationale**: `global/documentation` requires a repository to state in full the
conventions binding it, and says a reference elsewhere does not substitute,
naming the reviewer in a browser, the offline contributor and the agent with one
checkout. Three of the things this feature moves are conventions binding a
contributor, two of them marked MANDATORY in the page. Moving them produces
exactly the harm the fragment names; stating them in both places produces the
two statements `global/baseline` forbids.

Neither fragment says which governs a rule that is both a convention and a
description of the architecture.

**It is not new and not gohai's.** osapi's 005 moved the same kind of rule off
its published site into the corpus, and osapi's `CONTRIBUTING.md` states none of
them:

```sh
cd ~/git/osapi-io/osapi
grep -cE 'strict-server|no build tags|upsert|idempot|provider contract' CONTRIBUTING.md   # 0
```

Three merged osapi features sit in the same tension. Nobody noticed because
nobody applied the fragment to a move until this one. That is the argument for
applying a rule a fourth time rather than assuming three applications settled
it.

**Proposed resolution**, for `system` to ratify rather than for this feature to
adopt: the rule is stated once where a contributor meets it, in the repository,
imperative and short. The reasoning is stated once in the corpus. One statement
of each rather than two of either. A contributor with one checkout can comply;
one who wants to know why follows a link.

**Alternatives considered**:

- *Move everything and accept the offline contributor cannot read the rules.*
  Rejected: it is the harm the fragment exists to prevent, and a fragment
  overruled silently by a feature is worse than a fragment that is wrong.
- *Move nothing and close the feature.* Rejected: the architecture of the
  collection layer is genuinely absent from the corpus, which the amended
  baseline records as FR-025, and the seven-position library order is not a
  convention by any reading.
- *Decide it in this plan.* Rejected under the Correction principle. A
  constitutional conflict resolved inside a feature plan is a rule changed where
  nobody reviews it as a change of rule, which is the failure the principle
  names.

## What is owed, and by whom

| Owed                                                                                                     | Owner                       |
| -------------------------------------------------------------------------------------------------------- | --------------------------- |
| A `global/documentation` change distinguishing a rule from its reasoning                                 | `system`, its own feature   |
| An amendment to this feature's spec once that lands, since FR-001's split becomes three-way plus a depth | this project                |
| `tasks.md`                                                                                               | this project, after both    |
| Correcting `methodology.md`'s three tier figures                                                         | gohai, inside the reduction |
