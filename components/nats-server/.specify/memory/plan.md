# How this was established

Everything in `spec.md` came from reading `nats-server`, not from reading what
`nats-server` says about itself. The order was deliberate, and it is the order to
use again.

## The order

Files first. Each of the four non-test files in `pkg/server/`, for what it holds
and what it calls. Counts next, each by a command rather than by a sentence
claiming one. Prose last, and only to find out what it omits.

Reading the five documentation pages first would have produced a plausible
account of what the package does and would have missed everything worth knowing.
The pages are accurate about what they cover.

## What the reading found that counting did not

The ten counts reproduced first time and revealed nothing. All three limitations
came from reading four statements in sequence inside `Start()`.

Each statement there is unobjectionable. The order is the defect: attaching the
logger after the server is already running means startup logging goes elsewhere,
and no count reveals an order. `Start() error` says nothing about when the logger
arrives.

The same reading found two literal arguments at a call site, and the absence of a
defaulting statement in `New`. A fact about what is not there.

**A thin wrapper is worth reading rather than counting.** It either saves its
consumer the lines it wraps or decides something for them, and only the code says
which.

## What the checks cover

`just memory-check` runs every command in the measurement table and fails when a
value moves. That covers the counts.

It does not cover whether the three limitations still hold, whether a recipe does
what its name suggests, or whether the five documentation pages are accurate
about what they do describe. A reading covers those, and a reading is a person's
judgement.

## Revisions

Seeded 2026-09-30 from `specs/001-nats-server-baseline/`. Rewritten the same day
from requirement form into documentation, after the archival had copied the
feature specification's user stories and success criteria into memory and phrased
every statement as an obligation.
