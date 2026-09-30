# How this was established

Everything in `spec.md` came from reading `pkg/client`, with the eight
documentation pages used to find what they omit.

## The order

Files first, each for what it holds. Counts next, by command. Prose last.

## What the checks found before anyone read the result

Two counts were wrong on their first run, both because a command lacked an
exclusion rather than because the arithmetic slipped.

The documentation page count returned 9 instead of 8, because
`docs/node_modules/prettier/README.md` is a vendored dependency's file.

The exported-type count returned 23 instead of 9, because fourteen `*TestSuite`
types live in test files. That overstates the contract by more than half, in the
direction that reads plausible.

Both commands now carry their exclusion, and `just memory-check` runs them.

## What no command could have found

A reader asked what happens when the connection drops. Nothing answered, and the
specification's own acceptance scenario had promised the answer was stated.

No count was wrong there. A claim was, and it sat in an acceptance scenario,
which reads as the test rather than as the assertion under test. Reading
`connect.go` settled it: three options pass through, none of them about
reconnection, and no handler is registered.

**A reading catches a different class of defect from a command.** The commands
caught two wrong numbers. The reading caught a promise.

## What the checks cover

Counts, and only counts. Whether the 25 methods are the right 25, whether the
undocumented upstream-type leak matters to a future consumer, and whether the
eight pages are accurate about what they describe are all judgements.

## Revisions

Seeded 2026-09-30 from `specs/001-nats-client-baseline/`. Rewritten the same day
into documentation.
