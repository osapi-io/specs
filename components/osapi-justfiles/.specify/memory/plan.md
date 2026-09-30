# How this was established

Everything in `spec.md` came from reading the five `.just` files, the root
justfile, and every consumer's `fetch` recipe. The six README files were read
last and only for what they omit.

## The order

The files first. Counts next, and the recipe count twice: once by grep for
headers and once by `just --summary` per module, compared per module rather than
in total, because two wrong numbers can sum to a right one. Prose last.

Reading the READMEs first would have produced a plausible account of what the
modules are for and would have missed the unprefixed `run` recipe, the
pinned-inner-floating-outer version shape, and the self-consumption asymmetry.
None of the three appears in any README.

## The one decision worth recording

The seven-section shape asks for "the contract", and the word reads as though it
presumes exported symbols. This repository exposes none.

Three readings were available. Omitting the section would have recorded an
absence that is not there and taught the programme that a repository without code
has no contract. Reading "contract" narrowly as exported symbols reaches the same
place. Reading it as **what a consumer may depend on** is what was taken, and 38
recipe names with 20 variable names pass every test that matters: a consumer
depends on them, renaming one breaks them at their next fetch, and nothing in the
repository declares them.

That widens the word for every baseline after this one, so the bound is stated:
**something a consumer's build breaks on.**

## What the checks found

A count written as "about twenty" when it was exactly 20 and enumerable from the
table two paragraphs away, with no measurement row for it at all.

A consumer list that said six when the command beside it returns seven. `specs`
fetches two modules, and it was missing because the list was written from the six
*components* rather than from what `gh repo list` returns. **That list was wrong
when written, not stale.** Ageing was not the problem.

Five modules named in three places and explained in none, so a reader had to
infer each one's purpose from its recipe prefixes.

## What the checks cover

`just memory-check` runs every command in the measurement table. It does not
cover whether a recipe does what its name suggests, or whether the modules are
what the consumers need.

One entry nearly went in as a limitation: that a variable read without an
assigned default would not appear in the variables table. Writing it down was
enough to notice it was testable, and one command settled it. **A limit that can
be tested is not a limit, it is a check nobody ran.**

## Revisions

Seeded 2026-09-30 from `specs/001-justfiles-baseline/`. Rewritten the same day
into documentation. That baseline was taken sixth of twelve deliberately, to test
the seven-section shape against a repository with no code before four more were
written to it.
