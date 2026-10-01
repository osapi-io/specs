# Implementation Plan: One shape for every component baseline

**Branch**: `002-baseline-shape` | **Date**: 2026-09-29 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `system/specs/002-baseline-shape/spec.md`

## Summary

The specification states 29 requirements about what a component baseline
contains. This plan says what turning them into landed work consists of, and the
first useful answer is a number: **eleven units of work**, of which this feature
is one. Calling it "the baseline programme" hides that; calling it eleven makes
it schedulable.

What this feature itself produces is small — a charter fragment and a map.
Everything else it produces is *obligation*: nine new features and one amendment
that other projects carry out, each against a shape that is fixed before they
start rather than discovered while they write.

No code changes in any repository. Nothing in `docs/` moves in this feature
either; FR-016 and FR-027 put every move in its own feature.

## Technical Context

**Language/Version**: None. Markdown under `system/` and `components/`.

**Primary Dependencies**: None new. The charter composition machinery already
exists — `.charter/manifest.yml` lists the fragments and
`speckit-charter-compose` writes them into each project's constitution.

**Storage**: N/A.

**Testing**: `just test` in the specs repository — mdformat, just-fmt, and
`scripts/validate-skills.py`. There is no code to unit test. The checks that
matter for this feature are not automatable and are stated in
[quickstart.md](quickstart.md): a reading by somebody who has read none of the
baselines, and a search for any contributor rule stated in two places.

**Target Platform**: The corpus, and six project constitutions.

**Project Type**: Documentation.

**Constraints**: The fragment must match the voice and length of the existing
seven — they run 11 to 36 lines and each states a rule the organization arrived
at by getting it wrong first. A fragment that reads as an invention rather than
a correction is the noise `global/correction` warns about. The map must not
become a second list that drifts, which is the failure `global/repositories`
exists to prevent.

**Scale/Scope**: One fragment. One map section. Nine new features and one
amendment obliged across six projects. 442 documentation pages to be classified
by those features, none of them by this one.

**A number collision worth naming, because it reads as consistent and is not.**
`osapi` was measured at 221 documentation pages, and the four repositories that
still need a move total 221 as well — 68 plus 140 plus 8 plus 5. They are
different quantities that happened to share a figure. What a baseline classifies
is *every* page of its own repository, so the programme's total is the five
repositories that have any, `osapi` included.

**Corrected after osapi's baseline.** osapi has **219** published pages, not
221: the 221 counted the Docusaurus project's own `README.md` and `SUPPORT.md`.
The programme's total is therefore **440**, and the collision this paragraph
warns about turns out to have been a coincidence between a wrong number and a
right one. Reproduce from `osapi/` with
`find docs/docs -name '*.md' -not -path '*/node_modules/*' | wc -l` for 219, and
`find docs -name '*.md' -not -path '*/node_modules/*' | wc -l` for 221. Both
still hold after the UI move, because no page was deleted — the two relocated
pages kept their addresses. Recorded here rather than silently rewritten,
because the collision is still the lesson.

The command matters as much as the number. A first attempt at it added
`-o -name '*.mdx'` and returned 393, because the generated API reference is 174
`.mdx` files. A count is only evidence with the command beside it, and a command
is only evidence once it has been run.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle         | How this feature satisfies it                                                                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** | This is the principle the feature serves. It ends the state where the same contributor rule can sit in a repository and in the corpus, which is what SC-008 measures. The fragment is the enforceable residue; the design stays here.         |
| **Verification**  | The map carries the commands that produce it, so it is measured rather than asserted. FR-007's rule applies to this feature's own artifacts, not only to the baselines it governs.                                                            |
| **Tooling**       | Nothing new is provisioned. The fragment composes through machinery that already exists.                                                                                                                                                      |
| **Correction**    | The feature exists because two completed pieces of work disagreed — osapi's docs moved, gohai's did not. It records that rather than quietly picking one, and FR-026 fixes the ordering error osapi made rather than repeating it five times. |
| **Workflow**      | This is stage 3 for `002`; tasks follow in the same branch. Every obligation it creates is its own feature in its own project, which is what keeps a wrong shape from being discovered six times.                                             |

**Result**: no violations.

## Project Structure

### Documentation (this feature)

```text
system/specs/002-baseline-shape/
├── spec.md              # merged; 29 requirements, 9 outcomes
├── plan.md              # This file
├── research.md          # Phase 0: the six decisions the spec left open
├── data-model.md        # Phase 1: the eleven units, and what each produces
├── contracts/
│   └── section-order.md # Phase 1: the seven sections, and what belongs in each
├── quickstart.md        # Phase 1: how to tell the programme worked
├── checklists/
│   └── requirements.md  # From stage 1
└── tasks.md             # Phase 2 output
```

### Content

```text
specs/
├── .charter/fragments/global/
│   └── baseline.md                    # NEW — the fragment FR-014 requires
├── .charter/manifest.yml              # lists it, so composition picks it up
├── system/.specify/memory/
│   └── plan.md                        # NEW section: the repository map
└── components/*/.specify/memory/
    └── constitution.md                # recomposed, six of them
```

**Structure Decision**: the fragment and the map are this feature's whole
output. The baselines are not written here — that is FR-016, and it is what
stops one wrong judgement propagating into six documents before anybody reviews
it.

## Eleven units of work

Stated plainly because "the baseline programme" and "the next thing" plan very
differently. [data-model.md](data-model.md) gives each one's contents.

| #   | Unit                                               | Project              | Kind                              |
| --- | -------------------------------------------------- | -------------------- | --------------------------------- |
| 1   | The fragment and the map                           | `system`             | this feature                      |
| 2   | Baseline                                           | `osapi`              | new feature                       |
| 3   | Baseline amendment — sections 2, 3, classification | `gohai`              | **amendment to a merged feature** |
| 4   | Move                                               | `gohai`              | new feature                       |
| 5   | Baseline                                           | `osapi-orchestrator` | new feature                       |
| 6   | Move                                               | `osapi-orchestrator` | new feature                       |
| 7   | Baseline                                           | `nats-client`        | new feature                       |
| 8   | Move                                               | `nats-client`        | new feature                       |
| 9   | Baseline                                           | `nats-server`        | new feature                       |
| 10  | Move                                               | `nats-server`        | new feature                       |
| 11  | Baseline                                           | `osapi-justfiles`    | new feature                       |

`osapi` has no move — its documentation was relocated by the backfill across
three features already. `osapi-justfiles` has no move — it has no documentation
pages. `gohai` is the only amendment, because its baseline is merged and
archived.

## Where the fragment lands in that order

**After unit 2, before unit 5.** Neither end works:

- **Before any baseline** binds six repositories to a shape nothing has yet been
  written against. The shape is the thing being tested, and a fragment composed
  into six constitutions is expensive to correct.
- **After all six** means five baselines were written against a specification
  rather than a binding rule, which is exactly the state that produced gohai's
  idiosyncratic first attempt.

So `osapi`'s baseline — the first written to the shape, and the hub whose edges
every other baseline is stated against — is the proof the shape is writable. The
fragment composes once that has merged, and the remaining four baselines are
written under a rule rather than under advice.

`gohai`'s amendment (unit 3) may run either side of the fragment: it is a
correction to an existing document rather than a new one written to the shape.

## Complexity Tracking

> No Constitution Check violations, so this table is empty.
