# Quickstart: verifying the corpus backfill

**Feature**: `003-corpus-backfill` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

Six success criteria, and what to run for each. Three are checked by a gate;
three are checked by reading, and this says what reading means so that "it looks
right" is not the answer.

## Prerequisites

```bash
cd ~/git/osapi-io/specs && mise install && just fetch
cd ~/git/osapi-io/osapi && mise install
```

## The gates

```bash
# In the specifications repository: markdown formatting, justfile lint, and the
# citation checker that resolves every relative link in every skill.
cd ~/git/osapi-io/specs
just test

# In osapi: site formatting, and the build, which fails on a broken internal link.
cd ~/git/osapi-io/osapi
just docusaurus-fmt-check
just docusaurus-build
```

`just test` failing on `skill-lint` is SC-004's gate doing its job: a citation
whose target does not exist.

## SC-001 — a contributor answers from the corpus alone

Not automatable, so it is a reading with a fixed question set. Open only
`components/osapi/specs/004-job-system/spec.md` and answer:

1. What carries a job from the API to an agent, and what guarantees its
   delivery?
2. What must an agent not do when the same job arrives twice, and what does it
   do instead?
3. What bounds how long an operation runs, and what happens when the controller
   stops waiting before the agent stops working?

Each answer must be in the corpus, not in a link to the site. Question 3 exists
because that content is the newest on the page being moved (research Finding 2),
and is the easiest to leave behind.

## SC-002 — an operator still finds everything on the site

```bash
# No surviving site page may send an operator to the specifications corpus.
cd ~/git/osapi-io/osapi
grep -rn "specs repository\|specifications repository\|osapi-io/specs" docs/docs/sidebar/ \
  | grep -v "development/adding-an-api-domain.md"
```

Expected: no output. The one exclusion is the contributor page, whose reader is
not an operator — FR-012 is about operators.

Then open the three surviving pages and confirm each reads as a whole page
rather than a remainder: `architecture/job-architecture.md`,
`architecture/system-architecture.md`, `architecture/architecture.md`. A page
whose first heading follows a paragraph that references content no longer
present has failed FR-003.

## SC-003 — no address stops resolving

```bash
cd ~/git/osapi-io/osapi

# Every address that resolved before the change, including the two that became
# redirects.
for p in \
  architecture/architecture \
  architecture/system-architecture \
  architecture/job-architecture \
  architecture/api-guidelines \
  architecture/principles \
  development/adding-an-api-domain
do
  test -f "docs/docs/sidebar/$p.md" && echo "page   $p" && continue
  grep -q "$p" docs/docusaurus.config.ts && echo "redirect $p" && continue
  echo "MISSING $p"
done
```

Expected: six lines, none of them `MISSING`. A `MISSING` is a 404 nobody would
otherwise notice — which is why this check exists rather than a manual click
through the sidebar.

## SC-004 — one statement, the rest citations

```bash
# For each moved subject, the rule must be stated once. Pick a phrase unique to a
# moved rule and count where it appears.
cd ~/git/osapi-io
grep -rln "append-only" specs/components/osapi osapi/docs/docs osapi/.claude 2>/dev/null
```

Expected: the corpus specification, plus any file whose match is inside a
citation table. A second *statement* of the rule is the failure this catches;
`just test` catches only a citation that does not resolve.

## SC-005 — the skill shrinks

```bash
cd ~/git/osapi-io/specs
git diff --stat main -- .claude/skills/add-a-domain/
```

Expected: net negative on `references/`, and `SKILL.md` unchanged in shape — it
routes, it does not explain. The provider contract's precedent is 171 lines down
to 127 on one reference.

## SC-006 — every moved rule cites the code, and a gap is recorded as a gap

```bash
# A corpus requirement about behaviour must name the file it describes.
cd ~/git/osapi-io/specs
grep -c "internal/" components/osapi/specs/004-job-system/spec.md
```

Expected: a count in the same order as the requirement count. Then, for a sample
of five requirements, open the file each cites and confirm the code does what
the requirement says. A requirement whose code does not match must say so —
FR-009 — and the phrase to look for is a recorded gap, not a silent restatement.
