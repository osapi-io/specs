# Changelog

## Merged Features Log

### A baseline for nats-server — archived 2026-09-30

**Branch:** `001-nats-server-baseline`

**Spec:** [specs/001-nats-server-baseline/spec.md](../../specs/001-nats-server-baseline/spec.md)

**What was added:**

- The project's first memory. It held only a constitution composed from
  `.charter/`.
- What the repository is: a Go library that runs a NATS server **inside its
  consumer's process**. One package, one constructor, no binary — the server it
  starts is a goroutine in somebody else's program.
- The four things `Start()` does, **and the order it does them in**, because two
  of the three findings are consequences of the order.
- That the contract is **mostly not this repository's**: `Options` embeds
  `*natsserver.Options` whole and adds one field, so a change upstream changes this
  package's surface with no commit here. `types.go` is four lines and the most
  consequential file in the repository.
- FR-001 to FR-018 with FR-016a, three user stories, four entities, four edge
  cases, SC-001 to SC-007, AS-001 to AS-004.

**Three things `Start()` decides that a consumer cannot:**

- **Debug and trace are switched on unconditionally** — `SetLogger(wrapper, true,
  true)`, with nothing in `Options` or `New()` able to change either flag.
- **The logger is attached after the server is already running**, so startup
  logging goes to the upstream default logger and a consumer debugging a failed
  start finds their own logger empty.
- **`ReadyTimeout` has no default** — `New()` does no defaulting, and all four
  examples set it explicitly, which is how the absence stays invisible.

**Reading was the method, and that is the transferable part.** The ten counts
reproduced first time and revealed nothing. Every finding came from reading four
statements in sequence: each statement is unobjectionable and the *order* is the
defect. No count reveals an order, and `Start() error` says nothing about when the
logger arrives. A future baseline for a thin wrapper should copy that reading
rather than assuming a short file holds nothing.

**One claim was narrowed before archival.** The specification said all three facts
were stated in none of the five documentation pages. Two are partly documented, and
the refinement is what is archived: `logging.md` documents where trace output lands
but not that it is unconditional, and `configuration.md` documents `ReadyTimeout`
but cannot record that it has no default — **its table has no Default column at
all**, so the omission is structural rather than careless.

**New Components:**

- None. No Go code changed and nothing in the `nats-server` repository changed.

**Gaps, with owners:** all three findings are `nats-server`'s, and each implies a
change it must make — a flag for debug and trace, attaching the logger before the
goroutine starts, and a default for `ReadyTimeout`. Naming the change is not making
it. Worth knowing: **osapi embeds this server and osapi's own baseline does not
mention any of the three.**

**The SC-001 reading passed three of three** — the first clean reading in the
programme. It reported that the logging answer is assembled from four places rather
than stated in one, and that the amendment paragraphs narrowing FR-014 and FR-016a
sit directly under the bolded requirement sentences where a skimming reader could
miss them. It also judged the document to read as **one argument rather than a
checklist with footnotes**, which is a different verdict from the two baselines
before it.

**Tasks Completed:** 17/17 tasks
