# Quickstart: telling whether the programme worked

**Feature**: `002-baseline-shape` | **Date**: 2026-09-29

Phase 1. Two of these checks are commands. The two that matter most are not, and
this file says so rather than implying a green build settles it.

## Prerequisites

All repositories cloned as siblings, tools invoked through `mise`:

```bash
cd ~/git/osapi-io && ls -d specs gohai nats-client nats-server osapi osapi-justfiles osapi-orchestrator
```

## SC-009 — the corpus holds together

```bash
cd specs && mise exec -- just test
```

mdformat, just-fmt, and `scripts/validate-skills.py`. This checks formatting and
that every citation resolves. It does **not** check that a baseline's section 3
is architecture rather than a call graph — nothing automatable does.

## SC-005 — the fragment binds rather than advises

```bash
cd specs && grep -rl "^# Baseline" components/*/.specify/memory/constitution.md | wc -l
```

Expected: **6**. A fragment in `.charter/fragments/` that has not been composed
is a file, not a rule. If this returns fewer than six, `speckit-charter-compose`
has not run for every project.

## SC-002 — every count is reproducible

For each baseline, run the commands its measurements section states and compare.

```bash
cd specs && grep -rn '`[a-z].*|.*wc -l`' components/*/.specify/memory/spec.md | wc -l
```

That counts the commands present; running them is the check. A count whose
command no longer reproduces it has not failed — it has **dated**, and the
difference is the signal. What would be a failure is a count with no command
beside it.

## SC-003 — no baseline transcribed the code

```bash
cd specs && grep -rcE "^\s*(func|type) [A-Z]" components/*/.specify/memory/spec.md
```

Expected: low and explicable. A baseline citing a handful of signatures as
evidence is FR-006 working; one listing dozens is the call graph FR-005 forbids.
This is a smell test, not a gate — judgement is the check, and the question is
the one in [contracts/section-order.md](contracts/section-order.md) under
section 3.

## SC-004 — every baseline excludes something, and says so

```bash
cd specs && for f in components/*/.specify/memory/spec.md; do printf "%-28s %s\n" "$f" "$(grep -c "excludes\|deliberately leaves out" "$f")"; done
```

Expected: every row non-zero. Every baseline excludes something — FR-004's
evergreen bound guarantees it — so a zero means the omission was not stated,
which is the failure section 7 exists to prevent.

## SC-007 — every page classified before it moved

Not a single command, because the classification lives in the baseline and the
move lives in another feature. Per repository: the baseline's classification
lists every page under `docs/`, and the move's diff touches only pages that
classification marked contributor-facing.

```bash
cd gohai && find docs -name '*.md' -not -path '*/node_modules/*' | wc -l
```

Compare against the count the baseline's classification covers. A page in the
repository and absent from the classification is the gap this check exists to
catch.

## SC-008 — no contributor rule stated twice

The search that distinguishes a finished programme from six inventories written
beside the documentation they were supposed to replace.

```bash
cd ~/git/osapi-io && for r in gohai nats-client nats-server osapi osapi-orchestrator; do
  printf "%-22s %s contributor-facing pages remaining\n" "$r" "$(find $r/docs -name '*.md' -not -path '*/node_modules/*' 2>/dev/null | wc -l | tr -d ' ')"
done
```

The count alone proves nothing — user-facing pages are supposed to remain. The
check is that every page still there is one its baseline classified
**user-facing**. Anything classified contributor-facing and still present is a
rule stated twice.

## SC-001 — the reading

Not a command. The procedure, and the one that answers whether any of this
worked.

Give a reader who has seen **none** of the baselines all six, and nothing else —
no repository, no site, no session context. Ask three questions:

1. What is each of these six repositories for?
2. Which depends on which, and what would break if one changed?
3. Where would you look to find out how one of them is built?

A pass is all three answered from the baselines alone. Question 2 is the one
that fails if the baselines are six conforming documents that happen to share a
template rather than a set: each can be individually correct and still leave the
graph untraceable, if section 2 was filled in as a formality.

**What a pass proves, and what it does not.** It proves the answers are in the
text. It does not prove a new contributor would enjoy reading six documents in
sequence, and an agent is more patient than a person. Every reading in this
repository has carried that caveat and found real gaps regardless — five across
the osapi backfill, three in gohai's own documentation — so it is worth running
while being honest about its limit.

## Definition of done

| #      | Check               | Passes when                                                 |
| ------ | ------------------- | ----------------------------------------------------------- |
| SC-001 | The reading         | Three questions answered from the six baselines alone       |
| SC-002 | Counts reproducible | Every count has its command; drift is visible, not hidden   |
| SC-003 | No transcription    | No baseline lists the code                                  |
| SC-004 | Omissions stated    | Section 7 non-empty in all six                              |
| SC-005 | The fragment binds  | Composed into six constitutions                             |
| SC-006 | gohai amended       | Its baseline carries sections 2 and 3                       |
| SC-007 | Pages classified    | Every page classified before any move touched it            |
| SC-008 | One statement       | Every page remaining is one its baseline called user-facing |
| SC-009 | `just test`         | Green                                                       |
