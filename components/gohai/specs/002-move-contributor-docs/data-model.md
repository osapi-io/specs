# What each kind of content is, and where it goes

**Feature**: `002-move-contributor-docs` | **Date**: 2026-09-30

The spec's FR-001 names three kinds. Planning found the first splits by depth,
which is what blocks the plan. This records the mapping as far as it is settled,
heading by heading, so the reduction is mechanical once the fragment question
resolves.

## The kinds

| Kind                        | Test                                               | Where it lives                              |
| --------------------------- | -------------------------------------------------- | ------------------------------------------- |
| **Rule**                    | A contributor must do this or the change is wrong  | gohai, imperative. **Contested: see plan.** |
| **Reasoning**               | Why the rule, what it buys, what breaks without it | the corpus                                  |
| **Procedure**               | An ordered list of things somebody does            | gohai, beside the code                      |
| **Per-collector reference** | A fact about one collector among 62                | gohai, beside the catalogue                 |

The fourth is settled and uncontested: its key is the collector name, the same
key as `docs/collectors/`, and its reader is somebody using the library.

## Heading by heading

`docs/methodology.md` at gohai `f5eefe2`, 382 lines.

| Heading                                        |   Lines | Kind                    | Disposition                                                       |
| ---------------------------------------------- | ------: | ----------------------- | ----------------------------------------------------------------- |
| Implementation methodology                     |    6-12 | Reasoning               | moves, becomes the opening                                        |
| Extend upstream, don't replace                 |   13-70 | Rule + Reasoning        | **contested**, split by depth                                     |
| Library-first principle                        |   71-87 | Rule + Reasoning        | **contested**, split by depth                                     |
| Per-collector library stack                    |  88-126 | Per-collector reference | stays                                                             |
| Cross-platform compilation: no build tags      | 127-193 | Rule + Reasoning        | **contested**; the reasoning cites osapi rather than restating it |
| Field naming                                   | 194-260 | Reasoning + counts      | moves, with the three figures corrected                           |
| MANDATORY: cross-reference Ohai's data sources | 261-298 | Rule + Reasoning        | **contested**; the `gh api` invocation is procedure and stays     |
| Data Sources                                   | 299-344 | Per-collector reference | stays                                                             |
| Methodology work                               | 345-382 | Repository convention   | stays, `global/tracking` governs it                               |

The three contested rows are the plan's gate. Under the proposed resolution each
splits: a one-line imperative stays, the paragraphs explaining it move. Under a
reading where `global/documentation` governs outright, all three stay and the
move shrinks to the opening, field naming, and nothing else, which is roughly 75
lines rather than 215.

`docs/adding-a-collector.md`, 280 lines: nine steps, all Procedure, all staying.
Step 4 gains a citation to the registration limitation.

`docs/ocsf-validation.md`, 107 lines: four steps plus two reference sections.
All staying. Gains a citation *from* `CONTRIBUTING.md`, which it has never had.

## The new document's shape

`components/gohai/.specify/memory/architecture/collectors.md`, in this order:

1. What a collector is for, relative to the libraries it wraps. gohai aggregates
   rather than reimplements, and a collector reshapes a maintained source into a
   typed struct.
2. How a backing library is chosen. Seven positions, in order, each with what it
   is canonical for. Stays a numbered list because the order is the content.
3. What an extension may do, and the two seams that make it testable, `avfs.VFS`
   and `executor.Executor`. Carries the six-line Go snippet.
4. Why collector code compiles everywhere with no build tag, citing
   [osapi's providers](../../../../osapi/.specify/memory/architecture/providers.md)
   for the pattern rather than restating it.
5. What a field is called. Three tiers with the corrected counts and their
   commands, and the observation that 752 of 950 follow neither standard.
6. What is checked against Ohai and what is not: the collection approach, not
   the output shape.

## Sizes, for checking the split afterwards

| Thing                      |    Estimate | How it is checked                                    |
| -------------------------- | ----------: | ---------------------------------------------------- |
| `collectors.md`            |  ~215 lines | `wc -l`, and whether a reader answers SC-001         |
| `methodology.md` after     | \<200 lines | `wc -l`, and whether a reader answers what it is for |
| Rules stated in two places |           0 | a fresh reading, per SC-002                          |

An estimate missed by a wide margin means the split was drawn in the wrong
place, which is what the spec's Assumptions say to watch for.
