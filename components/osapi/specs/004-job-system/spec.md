# Feature Specification: The job system

**Feature Branch**: `004-job-system`

**Created**: 2026-09-28

**Status**: Archived 2026-09-28

**Input**: Subject A of [003-corpus-backfill](../003-corpus-backfill/spec.md) —
"the job system MUST be the first subject moved, because it is the largest body
of contributor knowledge on the site and the one the `add-a-domain` skill leans
on most" (FR-005).

This states how work reaches an agent and what is guaranteed about it, so that a
contributor or an agent can answer that from the corpus rather than from a page
written for somebody running osapi. It replaces the contributor half of
`docs/docs/sidebar/architecture/job-architecture.md`, whose operator half stays
on the site.

Every requirement cites the code it describes, per 003's FR-011. Three of them
correct what the page said, because the page had drifted — recorded as gaps
rather than restated, per 003's FR-009.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor adds an operation and knows what they are handed (Priority: P1)

Somebody adding an operation to a domain needs to know what carries their
request, what the agent is guaranteed to receive, and what the system does to
them if the network hiccups. They read this, and they know before they write.

**Why this priority**: it is the reason the subject moves first. Every domain
added to osapi passes through this system, and until this is stated the
`add-a-domain` skill either restates it or sends the reader to a page written
for an operator.

**Independent Test**: given this specification alone, a reader can say which
store holds a job, which store holds its result, what a second delivery obliges
the agent to do, and what bounds how long the work may run.

**Acceptance Scenarios**:

1. **Given** this specification, **When** a contributor asks how a request
   becomes work an agent runs, **Then** the path — store, notify, fetch,
   execute, record — is stated with the code that implements each step.
2. **Given** this specification, **When** a contributor asks what happens when
   the same job arrives twice, **Then** the obligation is stated as an
   obligation, not as an observation about the current implementation.
3. **Given** this specification, **When** a contributor asks what an operation
   may assume about time, **Then** the deadline, the backstop and what
   cancellation does not reach are all stated.

______________________________________________________________________

### User Story 2 - An agent implementer knows what the system will not do for them (Priority: P1)

Somebody writing the agent side needs the obligations: what to check before
executing, what to write and when, what to acknowledge, and which failures are
theirs to handle rather than the system's to retry.

**Why this priority**: equal to the first. The delivery guarantee is weaker than
it looks, and an implementer who assumes at-most-once will execute a reboot
twice.

**Independent Test**: given this specification alone, a reader can state what
the agent must check before running an operation, what it must record before
acknowledging, and which of a failure's causes it must not retry.

**Acceptance Scenarios**:

1. **Given** the specification, **When** an implementer asks what to do with a
   redelivered message, **Then** the check that makes re-execution unnecessary
   is stated, along with what happens when the response cannot be written.
2. **Given** the specification, **When** an implementer asks which failures
   terminate the message rather than letting it redeliver, **Then** the list is
   stated with its reason.

______________________________________________________________________

### User Story 3 - A rule that was wrong on the site is not wrong in the corpus (Priority: P2)

Somebody reading a number in the corpus — a timeout, a delivery count, a key
format — finds the number the code uses, or an explicit statement that the two
disagree.

**Why this priority**: lower than the two above, but it is what makes this a
specification rather than a copy. Three of the page's statements were already
untrue when this was written.

**Independent Test**: for each number and key format stated, the cited code says
the same thing, or the requirement records the disagreement.

**Acceptance Scenarios**:

1. **Given** a requirement naming a configured value, **When** the cited file is
   opened, **Then** it holds that value or the requirement says it does not.
2. **Given** a value the page stated wrongly, **When** the corpus is read,
   **Then** the correction is visible as a correction rather than silently
   different.

### Edge Cases

- A configured value has a default in code and a different value in the shipped
  config file. Stating one hides the other, so a requirement about a configured
  value names the default and the file that may override it.
- An operation is not idempotent and cannot be made so — `command.exec`,
  `power.reboot`. The delivery guarantee cannot be strengthened for them, so the
  obligation lands on the agent, and the specification has to say which side
  owns it.
- A job outlives the controller's patience. Two clocks run, and the
  specification must say what each bounds, because an operator reading "timed
  out" will otherwise conclude the work did not happen.
- A subject prefix is configurable per namespace, so a stated subject is a shape
  rather than a literal.

## Requirements *(mandatory)*

### Functional Requirements

#### How work reaches an agent

- **FR-001**: A job MUST be stored before it is announced. The definition is
  written to the `job-queue` KV bucket under `jobs.{job-id}`, and only then is a
  notification published to the `JOBS` stream. Evidence:
  `internal/job/client/client.go` — `kvKey := "jobs." + jobID`, then the publish
  that follows it.
- **FR-002**: The notification MUST carry the job's identity rather than its
  content. An agent receives an ID on a subject and fetches the definition from
  KV. Evidence: `internal/job/client/client.go`, and the agent's fetch in
  `internal/agent/handler.go`.
- **FR-003**: Status MUST be recorded as append-only events rather than as a
  mutated field. Each event is its own key,
  `status.{job-id}.{state}.{source}.{unix-nano}`, and the job's status is
  computed from them by priority. Evidence: `internal/job/client/jobs.go` and
  `internal/job/client/agent.go` for the key shape; `job.StatusPriority` in
  `internal/job/types.go` for the computation.
- **FR-004**: The corpus MUST state that the job definition key is
  `jobs.{job-id}`, and MUST record that the published site said
  `{status}.{uuid}` — a shape the code does not use. **Gap**: the page described
  the status-event keys as though they were the job key. Evidence:
  `internal/job/client/client.go` against
  `docs/docs/sidebar/architecture/job-architecture.md`.
- **FR-005**: Results MUST be stored separately from the job, in the
  `job-responses` bucket, so a caller reading a result does not read the job's
  history to find it. Evidence: `internal/config/nats.go` declares both buckets.

#### Routing

- **FR-006**: Operations MUST be routed by a dot-notation subject under one of
  two prefixes, `jobs.query` for reads and `jobs.modify` for writes, so that a
  consumer can subscribe to one class of work without filtering the other.
  Evidence: `JobsQueryPrefix` and `JobsModifyPrefix` in
  `internal/job/subjects.go`.
- **FR-007**: The subject prefix MUST be treated as namespaced rather than
  literal. `internal/job/subjects.go` builds both prefixes from a base that a
  deployment can change, so a corpus statement naming `jobs.query` names a
  shape.
- **FR-008**: A target MUST be resolvable as a hostname, a machine ID, a
  broadcast (`_all`, `_any`) or a label selector, and the rules that decide
  which agents a broadcast expects MUST be stated. Evidence:
  `internal/job/subjects.go`, `job.ExpectedAgentHostnames`.

#### What is guaranteed, and what is not

- **FR-009**: The corpus MUST state that delivery is at-least-once, not
  at-most-once, and MUST state the obligation that follows: before executing, an
  agent checks whether it has already recorded a response for that job, and if
  it has, acknowledges without re-executing. Evidence: `HasJobResponse` in
  `internal/job/client/types.go`, used in `internal/agent/handler.go`.
- **FR-010**: The corpus MUST state which operations make this obligation load-
  bearing rather than theoretical: `command.exec`, `command.shell`,
  `power.reboot` and `power.shutdown` are not safe to run twice. Evidence: the
  Error Handling section of the site page, which states this correctly, and the
  operations in `internal/agent/processor_command.go`.
- **FR-011**: The corpus MUST state that a job which has run is terminal: the
  agent acknowledges after recording a response, success or failure, so a failed
  operation is not retried by redelivery. Evidence: `internal/agent/handler.go`.
- **FR-012**: The corpus MUST state what happens when the response cannot be
  written after the operation ran — the failure is recorded best-effort and the
  message is still acknowledged, because leaving it unacknowledged would
  redeliver it and run the operation a second time. Evidence:
  `internal/agent/handler.go`.
- **FR-013**: The corpus MUST state which failures terminate a message instead
  of letting it redeliver — a malformed payload, an unparsable subject, a failed
  signature — and why: none of them can succeed on retry. A failure to read the
  job data itself is treated as possibly transient and left to redeliver.
  Evidence: `internal/agent/handler.go`.
- **FR-014**: The corpus MUST state the consumer's delivery settings as defaults
  that a deployment may override, and MUST record that the published site stated
  different values. **Gap**: the page said `MaxDeliver: 3` and `AckWait: 30s`;
  the defaults are `5` and `2m`. Evidence: `cmd/root.go` —
  `agent.consumer.max_deliver` 5, `agent.consumer.ack_wait` 2m — and
  `configs/osapi.yaml`, which sets the same values; consumed in
  `internal/agent/consumer.go`.
- **FR-015**: The corpus MUST state that an operation outliving `AckWait` is not
  redelivered mid-flight, because the agent extends the deadline while it runs.
  Evidence: the in-progress keepalive in `internal/agent/handler.go`.

#### Time

- **FR-016**: The corpus MUST state that two clocks bound a job and that they
  bound different things: `controller.api.job_timeout` bounds how long the
  controller waits for a response, and the agent's command deadline bounds how
  long the work itself may run. Evidence: `cmd/root.go` for the default,
  `internal/job/client/client.go` for the wait, `internal/exec/types.go` for the
  command deadline.
- **FR-017**: The corpus MUST state that a command with no deadline of its own
  is bounded by a backstop rather than left to run forever, and MUST name it.
  Evidence: `DefaultCommandTimeout` in `internal/exec/types.go`.
- **FR-018**: The corpus MUST state that cancelling the originating API request
  does not stop a running agent operation, and that `job delete` removes the
  queue entry rather than the process. An operation is stopped by its own
  deadline, the backstop, or the agent shutting down. Evidence:
  `internal/job/client/client.go`, `internal/exec/exec.go`.

#### Reporting

- **FR-019**: The corpus MUST state that a per-host result carries one of four
  statuses — `ok`, `failed`, `skipped`, `timeout` — and what distinguishes them:
  a failure ran and did not succeed, a skip does not apply to that OS family,
  and a timeout says nothing about whether it ran. Evidence:
  `pkg/sdk/client/status.go`, and the synthesized timeout row in
  `internal/job/client/client.go`.
- **FR-020**: The corpus MUST state that a failure carries a machine-readable
  cause beside its message, and that a cause the reader does not recognise is
  treated as an ordinary failure rather than guessed at. Evidence:
  `internal/job/errors.go`, `job.Response.ErrorCode` in `internal/job/types.go`.
- **FR-021**: The corpus MUST state the KV bucket TTLs as configured values,
  naming the file that sets them, and MUST record that the published site stated
  a different one. **Gap**: the page said 24 hours for completed and failed
  jobs; the shipped configuration sets one TTL for the whole `job-queue` bucket,
  `1h`. Evidence: `configs/osapi.yaml`.

#### Citing rather than restating

- **FR-022**: Where this subject reaches signing, response verification or agent
  identity, it MUST cite [002](../002-agent-key-store/spec.md) rather than
  describing them again.
- **FR-023**: Where it reaches what a provider must return or how a provider
  behaves, it MUST cite [001](../001-provider-contract/spec.md).
- **FR-024**: After this specification merges, the `add-a-domain` skill MUST
  cite these requirements rather than restating the mechanics, and the
  contributor half of the site page MUST be removed in the same change that adds
  those citations. This is 003's FR-010 applied to this subject, and it is the
  task nothing enforces — see 003's research Finding 3.

### Key Entities

- **Job**: An immutable definition stored under `jobs.{job-id}`, plus the
  append-only status events that describe what happened to it.
- **Notification**: A subject-routed message carrying a job ID, not its content.
- **Response**: An agent's answer, stored in its own bucket, carrying a status,
  a message and a machine-readable cause.
- **Target**: What a job is addressed to — a hostname, a machine ID, a broadcast
  or a label selector.
- **Obligation**: Something the system does not guarantee and the agent must
  therefore do. At-least-once delivery creates the only one that matters here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contributor with no prior knowledge answers all three questions
  in [003's quickstart](../003-corpus-backfill/quickstart.md) from this
  specification alone.
- **SC-002**: Every requirement naming a configured value or a key format cites
  a file, and opening that file confirms the value or finds the gap the
  requirement records.
- **SC-003**: The three gaps — the job key shape, the consumer defaults, the
  bucket TTL — are stated as corrections rather than silently differing from the
  page they came from.
- **SC-004**: After the site change, one statement of each of these rules exists
  across the corpus, the site and the skills, and `just skill-lint` passes with
  the citations resolving.
- **SC-005**: No requirement here restates a rule that
  [001](../001-provider-contract/spec.md) or
  [002](../002-agent-key-store/spec.md) already states.

## Assumptions

- The operator half of `job-architecture.md` stays on the site: the job states
  as observed, polling, the CLI reference, and the metrics worth watching. 003's
  data-model records the split line by line.
- The page is 630 lines as this is written, not the 603 003's spec records. The
  27 added lines are the Error Handling section, and they are the newest and
  most precisely sourced content on the page — which is why FR-009 through
  FR-018 lean on it.
- No Go code changes. This states what the code already does, and records where
  the page said otherwise.
- Three gaps were found by reading the code behind three of the page's
  statements. Others may exist in statements not yet checked; FR-002's citation
  requirement is what lets the next reader find them rather than trust the
  corpus.
