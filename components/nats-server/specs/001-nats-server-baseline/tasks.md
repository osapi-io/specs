______________________________________________________________________

## description: "Task list for the nats-server baseline"

# Tasks: A baseline for nats-server

**Input**: Design documents from
`components/nats-server/specs/001-nats-server-baseline/`

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md) — both written in this
branch

**Tests**: none. There is no code. What stands in is ten commands, **one reading
of four statements in sequence**, and a reader's reading.

## The second task is the one that matters

The ten commands found nothing interesting: ten figures, all unremarkable, all
reproducing first time. Every finding in this baseline came from **T007**, which
reads `Start()` in order rather than counting anything.

No count reveals an order, and no signature does either — `Start() error` says
nothing about when the logger arrives. So T007 is a reading and is marked as
one, and a future baseline for a small wrapper should copy it rather than
assuming that a short file holds nothing.

**Nothing lands in the `nats-server` repository.** T013 verifies that.

______________________________________________________________________

## Phase 1: Setup

- [ ] T001 Confirm the measurements are against the commit the specification
  names: `git -C ~/git/osapi-io/nats-server log --oneline -1` shows `7ac142e` or
  later. A figure that has moved is recorded as a new measurement with its date.

______________________________________________________________________

## Phase 2: Foundational — the counts, which are the easy half

Run from `~/git/osapi-io/nats-server`. Each command is from FR-016.

- [ ] T002 The Go counts: `find . -name '*.go' -not -path './.git/*' | wc -l` →
  `12`, and with `-not -name '*_test.go'` → `10`.
- [ ] T003 The package's shape and surface, tests excluded: 4 non-test files, 1
  exported function, 8 exported methods (2 on `Server`, 6 on `SlogWrapper`), 4
  exported types, 1 interface.
- [ ] T004 [P] The documentation and example counts: 5 pages with the
  `node_modules` exclusion, 58 README lines, 4 runnable examples. The exclusion
  is unnecessary here and carried on purpose — `nats-client`'s baseline got that
  count wrong for want of it, and two sibling baselines using different commands
  invites a reader to wonder which is right.

______________________________________________________________________

## Phase 3: User Story 1 — a consumer knows what embedding costs them (Priority: P1)

- [ ] T005 [US1] Confirm FR-002 states the four things the package does rather
  than what it exposes. A wrapper this thin is described by what it decides, not
  by its surface.

- [ ] T006 [US1] Confirm FR-007 states the **order** `Start()` performs those
  four things in, because two of the three gaps are consequences of the order
  and neither is visible from a signature.

- [ ] T007 [US1] **Read `pkg/server/server.go`'s `Start()` in order** and
  confirm all three findings against it:

  1. `SetLogger(slogWrapper, true, true)` — debug and trace are literals, and
     nothing in `Options` or `New()` can change them. FR-014.
  2. The `SetLogger` call comes **after** `go natsServer.Start()` and after
     `ReadyForConnections`, so startup logging never reaches the consumer's
     `slog`. FR-015.
  3. `New()` performs no defaulting, so an unset `ReadyTimeout` reaches
     `ReadyForConnections` as a zero duration. FR-016a.

  **This is a reading, not a command.** Three greps confirm each fact once you
  know to look — `grep -rn 'SetLogger' pkg/server/*.go` finds one call site,
  `grep -rn 'ReadyTimeout' pkg/server/*.go` finds a declaration and a use and no
  default — but nothing produces the findings from scratch. Record that, because
  the temptation on the next thin wrapper will be to trust its size.

- [ ] T008 [US1] Confirm all three facts are absent from all five documentation
  pages, and that the pages covering those subjects are `configuration.md`,
  `lifecycle.md` and `logging.md` — the three the findings fall under. Grep each
  page for `SetLogger`, `trace`, `ReadyTimeout` and `default`.

- [ ] T009 [US1] Run the SC-001 reading. Give somebody who has not opened
  `pkg/server` the specification alone and three questions: what does `Start()`
  do and in what order; what logging will a consumer get; and what must they set
  in `Options`? **The second is the one to watch** — a reader who learns only
  that logging is routed into `slog`, and not that debug and trace are forced on
  and startup is missed, has been told the reassuring half. A person is
  preferred; a fresh agent given only `spec.md` is the fallback. **Record what
  it proves and what it does not.**

______________________________________________________________________

## Phase 4: User Story 2 — the contract is mostly somebody else's (Priority: P1)

- [ ] T010 [US2] Confirm FR-011 states that `Options` **embeds**
  `*natsserver.Options` rather than wrapping or copying it, and what follows: a
  consumer can reach every upstream option through it, and a change upstream
  changes this package's surface with no commit here. Verified in
  `pkg/server/types.go`, which is four lines long and is the most consequential
  file in the repository.
- [ ] T011 [US2] Confirm the single edge from **both ends** — `go.mod` here and
  `osapi/go.mod` — and that FR-004 states **when** a break arrives: at the bump,
  not at the change, because osapi pins a commit.
- [ ] T012 [US2] Confirm FR-013 states what the contract does **not** let a
  consumer decide. A contract stated only as what it offers is half a contract
  when two of its decisions are unreachable.

______________________________________________________________________

## Phase 5: User Story 3 — the two NATS baselines read as a pair (Priority: P2)

- [ ] T013 [US3] Confirm the seven section names are 002's verbatim and all
  seven are present in order — FR-018 and SC-005. These were inherited from
  `nats-client`'s baseline, which inherited them from `osapi-justfiles`' after
  that one recorded three drifting. **Two hops without drift** is the first
  evidence the correction holds rather than merely having been made once. Also
  confirm nothing changed in the inventoried repository:
  `git -C ~/git/osapi-io/nats-server status --porcelain` is empty.
- [ ] T014 [US3] Read `nats-client`'s baseline and this one back to back and
  confirm a reader can see that the two wrap opposite ends of the same library.
  This is the pair test, and it is the smallest version of the programme's whole
  purpose — SC-001 of `system`'s 002 asks it of all six.

______________________________________________________________________

## Phase 6: Verification and archival

- [ ] T015 Run `cd specs && mise exec -- just test` — SC-006.
- [ ] T016 Run `speckit-archive-run specs/001-nats-server-baseline` once this
  branch has merged. This project's memory holds only a constitution, so the run
  **seeds** rather than folds.
- [ ] T017 Mark `system`'s 002 as having unit 8 done. Remaining after it:
  `osapi-orchestrator` (unit 9, the largest), gohai's amendment (unit 10), and
  two moves.

______________________________________________________________________

## Dependencies & Execution Order

- **T007 blocks Phase 4 and Phase 5** in substance rather than mechanically: the
  three findings are what make FR-013 and FR-014 through FR-016a checkable.
- **T009 should run before T008** if only one can. A reader who has been shown
  which pages omit the facts is no longer a reader who has seen nothing else.
- **Phase 6** is last; T016 needs this branch merged.

## Notes

- No Go code changes. No change of any kind in `nats-server`.
- Every gap here implies a change this repository must make — a flag for debug
  and trace, attaching the logger before the goroutine starts, a default for
  `ReadyTimeout` — and naming the change is not making it.
- osapi embeds this server and **osapi's own baseline does not mention any of
  the three facts either**. Worth knowing when reading the pair.
