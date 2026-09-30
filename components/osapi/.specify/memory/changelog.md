# Changelog

## Merged Features Log

### The embedded UI — archived 2026-09-29
**Branch:** `007-the-embedded-ui`
**Spec:** [specs/007-the-embedded-ui/spec.md](../../specs/007-the-embedded-ui/spec.md)

**What was added:**
- The UI stated for the first time. Memory held 1,840 lines about osapi and nothing
  about the part of it a user actually sees: what it is, how it reaches a browser,
  what separates its four kinds of component, that its client is generated from the
  same specification as the Go SDK, and that it decodes a JWT without verifying it.
- Two requirements that came from the code rather than either prose document — the
  unverified decode, and `/ui/` sitting in `.coverignore` so the coverage gate says
  nothing about the UI.
- The record of a **prose-versus-prose** divergence, which is new ground: two
  documents stating the same architecture, edited eighteen days apart, each holding a
  section the other never got. Carried forward as a union rather than by picking a
  winner, because recency tracks editing and not accuracy.
- A **third disposition** for a document: a pointer, kept for its location rather
  than its content. One file in the programme has it.
- US14 and US15, FR-095 through FR-112, four entities, three edge cases, SC-026
  through SC-029, and AS-023 through AS-026.

**New Components:**
- None. No Go code changed; the diff is markdown in two repositories.
- `ui/` appears in the plan's structure for the first time, with the boundary its
  four component kinds are placed against.

**Folded:** an operator story into US11, a split-page edge case into the backfill's
same-paragraph case, and three outcomes into SC-016, SC-021 and SC-024, each of which
already generalised past the subject that wrote it.

**Corrected before archival:** three of the feature's own claims, each found by a
different one of its own checks and none by re-reading the specification — a grep
found a fourth copy of the architecture the classification had missed, a line count
found the pointer at ten lines against a criterion of under ten, and the reading found
FR-004 requiring a statement it did not make.

**Not fully passed:** SC-026's reading answered two of its three questions, and has
not been re-run since FR-004 was fixed. SC-016's grep failed on its first run and
passes now.

**Implementation:** osapi-io/osapi#549 and #550; specified at osapi-io/specs#172,
planned at #173, verified at #174, corrected at #175 and #176.

**Tasks Completed:** 16/16 tasks

### The corpus backfill — archived 2026-09-28

**Branch:** `003-corpus-backfill`

**Spec:** [specs/003-corpus-backfill/spec.md](../../specs/003-corpus-backfill/spec.md)

**What was added:** the method, not the content. Its two subjects carried the
knowledge and were archived first; what is recorded here is how knowledge gets moved
and what stops it drifting afterwards.

- Twelve rules as FR-082 through FR-093: classify by who reads a page, group by
  subject rather than by page, keep every address resolving, cite rather than
  restate, one statement per rule, and check a rule against the code before writing
  it down.
- The citation contract, in the plan: the shape a citation must have and the four-level
  relative depth the skill linter enforces, with the one sanctioned exception for a
  site page that cannot link relatively into another repository.
- Two redirected addresses, also in the plan.

**New Components:** none. No Go code changed across the whole backfill.

**Folded rather than duplicated:** two of its user stories and four of its outcomes
folded into entries its own subjects had already put in memory — the operator story,
the one-home story, and the outcomes about reading from the corpus, citing the code,
one statement per rule, and addresses resolving. Four of those folds widened the
existing entry from one subject to the general case. That is what a method feature
archived after its subjects should look like, and the alternative would have been
twelve near-duplicates.

**What it got wrong about itself:** three page inventories, corrected before archival.
Every line count was right; the count of items inside two pages was taken from prose
rather than measured, which is the failure FR-090 exists to catch, in the record of the
feature that states it.

**Tasks Completed:** 29/29 tasks

### Building a domain — the SDK naming convention, 2026-09-28

**Source:** FR-073's remaining gap, closed by deriving the rule rather than inventing it

FR-073 established that three documents deferred to an `sdk-standards` capability
nobody wrote, and that one of its four subjects — method naming — was stated nowhere
at all. That gap is now closed, and it was closed the only honest way available: by
reading the 31 services and roughly 110 exported methods in `pkg/sdk/client/` and
writing down what they already do.

FR-094 states five rules — the five exact CRUD verbs, a bare verb for the service's
own resource, verb-then-object for a sub-resource, `Get` where a service has exactly
one read, and verb-then-object where it has several — and names **seven methods to be
renamed** so that nothing is left as a permitted exception.

The first draft of this recorded four of them as permitted deviations instead. Two of
those four were misread: `File.Stale` and `File.Changed` were called predicates
answering a question about state, which is what their *names* suggest and not what
their signatures say — they return a list and a single record. FR-090 requires a rule
checked against the code before it is written down, and this is that requirement
failing against the analysis that stated it, one day after it was written.

Renaming rather than excepting is affordable precisely now: the SDK carries no
released version and its one external consumer pins a pseudo-version commit, so the
whole cost is twenty-six call sites in osapi and three in the orchestrator. After the
first tag they are breaking changes.

### Building a domain — amended again 2026-09-28

**Source:** closing out FR-073's gap, and correcting the correction

Two things, and the second is a correction of this project's own earlier fix.

- **The `sdk-standards` claim had three copies, not two.** FR-073 named the site's
  domain page and the skill's `references/sdk.md`. The site's SDK guidelines page
  carried it too, found while checking that no operator page points into the corpus.
  All three now name it as unwritten.
- **One of the deferral's four subjects has no rule anywhere.** It named method
  naming, type exposure, result-field tags and error handling. The last three are
  real and stated as FR-074, and the guidelines page shows each working. Method
  naming is stated nowhere — not in the corpus, not on that page, not in the
  capability nobody wrote. The replacement text written for the guidelines page
  listed it among the rules FR-073 and FR-074 state, which was itself an overclaim of
  the same kind, smaller, and is corrected.

So the missing authority was never a document that would have collected existing
rules. For one of its four subjects there was nothing to collect, which is a more
useful thing to know than "a capability is missing".

**Where the remainder belongs:** this project, not `system`. `osapi-orchestrator` does
depend on `osapi`, so the cross-repository claim was true in substance, but the SDK is
osapi's own public API and the orchestrator consumes it — osapi's behaviour rather than
an agreement between repositories. A method-naming convention is worth stating once
somebody decides what it is, rather than inferring one from the method names that
happen to exist.

### Building a domain — amended 2026-09-28

**Source:** the SC-001 reading, `specs/005-building-a-domain/tasks.md` T021

The reading that closed Subject B was given the specification and nothing else, and
three things did not survive it. All three are corrected here rather than in the pull
request that archived the feature, because a merged statement is amended in its own
change.

- **FR-081 is new: nothing stated a domain's test obligations.** Tests were named
  among the seven artifact kinds a domain contributes, and every other kind had a
  requirement — the CLI, the SDK, handler registration. The deferral to osapi's
  `CONTRIBUTING.md` was real and recorded in the feature's data model; it was simply
  not in the specification, so a reader of that alone saw an omission rather than a
  deferral.
- **FR-061 now reconciles the six layers with the seven artifact kinds.** SDK,
  documentation and tests appeared in one list and not the other, with nothing saying
  why. The layers describe the running system; the artifacts describe what a domain
  adds to it, and three of them are not layers at all.
- **FR-060 now says what makes an operation node-targeted rather than only where its
  code lives.** It is where the work happens: a managed machine by way of the job
  system and a provider, or the controller answering from state it holds. `file`
  exists as both an object-store upload and a host deployment, which is why the test
  has to be functional rather than nominal.

FR-058 also gained one clause: the combined specification is
`internal/controller/api/gen/api.yaml`, assembled by `redocly join`, and it was used
by name without ever being defined.

Three further observations from the same reading were not acted on: the processor
file's expected name, a threshold for "an area expected to grow", and the absence of
a worked end-to-end example are the `add-a-domain` skill's job rather than the
corpus's.

### Building a domain — archived 2026-09-28

**Branch:** `005-building-a-domain`

**Spec:** [specs/005-building-a-domain/spec.md](../../specs/005-building-a-domain/spec.md)

**What was added:**

- What a domain consists of across every layer, and the obligation that makes it
  checkable: a domain appears everywhere an existing domain appears.
- The build order, with the three orderings a tool forces separated from the five
  that are convention. The walkthrough is in the plan; the forced orderings are
  requirements.
- Validation, including the one place a tag does nothing — path parameters in
  strict-server mode.
- Broadcast, the four job-client methods, handler registration, the SDK and CLI
  obligations, and all eight design principles.

**New Components:** none. No Go code changed.

**Gaps recorded rather than fixed:**

- The hostname path-parameter validator is not a shared helper. It is unexported and
  duplicated in three packages, so the call the site named does not compile across
  them. Owner: osapi.
- The `sdk-standards` capability three documents deferred to as binding does not
  exist. Owner: this repository, as a feature of its own.
- The API guidelines page states six guidelines where the backfill recorded five.
- The principles page states eight principles where the backfill recorded five.
- The site's verification step does not cover the documentation step before it.
  Owner: osapi.

The last two are the backfill's own record being wrong about pages it measured
correctly; the line counts matched.

**Tasks Completed:** 22/24 tasks — the independent completeness reading and this
archival were open when it was written.

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
