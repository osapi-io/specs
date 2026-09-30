# How this was established

Everything in `spec.md` came from reading gohai's code, with its prose used only
to find disagreements.

## The order

Code first: `internal/collector/collector.go` for the interface and the category
constants, `internal/collector/registry.go` for the exported surface and the
dependency handling, `pkg/gohai/gohai.go` for registration. Counts next, each by
a command. Prose last.

Reading the README first would have produced an inventory stating 65 collectors
across 9 categories. Both figures were wrong in that framing, and the code says
62 implemented and 10 categories.

## What that order found

Two disagreements between gohai's prose and its code, and a third that only
surfaced while reconciling the first.

The README and the catalogue both said nine categories. Ten constants are
declared and all ten are in use, so nine was wrong rather than differently
scoped.

The catalogue tabulated 65 rows against 62 packages. That one is a definition
rather than an error: 65 counts deliberately unimplemented entries and 62 counts
what exists.

Reconciling those two meant reading the catalogue's legend, which defined one
marker twice, once as implemented and tested and once as planned. 62 of 65 rows
carried it, so the column could not be read. Nobody was looking for that.

All three are fixed in gohai by gohai#201.

## What the checks cover

`just memory-check` runs every command in the measurement table. Two of those
commands check separate things that happen to agree: 62 implemented packages and
62 registered collectors. A collector can exist without being registered, and
that pair is what would catch it.

The checks do not cover how any individual collector gathers its facts, and this
document deliberately does not either. There are 62 of them and one contract.

## Revisions

Seeded 2026-09-29 from `specs/001-gohai-baseline/`. Rewritten 2026-09-30 into
documentation. That baseline predates the seven section shape `system`'s 002
fixes and carries no dependency or architecture section of its own, which 002
records as an amendment still owed.
