# Contract: what a citation is, and what checks it

**Feature**: `003-corpus-backfill` | **Date**: 2026-09-28

A documentation feature exposes no interface. What it has is a convention that
other things depend on, and a gate that fails when the convention is broken.
This records both, because FR-007 and FR-008 are only enforceable if a citation
has a shape a checker can resolve.

## The shape

A citation is a relative markdown link from the citing file to the corpus
requirement, in a table that maps each rule to the requirement stating it. The
provider contract set this pattern;
`.claude/skills/add-a-domain/references/provider.md` is the working example.

```markdown
| Rule | Stated in |
| --- | --- |
| A provider returns a typed result, never a formatted string | [FR-004](../../../components/osapi/specs/001-provider-contract/spec.md) |
```

Three properties matter:

1. **Relative, not absolute.** `scripts/validate-skills.py` resolves relative
   links from the file's own directory. An absolute URL is not checked by
   anything, which makes it a restatement with extra steps.

   From a reference file the depth is **four** levels up — `references/` →
   `<skill>/` → `skills/` → `.claude/` → the repository root — so the path opens
   `../../../../components/osapi/specs/…`. Three levels lands in `.claude/` and
   resolves to nothing; the gate says so by name, which is how this note came to
   be written.

2. **Named to a requirement, not to a document.** "See the job system
   specification" is a pointer; "FR-007" is a citation. Only the second tells a
   reader whether the thing they are looking for is there.

3. **One statement per rule.** The citing file states the rule's *name* and
   where it lives. It does not restate the rule, because two statements are what
   this feature exists to end.

## What checks it

| Check                                                               | Where           | What it catches                                                                                                                                           |
| ------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/validate-skills.py`, via `just skill-lint` and `just test` | this repository | A citation in a skill whose target file does not exist. This is the gate FR-008 leans on.                                                                 |
| mdformat, via `just md-fmt-check`                                   | this repository | Formatting of the corpus itself. It excludes `.claude/`, so a skill's own formatting is not checked — which is deliberate and documented in CONTRIBUTING. |
| Prettier, via `just docusaurus-fmt-check` in osapi                  | osapi           | Site formatting. Runs with the tests, not the pre-commit checks.                                                                                          |
| The Docusaurus build                                                | osapi           | A broken internal link between site pages, including one left behind by a moved page.                                                                     |

## What nothing checks

Three gaps, stated so the tasks can cover them by hand rather than assuming a
gate exists:

- **A citation that resolves to a file but names a requirement that is not in
  it.** The checker resolves paths, not anchors. Mitigation: the task that adds
  a citation quotes the requirement it names.
- **A rule stated twice**, once in the corpus and once on the site. No tool
  compares them. Mitigation: FR-010's single-change rule, and the verification
  in [quickstart.md](../quickstart.md).
- **A rule that describes behaviour the code does not have.** FR-009 exists
  because nothing catches this either; the corpus citing the code per FR-011 is
  what makes the next reader able to.
