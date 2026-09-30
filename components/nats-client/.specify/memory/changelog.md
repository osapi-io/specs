# Changelog

## Merged Features Log

### A baseline for nats-client — archived 2026-09-30

**Branch:** `001-nats-client-baseline`

**Spec:** [specs/001-nats-client-baseline/spec.md](../../specs/001-nats-client-baseline/spec.md)

**What was added:**

- The project's first memory. It held only a constitution composed from
  `.charter/`, which states what binds every repository and nothing about this one.
- What the repository is — a Go library wrapping the upstream NATS client, one
  package, one constructor, no binary — and what it **adds**, which is the only
  part a consumer cannot read in NATS' own documentation.
- That it **does not hide NATS**: upstream types reach a consumer through the
  wrapper's signatures, so it is a convenience layer rather than an abstraction.
  Nothing in the repository says so, which is FR-015's gap.
- That it adds **no reconnection behaviour** — no reconnect options, no handlers —
  so the upstream default governs and a consumer is never notified of a drop or a
  recovery. FR-012a.
- Where it sits: no dependencies inside the organization, one consumer, and the
  break **delayed rather than absent** because osapi pins a commit not a tag.
- The contract: one constructor, 25 `Client` methods, 9 exported types, three
  authentication modes, and what it does not promise.
- FR-001 to FR-018 with FR-012a and FR-012b, three user stories, four entities,
  four edge cases, SC-001 to SC-007, AS-001 to AS-004.

**Three of its own claims were wrong, and how each was found matters:**

- The documentation page count returned **9** instead of 8 — `docs/node_modules/`
  holds a vendored README. `system`'s 002 recorded 8 and was right.
- The exported-type count returned **23** instead of 9 — fourteen `*TestSuite`
  types live in `_test.go` files, overstating the contract by more than half, in
  the direction that reads plausible.
- **An acceptance scenario promised that the connection-drop behaviour was
  stated, and nothing stated it.** The scenario asserted a conclusion the code had
  not been consulted about, and it read as the test rather than as the assertion
  under test — the worst place for an unverified claim.

The first two were caught by **running a command**. The third could not have been:
no count was wrong, a claim was, and only a reader asking the question found it.
That is what SC-001 is for and why it is a reading rather than a grep. **Re-reading
the specification found none of the three.**

**What it inherited, and whether inheriting worked:**

- The seven section names were copied from `osapi-justfiles`' **corrected** file
  rather than re-derived — exactly the propagation its FR-021a predicted, and
  because the correction landed first the drift did not reach here. FR-018.
- The dependency edge was verified from **both ends** before being written down,
  the habit that baseline lacked when it listed its consumers from one frame.

**New Components:**

- None. No Go code changed and nothing in the `nats-client` repository changed.

**Gaps, with owners:** no published tags, so a consumer cannot name a version
(`nats-client`, with a bump in `osapi`); the undocumented upstream-type leak
(`nats-client`, if it chooses to say so); and this baseline's own three errors,
recorded rather than fixed away.

**Unresolved, and not this project's:** the SC-001 reading judged the document to
read as a checklist with footnote-style prose attached to each line rather than as
continuous prose. `osapi-justfiles`' reading returned the same judgement, and both
belong to `system`'s 002 — one document carrying an inventory and a shape finding
serves the first reader worse.

**Tasks Completed:** 16/16 tasks
