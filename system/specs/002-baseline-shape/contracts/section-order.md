# Contract: the seven sections, and what belongs in each

**Feature**: `002-baseline-shape` | **Date**: 2026-09-29

FR-001 fixes the seven sections and their order. This records what belongs in
each and, more usefully, what a writer will be tempted to put there that does
not. Nine features will be written against this; without it, "architecture"
means whatever the writer thought it meant, which is how the first baseline came
to exclude it.

## 1. What this repository is

**Belongs**: its purpose in a paragraph, and who consumes it — a program, an
operator, a contributor, another repository.

**Does not**: a feature list. A reader wanting features reads the repository's
own documentation; a reader here wants to know whether they are in the right
repository at all.

## 2. Where it sits

**Belongs**: what it depends on, what depends on it, and what breaks in each
direction. Both directions, **even when one is empty** — `gohai` has no edges
either way, and "no edges" is information where an absent section reads as
unfinished.

**Does not**: the whole graph. That is the map's job, held once in `system`'s
memory. A baseline states its own edges so the map has witnesses, not so the
graph is written six times.

## 3. Architecture

**Belongs**: the parts, what each is *for*, and what passes between them. "The
agent receives work through a queue and returns a result through a store"
survives a rename; "`handler.go` calls `processJob` which calls the provider"
does not.

**Does not**: a transcribed call graph, a list of every exported function, or a
file-by-file walkthrough — FR-005 forbids all three. Each is wrong within a
month and each is obtainable from the code faster than from prose.

**The test**: if a function were renamed tomorrow, would this section become
*wrong*, or merely cite a stale path? Wrong means it was written at the level
FR-004 forbids. A symbol appears as evidence for a claim, never as the claim —
FR-006.

## 4. The contract

**Belongs**: what a consumer may depend on. An interface and its methods, a wire
format, a set of recipe names, an exported package surface — whatever this
repository's consumers actually bind to. And what is explicitly *free to
change*, which is the half writers omit.

**Does not**: anything already stated elsewhere in the corpus. `osapi`'s
contract is already four archived features; its baseline cites them. Restating
is the second statement the programme exists to end.

## 5. Measurements

**Belongs**: counts, each with the command that reproduces it — FR-007. A table
is right here; this is the one section that is genuinely tabular.

**Does not**: a count without its command. That is a claim that was true when
somebody typed it, and nothing marks the moment it stops being true.

## 6. Gaps

**Belongs**: every place the repository's own prose and its code disagree, with
**both sides named and an owner** — FR-010. The baseline describes; correcting
the repository is that repository's own change.

**Does not**: a silent correction. gohai's baseline found "65 collectors"
against 62 packages and "9 categories" against 10; recording both sides is what
let a third defect surface, because reconciling the numbers meant reading the
legend that defined a symbol twice.

## 7. What this inventory excludes

**Belongs**: named omissions, each with why. FR-012 requires it of any section
omitted outright, and FR-004's evergreen bound means every baseline excludes
*something* — which is why SC-004 requires this section to be non-empty in all
six.

**Does not**: silence. An unstated omission is indistinguishable from an
oversight, and a reader who cannot tell will either duplicate the work or trust
a gap.

## What checks this

Nothing automatic, and saying so is part of the contract. `just test` checks
formatting and citation resolution, not whether section 3 is architecture or a
call graph. What checks that is review, and the question a reviewer asks is the
test under section 3 above.

[quickstart.md](quickstart.md)'s reading is the indirect check: a reader asked
what a repository is *for* cannot answer it from a call graph, and cannot trace
an edge from a baseline that omitted section 2.
