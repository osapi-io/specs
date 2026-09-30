# How this was established

`spec.md` is the consolidation of seven features archived under `specs/`. Most of
it was decided feature by feature and merged in; the frame around it, what osapi
is and where it sits, came from a baseline written after five of those features
had already landed.

## The order, when it was followed

Code first, counts by command, prose last. Seven counts, each with the command
that reproduces it, and `just memory-check` runs them.

The baseline that added the frame did follow that order. Three of the features
before it did not consistently, and the corpus backfill records what that cost:
its page inventories were right about line counts and wrong about the count of
items inside two pages, because those came from reading about the pages rather
than from the pages.

## What the frame found that five features had not

Three contributor pages had survived the corpus backfill. The backfill named six
candidate pages and classified those, so these three were never candidates and
nothing examined them. Two had no corpus counterpart at all: 464 lines of
contributor architecture on an operator's site with nowhere to cite.

That changed the programme from eleven units to twelve.

Looking wider for the same reason found `ui/docs/architecture.md`, a 263-line
second statement of the site's UI architecture, already diverged. Each copy held
a section the other never got, edited eighteen days apart, and nothing marked the
moment they stopped agreeing. **The drift the one-statement rule exists to
prevent, observed rather than hypothesised.** Resolved by the UI feature, which
took the union rather than picking a winner, because recency tracks editing and
not accuracy.

## Two numbers that are both right

219 published pages and 221 files under `docs/`. A baseline stating one would
leave a reader comparing it against the other and concluding something is broken.
The classification of every page covers the 219.

The classification summed to 217 on its first attempt, two short, because two
pages sit outside the subdirectory counts the table was built from. Two missing
pages in a 219-page classification is invisible to every other check.

## Why the contract section is mostly citation

osapi's contract is already stated across four archived features: the provider
contract, the agent key store, the job system, and building a domain. Restating
any of it in the baseline would have created the second statement the whole
programme exists to end.

That makes osapi's baseline the reverse of every other component's, where the
contract is the substantive part. A reader must not take the brevity for an
omission.

## What this memory was archived out of order

The baseline that says what osapi is had no plan for a day, and the archival gate
requires one, so **six features reached this memory before the one that says what
the repository is.** One of them was the UI feature, whose own specification
depends on the baseline's page classification.

A baseline with no plan is not merely undocumented. It is unarchivable, and
nothing in the workflow says so.

## What the checks cover

Counts. Not whether the page classification is right page by page, not whether
the contract's citations are complete, and not whether the architecture survives
a rename. That last one is only settled by re-reading after a refactor, which is
why it is a judgement rather than a gate.

## Revisions

Consolidated from the provider contract, the agent key store and the job system
in September 2026, then building a domain, the corpus backfill, the SDK naming
convention, the baseline, and the embedded UI. Rewritten 2026-09-30 from
requirement form into documentation.
