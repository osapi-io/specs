## Why

The corpus was authored without reading the schema it is written to. OpenSpec
supplies a template and a set of rules for every artifact, retrievable with
`openspec instructions <artifact> --change <name>`. That command was never run.
`CONTRIBUTING.md` documents the four-stage workflow and does not mention it, so
nothing pointed at the rules and they were followed only where they happened to
match instinct.

Three rules were missed, and `openspec validate --strict` passes anyway — it
checks delta structure, not conformance:

- **Risks use the form `[Risk] -> Mitigation`.** No design document uses it. Not
  one of fifteen, including four written before this was noticed.
- **One behavior per requirement.** Eighteen requirements across all six
  capabilities carry three or more `SHALL` statements. `Coverage target` carries
  eleven. A requirement bundling three rules cannot be modified independently:
  changing one rewrites a heading the other two live under, which is the
  fragility that has twice nearly orphaned a delta.
- **Requirements do not name files, functions, or libraries.** Twenty do.

The same gap explains a second failure. The archive workflow assesses whether a
delta's target exists in the main spec before merging. Archiving was run with
`--yes`, which skips the prompt that assessment surfaces in. Two changes carried
a `MODIFIED` delta against a requirement the corpus did not hold, and both were
caught by reading rather than by the check that exists for it.

## What Changes

- `CONTRIBUTING.md` states that each artifact has a template and rules, and how
  to retrieve them.
- Design documents state risks in the form the schema defines.
- Requirements bundling several behaviors are split, so each can be modified
  without rewriting the others.
- Requirements naming a file, function, or library either move that detail to
  design, or record why the name is the subject rather than an implementation
  detail.

## Capabilities

### Modified Capabilities

- `documentation`: adds what an artifact in the corpus must satisfy, so the
  rules bind the corpus rather than living only in the tool that scaffolds it.

## Impact

- `specs`: `CONTRIBUTING.md` gains the workflow detail; fifteen design documents
  and six capability specifications are revised. No other repository is affected
  — every change here is to how the corpus is written, not to what it requires
  of code.
