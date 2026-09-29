# Changelog

## Merged Features Log

### The job system — amended 2026-09-28

**Source:** the SC-001 reading, `specs/004-job-system/tasks.md` T015

The reading that closed 004 handed the specification a reader who had seen
nothing else, and two requirements did not survive it. Both are corrected here
rather than in the pull request that archived the feature, because a merged
statement is amended in its own change.

- **FR-045 and FR-046 named their clocks without giving their durations.**
  `controller.api.job_timeout` and `DefaultCommandTimeout` appeared as
  identifiers with citations, where the neighbouring requirements state
  `MaxDeliver: 5`, `AckWait: 2m` and `1h` as numbers. A reader could learn that
  two clocks exist and not how long either one runs, which is short of what the
  requirement claims to answer. Now `30s` and `10m`.
- **FR-054 is new: nothing stated what happens once `MaxDeliver` is exhausted.**
  The delivery requirements described at-least-once and stopped at its terminal
  case. The dead letter queue holds the JetStream advisory, not the job — a
  distinction worth stating, since the job itself stays in `job-queue` under that
  bucket's TTL.

Three further findings from the same reading were not acted on: no TTL is stated
for the `job-responses` bucket, and broadcast ordering and payload versioning are
subjects 004 never claimed.

### The job system — archived 2026-09-28

**Branch:** `004-job-system`

**Spec:** [specs/004-job-system/spec.md](../../specs/004-job-system/spec.md)

**What was added:**

- How work reaches an agent, stated in the corpus: a job is stored under
  `jobs.{job-id}` before it is announced, the notification carries an ID rather than
  content, and status is append-only events computed by priority.
- The delivery guarantee, and the obligation it creates. At-least-once, not
  at-most-once, so an agent checks for a recorded response before executing — and the
  operations that make that load-bearing rather than theoretical are named.
- The two clocks that bound a job, which bound different things: how long the
  controller waits, and how long the work may run. With the backstop for a command
  that sets no deadline, and the fact that cancelling the request stops neither.
- Four per-host statuses and a machine-readable cause beside each message, including
  why a host that never answered reports `timeout` rather than `failed`.
- 430 lines left `docs/docs/sidebar/architecture/job-architecture.md`, whose
  remaining 203 are for somebody running jobs. Its address is unchanged and four
  inbound links now describe what it holds.
- The `add-a-domain` skill's delivery-semantics section became seven citations.

**Three corrections:** the published site had drifted from the code, and each
disagreement is recorded rather than quietly resolved.

- The job key is `jobs.{job-id}`; the page said `{status}.{uuid}`, which described
  the status-event keys as though they were the job key. FR-033.
- The consumer defaults are `MaxDeliver` 5 and `AckWait` 2m; the page said 3 and 30s.
  FR-043.
- One TTL of `1h` covers the `job-queue` bucket; the page said 24 hours for completed
  and failed jobs. FR-050.

None was corrected in place on the page. Correcting a number in two places is how it
drifted the first time, and a configured value's statement of record is the
configuration file.

**New Components:** none. No Go code changed; this states what the code already does.

**Tasks Completed:** 16/18 — T011 and T017 are bookkeeping that this archival
completes; T015, the reading with somebody who has not seen the page, is the one task
an author cannot run on their own work.

**Bugs addressed:** none. Three documentation gaps, recorded above.

### Per-agent public key store — archived 2026-09-26

**Branch:** `002-agent-key-store`

**Spec:** [specs/002-agent-key-store/spec.md](../../specs/002-agent-key-store/spec.md)

**What was added:**

- The controller keeps each accepted agent's public key beyond the enrollment
  request that carried it, written only by acceptance and removed on rejection.
- Job responses are verified against that key before they count as a result, with
  three distinguishable causes for refusal and no path that accepts an unverified
  response.
- Agents sign the routing fields of their registration — machine ID, hostname,
  fingerprint, state and labels — and only a verified registration decides where
  work goes. A contested hostname resolves deterministically.
- Rotation keeps a replaced key acceptable for a bounded grace period; removal
  takes effect at once.
- The fleet view reports whether a key is stored and whether the last registration
  verified, so a rollout can be staged before enforcement is enabled.
- Enforcement is opt-in per side and governed by the existing PKI switches.

**New Components:**

- `internal/controller/enrollment/keystore.go` and `keystore_adapter.go`
- `internal/job/registration.go`
- `AgentKey`, `AgentKeyStore` and the rejection causes in `internal/job/client`

**Tasks Completed:** 40/41 tasks — T040 not run, since walking the quickstart
needs a live controller and agent.

**Bugs addressed:** GHSA-3jh4-v775-58vr, GHSA-j73r-9f42-4pv5 (fixed on main;
both remain draft until a release names a patched version)

### Provider contract — archived 2026-09-26

**Branch:** `001-provider-contract`

**Spec:** [specs/001-provider-contract/spec.md](../../specs/001-provider-contract/spec.md)

**What was added:**

- The provider contract as a corpus statement: what a provider is, the operation
  set and its context-first convention, the three idempotency outcomes, the
  unsupported outcome, the four implementation patterns, platform selection,
  facts injection, the provider-side validation boundary, filesystem and command
  access, and the testing obligations belonging to the contract.
- The rule that the `add-a-domain` skill cites these requirements rather than
  restating them (FR-016), which the skill's provider reference now follows.

**New Components:**

- None. No Go source changed; the fourteen node providers and their categorized
  siblings already conformed.

**Tasks Completed:** no tasks.md — the feature was specified and stated, not
implemented.
