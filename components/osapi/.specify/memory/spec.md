# Main Project Specification

> **Revision**: 2026-09-26 — Seeded from the provider contract
> (`specs/001-provider-contract`): 3 user stories, 16 functional requirements, 5
> entities, 5 edge cases, 5 measurable outcomes, 4 assumptions.

> **Revision**: 2026-09-26 — Added the per-agent public key store
> (`specs/002-agent-key-store`): 3 user stories, 13 functional requirements, 4
> entities, 5 edge cases, 7 measurable outcomes, 5 assumptions. Nothing folded:
> the provider contract and agent identity share no ground.

## User Scenarios & Testing

### User Story 1 - The contract can be read without reading a sibling provider (Priority: P1)

Someone adding a provider learns what a provider must do from the corpus: the
operations it exposes, what each reports when the desired state is already met,
and what happens on an OS family it does not support.

**Why this priority**: This is the feature. Everything else here is detail
underneath it.

**Independent Test**: A reader with no osapi knowledge, given only the corpus,
can say what creating an existing resource reports, and what the caller sees when
the provider does not support the host's OS family.

**Acceptance Scenarios**:

1. **Given** the corpus alone, **When** a contributor asks what a provider must
   implement, **Then** the operation set, the context-first convention, and the
   result fields are stated without reference to a specific domain.
2. **Given** the corpus alone, **When** a contributor asks what makes an
   operation idempotent here, **Then** the three desired-state outcomes are
   stated as a rule rather than illustrated by one domain.
3. **Given** a provider that returns an error when deleting an absent resource,
   **When** it is reviewed against the corpus, **Then** the review cites a
   requirement rather than a sibling provider's behaviour.

[Source: specs/001-provider-contract/spec.md -> User Story 1]

### User Story 2 - The four implementation patterns are distinguishable (Priority: P2)

A provider that runs commands, one that writes its own configuration files, one
that delegates file writes, and one that calls an external API are four different
shapes with different obligations. A contributor can tell which shape a new
domain needs before writing it.

**Why this priority**: Choosing the wrong shape is expensive to undo: it decides
whether the domain gets change tracking and drift detection for free, and whether
it has platform variants at all.

**Independent Test**: Given a description of a new domain, a reader can name its
pattern from the corpus and say whether it needs stubs for the OS families it
does not implement.

**Acceptance Scenarios**:

1. **Given** a domain that manages a file under a well-known path, **When** the
   contributor consults the corpus, **Then** delegating writes to the file
   deployer is identified as the pattern, with what that delegation provides.
2. **Given** a domain that talks to an external daemon, **When** the contributor
   consults the corpus, **Then** no platform variants are expected and
   availability is established when the provider is constructed instead.

[Source: specs/001-provider-contract/spec.md -> User Story 2]

### User Story 3 - The trust boundary is stated where a provider is the second caller (Priority: P3)

A provider validates its inputs even though the request was already validated,
because the request path is not the only way a provider is reached: work is read
back from storage and executed later.

**Why this priority**: Three of the four critical findings in the September 2026
review were provider-side input handling. The rule existed in nobody's head as a
rule, so each domain decided for itself.

**Independent Test**: A reviewer can point at a requirement stating that a value
which becomes a path, a filename or a command argument is validated in the
provider, and check any domain against it.

**Acceptance Scenarios**:

1. **Given** a provider that builds a filesystem path from a request value,
   **When** it is reviewed against the corpus, **Then** validating that value in
   the provider is required, not optional hardening.
2. **Given** a provider that passes a secret to a command, **When** it is
   reviewed, **Then** the corpus requires the secret to reach the command without
   appearing in its arguments.

[Source: specs/001-provider-contract/spec.md -> User Story 3]

### User Story 4 - The controller can tell a real agent's answer from a forged one (Priority: P1)

An operator asks for a command to run on a host. The result that comes back is
checked against the key of the agent that enrolled as that host, so a result
written by something else does not reach the operator as fact.

**Why this priority**: Agents already sign their responses. Nothing checked the
signature, so the signing was decorative. Everything else here builds on the
store this requires.

**Independent Test**: With the store in place, a response carrying a valid
signature is accepted, and the same response re-signed by a different key is
rejected, without the operator's request appearing to succeed.

**Acceptance Scenarios**:

1. **Given** an accepted agent, **When** it answers a job, **Then** the controller
   verifies the response against that agent's stored key before treating it as a
   result.
2. **Given** a response signed by a key that is not the stored key for that agent,
   **When** it arrives, **Then** it is rejected and the job does not report
   success.
3. **Given** an agent with no stored key, **When** a response claiming to be from
   it arrives, **Then** it is rejected rather than accepted unverified.

[Source: specs/002-agent-key-store/spec.md -> User Story 1]

### User Story 5 - A host's name cannot be claimed by another machine (Priority: P1)

Work targeted at `web-01` reaches the machine that enrolled as `web-01`. A second
machine that announces the same hostname does not receive that work, and does not
replace the first in the operator's view of the fleet.

**Why this priority**: Registration is what targeting reads. An unauthenticated
registration means the identity established at enrollment can be overridden
afterwards by anything able to write, which makes enrollment's guarantee
conditional on the transport alone.

**Independent Test**: A registration whose signature does not verify against the
stored key for its machine ID is not visible to targeting, and work aimed at that
hostname continues to reach the enrolled machine.

**Acceptance Scenarios**:

1. **Given** an enrolled agent, **When** it registers, **Then** the registration
   is signed and verified against its stored key before targeting will use it.
2. **Given** a registration claiming a hostname already held by a different
   enrolled machine, **When** it is verified, **Then** it does not displace the
   enrolled machine for targeting purposes.
3. **Given** a registration that is unsigned or fails verification, **When**
   targeting resolves a hostname or label, **Then** that registration is not among
   the candidates.

[Source: specs/002-agent-key-store/spec.md -> User Story 2]

### User Story 6 - Keys change without an outage, and leave when the agent does (Priority: P2)

An operator rotates an agent's key, or removes an agent, and neither action
requires re-enrolling the fleet or leaves a stale key behind that would still be
trusted.

**Why this priority**: A store that cannot be updated becomes a reason to turn
verification off. The controller key already has a rotation story with a grace
period; the agent key needs the equivalent.

**Independent Test**: After a rotation, messages signed with the new key verify,
messages signed with the previous key verify until the grace period lapses, and
messages signed with a key that was removed do not verify at all.

**Acceptance Scenarios**:

1. **Given** an agent that rotates its key, **When** it re-enrolls or presents the
   new key through the supported path, **Then** the stored key is replaced and
   subsequent messages verify against it.
2. **Given** a rotation in progress, **When** a message signed with the previous
   key arrives inside the grace period, **Then** it verifies, and after the grace
   period it does not.
3. **Given** an agent that is removed or rejected, **When** anything signed by its
   key arrives afterwards, **Then** it does not verify.

[Source: specs/002-agent-key-store/spec.md -> User Story 3]

### Edge Cases

- A host runs an OS family the provider does not implement. This is not a
  failure: the provider reports the shared unsupported outcome and the work is
  recorded as skipped, so the caller can tell "not available here" from "broken".
  Evidence: `internal/provider/errors.go:28`, `internal/agent/handler.go:414`.
  [Source: specs/001-provider-contract/spec.md -> "A host runs an OS family the provider does not implement"]
- A provider is constructed but never registered with the agent's registry. Facts
  are injected by walking registered providers, so its facts are absent and any
  fact-dependent operation fails when called rather than at startup. Evidence:
  `internal/provider/facts.go:64`, `internal/agent/agent.go`.
  [Source: specs/001-provider-contract/spec.md -> "A provider is constructed but never registered"]
- The same unit of work is delivered twice. The provider's idempotency is what
  makes the repeat harmless; delivery handling is specified separately.
  [Source: specs/001-provider-contract/spec.md -> "The same unit of work is delivered twice"]
- A request value arrives that the request path would now reject, because it was
  stored before that rule existed, or because something else wrote to the store.
  The provider's own validation is the only remaining check.
  [Source: specs/001-provider-contract/spec.md -> "A request value arrives that the request path would now reject"]
- A provider writes a file and the process dies mid-write. A partially written
  configuration file is worse than none, so the write does not happen in place.
  Evidence: `internal/provider/file/deploy.go`.
  [Source: specs/001-provider-contract/spec.md -> "A provider writes a file and the process dies mid-write"]

- An agent enrolled before the key store existed has no stored key. Which of
  "reject its messages" or "accept until it re-enrolls" applies is stated, and the
  same answer holds for responses and registrations, so an upgrade does not
  silently create a trusted-by-default class of agent.
  [Source: specs/002-agent-key-store/spec.md -> "An agent enrolled before this feature exists"]
- Two machines present the same hostname. Enrollment records identity by machine
  ID, so both can exist; targeting chooses deterministically rather than by
  iteration order.
  [Source: specs/002-agent-key-store/spec.md -> "Two machines present the same hostname"]
- A machine ID is reused, for example a restored VM image. The stored key is
  replaced only through an accepted enrollment, never by the arrival of a message
  signed with a different key.
  [Source: specs/002-agent-key-store/spec.md -> "A machine ID is reused"]
- The store is unavailable when a response or registration arrives. Verification
  does not silently pass, and the outcome is never "treat as verified".
  [Source: specs/002-agent-key-store/spec.md -> "The store is unavailable"]
- An agent is accepted while a previous registration for its hostname is still
  present. The older entry stops being authoritative once the new agent is
  accepted.
  [Source: specs/002-agent-key-store/spec.md -> "An agent is accepted while a previous registration"]

## Requirements

### Functional Requirements

- **FR-001**: The corpus MUST state that a provider is the operations layer, runs
  in the agent process rather than the controller, receives its parameters from
  the unit of work, and returns a result; the controller never executes
  operations itself. Evidence: `internal/agent/processor_*.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-001]
- **FR-002**: The corpus MUST state the provider operation set and the
  context-first convention on every method, and the
  list/get/create/update/delete shape used where a domain is a collection of
  resources. Evidence: `internal/provider/node/sysctl/types.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-002]
- **FR-003**: The corpus MUST state that a mutation result carries whether
  anything changed, and that a per-resource error is reported in the result
  rather than replacing it, so one failing host does not hide the others.
  Evidence: `internal/provider/node/sysctl/types.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-003]
- **FR-004**: The corpus MUST state the idempotency contract as a rule: creating a
  resource that already exists reports no change and no error; deleting a
  resource that is absent reports no change and no error; updating a resource
  that is absent is an error. Evidence:
  `internal/provider/node/sysctl/debian.go`, its Create, Update and Delete.
  [Source: specs/001-provider-contract/spec.md -> FR-004]
- **FR-005**: The corpus MUST state that an operation unsupported on the host's OS
  family reports the shared unsupported outcome, and that this is distinct from
  reporting no change — it is recorded as skipped. Evidence:
  `internal/provider/errors.go:28`, `internal/agent/handler.go:414`.
  [Source: specs/001-provider-contract/spec.md -> FR-005]
- **FR-006**: The corpus MUST state the four implementation patterns, how to
  recognise which applies, and what each obliges: a direct provider that runs
  commands (`internal/provider/node/process`); a provider that delegates file
  writes to the file deployer and gains change tracking, idempotency and template
  rendering (`internal/provider/scheduled/cron`, `internal/provider/node/service`,
  `internal/provider/node/certificate`, `internal/provider/node/user`); a
  provider that manages its own configuration files and marks them with a
  reserved filename prefix so managed files are distinguishable from hand-written
  ones (`internal/provider/node/sysctl`); and a provider that calls an external
  API, has no platform variants, and establishes availability when constructed
  (`internal/provider/container`).
  [Source: specs/001-provider-contract/spec.md -> FR-006]
- **FR-007**: The corpus MUST state that platform-specific providers are selected
  outside the provider — by OS family, and by whether the process is
  containerised — and that the families a domain does not implement are present
  as stubs rather than absent. Evidence: `pkg/sdk/platform` `Detect` and
  `IsContainer`, consumed in `cmd/agent_setup.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-007]
- **FR-008**: The corpus MUST state how a provider obtains host facts: by
  embedding the shared facts holder, asserting the setter contract at compile
  time, and being registered so facts are injected at startup. Evidence:
  `internal/provider/facts.go:30`, `:41`, `:64`.
  [Source: specs/001-provider-contract/spec.md -> FR-008]
- **FR-009**: The corpus MUST state that validation on the request path does not
  discharge the provider's: any value that becomes a filesystem path, a filename,
  or a command argument is validated in the provider before use, because work
  executed from storage is a second caller. Evidence: GHSA-7fjw-v3g9-326g, fixed
  in `internal/provider/node/sysctl/debian.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-009]
- **FR-010**: The corpus MUST state that a secret reaches a command without
  appearing in its arguments, and that arguments are treated as logged and
  publicly visible. Evidence: GHSA-6gc6-px2x-q95j; the stdin-carrying variant in
  `internal/exec`, and the argument logging in `internal/exec/exec.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-010]
- **FR-011**: The corpus MUST state that a value supplied by a caller is never
  allowed to be parsed as an option by a command the provider runs.
  [Source: specs/001-provider-contract/spec.md -> FR-011]
- **FR-012**: The corpus MUST state that filesystem access goes through the
  virtual filesystem abstraction rather than the standard library or a
  substitute, so a provider is testable in memory and with injected failures, and
  that commands go through the shared exec manager rather than being spawned
  directly. Evidence: `CONTRIBUTING.md` "Filesystem access"; the constructors in
  `internal/provider/*/debian.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-012]
- **FR-013**: The corpus MUST state that a file a provider writes is not written
  in place, so a crash cannot leave a half-written configuration file behind, and
  that the mode and ownership a caller asked for are applied even when the content
  is unchanged. Evidence: `internal/provider/file/deploy.go`; osapi-io/osapi#498.
  [Source: specs/001-provider-contract/spec.md -> FR-013]
- **FR-014**: The corpus MUST state the testing obligations belonging to the
  contract rather than to house style: each of the three idempotency outcomes is
  covered; every stub family is asserted to report the unsupported outcome; and
  each rejection required by FR-009 through FR-011 is covered by a case proving
  no command ran and no file was written. Evidence:
  `internal/provider/node/sysctl/debian_public_test.go`,
  `internal/provider/node/*/darwin_public_test.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-014]
- **FR-015**: The corpus MUST state what a provider does not touch: it adds no
  message subject, stream, consumer or key-value bucket, and nothing in the
  provider layer depends on the sibling messaging libraries. Evidence: no file
  under `internal/provider/` imports `osapi-io/nats-client`; buckets and streams
  are declared in `internal/job/config.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-015]
- **FR-016**: The `add-a-domain` skill MUST cite these requirements rather than
  restating them, so the corpus is the single statement and the skill routes to
  it. [Source: specs/001-provider-contract/spec.md -> FR-016]

- **FR-017**: The system MUST retain an accepted agent's public key beyond the
  lifetime of its enrollment request, keyed by machine ID, so the key remains
  available for every later verification.
  [Source: specs/002-agent-key-store/spec.md -> FR-001]
- **FR-018**: The system MUST record the key only as part of accepting an
  enrollment. No message, registration or heartbeat may introduce or change a
  stored key. [Source: specs/002-agent-key-store/spec.md -> FR-002]
- **FR-019**: The controller MUST verify an agent's job response against that
  agent's stored key before the response is treated as a result, and MUST NOT
  fall back to accepting an unverified response.
  [Source: specs/002-agent-key-store/spec.md -> FR-003]
- **FR-020**: The agent MUST sign what it registers, and the controller MUST
  verify that signature against the stored key before the registration is used
  for targeting, labels, facts or fleet status.
  [Source: specs/002-agent-key-store/spec.md -> FR-004]
- **FR-021**: A registration that is unsigned, unverifiable, or signed by a key
  other than the stored key for its machine ID MUST NOT be visible to target
  resolution, and MUST NOT replace the entry of an enrolled machine.
  [Source: specs/002-agent-key-store/spec.md -> FR-005]
- **FR-022**: Where a hostname is claimed by more than one machine, target
  resolution MUST be deterministic and MUST prefer the enrolled machine, rather
  than depending on iteration order.
  [Source: specs/002-agent-key-store/spec.md -> FR-006]
- **FR-023**: The system MUST support replacing a stored key through an accepted
  enrollment, and MUST accept the previous key for a bounded grace period after
  replacement, so a rotation does not reject messages signed just before it.
  [Source: specs/002-agent-key-store/spec.md -> FR-007]
- **FR-024**: The system MUST remove a stored key when its agent is removed or its
  enrollment is rejected, after which nothing signed by that key verifies.
  [Source: specs/002-agent-key-store/spec.md -> FR-008]
- **FR-025**: Enforcement MUST be something the operator turns on per side, and
  MUST NOT begin as a side effect of upgrading. Once enforcement is on for a side,
  a message from an agent with no stored key MUST be refused there. Until it is
  on, such a message is handled as it is today. "Treat as verified" is never an
  outcome. [Source: specs/002-agent-key-store/spec.md -> FR-009]
- **FR-026**: Verification failures MUST be distinguishable by cause: no stored
  key, signature mismatch, and store unavailable are different conditions and MUST
  be reported differently, so an operator can tell "not enrolled yet" from
  "something is forging messages".
  [Source: specs/002-agent-key-store/spec.md -> FR-010]
- **FR-027**: The behaviour MUST be governed by the existing PKI switches rather
  than a new one, and with PKI disabled the system MUST behave exactly as it does
  today. [Source: specs/002-agent-key-store/spec.md -> FR-011]
- **FR-028**: Operators MUST be able to see which agents have a stored key, and
  its fingerprint, so a fleet can be checked before verification is enforced.
  [Source: specs/002-agent-key-store/spec.md -> FR-012]
- **FR-029**: The documentation MUST state the rollout order, the failure modes
  from FR-026, and what an operator does when an agent reports no stored key.
  [Source: specs/002-agent-key-store/spec.md -> FR-013]

### Key Entities

- **Provider**: A domain's operations, running in the agent, selected by OS
  family. Exposes the operation set in FR-002 and honours FR-004.
  [Source: specs/001-provider-contract/spec.md -> Provider]
- **Result**: What an operation returns: the resource identity, whether anything
  changed, and a per-resource error when one occurred.
  [Source: specs/001-provider-contract/spec.md -> Result]
- **Unsupported outcome**: The shared signal meaning "not available on this OS
  family", distinct from a failure and from no change.
  [Source: specs/001-provider-contract/spec.md -> Unsupported outcome]
- **Facts**: Host attributes collected by the agent and injected into registered
  providers. [Source: specs/001-provider-contract/spec.md -> Facts]
- **File deployer**: The narrow contract a provider delegates file writes to in
  order to gain change tracking, idempotency and template rendering.
  [Source: specs/001-provider-contract/spec.md -> File deployer]

- **Stored agent key**: An accepted agent's public key, held against its machine
  ID, with the fingerprint recorded at acceptance and, during rotation, the
  previous key and the moment it stops being accepted.
  [Source: specs/002-agent-key-store/spec.md -> Stored agent key]
- **Registration**: What an agent publishes about itself — hostname, labels,
  machine ID and status — which targeting reads. Authenticated under FR-020.
  [Source: specs/002-agent-key-store/spec.md -> Registration]
- **Job response**: What an agent returns for a unit of work. Authenticated under
  FR-019. [Source: specs/002-agent-key-store/spec.md -> Job response]
- **Enrollment acceptance**: The only event that may create or replace a stored
  key. [Source: specs/002-agent-key-store/spec.md -> Enrollment acceptance]

## Success Criteria

### Measurable Outcomes

- **SC-001**: A contributor states all three idempotency outcomes and the
  unsupported outcome from the corpus alone, without opening a provider.
  [Source: specs/001-provider-contract/spec.md -> SC-001]
- **SC-002**: Every existing provider can be checked against the contract, and
  each deviation is expressible as a named requirement it fails rather than as a
  difference from a sibling. [Source: specs/001-provider-contract/spec.md -> SC-002]
- **SC-003**: The `add-a-domain` skill's provider reference contains no restated
  mechanics: what remains is routing plus citations into this corpus.
  [Source: specs/001-provider-contract/spec.md -> SC-003]
- **SC-004**: A new domain's provider is reviewable against the corpus with no
  appeal to "look at how sysctl does it".
  [Source: specs/001-provider-contract/spec.md -> SC-004]
- **SC-005**: Someone asking whether a provider needs to know about the messaging
  layer gets a stated answer rather than inferring one from imports.
  [Source: specs/001-provider-contract/spec.md -> SC-005]

- **SC-006**: A response or registration signed by a key other than the one
  recorded at acceptance is rejected in every case, and never reaches an operator
  as a result or as fleet state.
  [Source: specs/002-agent-key-store/spec.md -> SC-001]
- **SC-007**: Work targeted at a hostname reaches the machine that enrolled under
  that hostname, including when another machine is publishing the same hostname.
  [Source: specs/002-agent-key-store/spec.md -> SC-002]
- **SC-008**: An operator can determine, for any agent, whether the controller
  holds its key and which key that is, without reading storage directly.
  [Source: specs/002-agent-key-store/spec.md -> SC-003]
- **SC-009**: Rotating an agent's key causes no rejected messages for correctly
  behaving agents, and messages signed with the old key stop verifying once the
  grace period lapses. [Source: specs/002-agent-key-store/spec.md -> SC-004]
- **SC-010**: With PKI disabled, behaviour is unchanged from before the key store
  existed. [Source: specs/002-agent-key-store/spec.md -> SC-005]
- **SC-011**: Every rejection is attributable to one of the stated causes, and no
  rejection is reported only as a generic failure.
  [Source: specs/002-agent-key-store/spec.md -> SC-006]
- **SC-012**: An operator can enable enforcement on one side, see which agents
  would be refused, re-enrol them, and complete the rollout without the fleet
  refusing work at a moment they did not choose.
  [Source: specs/002-agent-key-store/spec.md -> SC-007]

## Assumptions

- **AS-001**: The audience is contributors and agents working on osapi, not
  operators. What each domain does for a user stays in the published
  documentation; this states how a provider behaves. File paths and named errors
  appear as evidence for requirements, which the constitution's Verification
  principle requires.
  [Source: specs/001-provider-contract/spec.md -> "The audience is contributors and agents"]
- **AS-002**: Requirements state current behaviour. Two known gaps are recorded
  rather than specified away: the option-parsing rule in FR-011 is not yet
  enforced for user and group names (recorded on GHSA-6gc6-px2x-q95j), and the
  atomic-write and mode-application rules in FR-013 are not yet honoured by the
  file deployer (osapi-io/osapi#498). A requirement the code does not yet meet is
  a gap in the code, not an error in the corpus.
  [Source: specs/001-provider-contract/spec.md -> "Requirements state current behaviour"]
- **AS-003**: The job system, the request, SDK and CLI layers, and the UI are out
  of scope and become their own features. This covers only what a provider is and
  must do. [Source: specs/001-provider-contract/spec.md -> "The job system, the request, SDK and CLI layers"]
- **AS-004**: The four patterns are the four in the codebase today. A fifth would
  amend this. [Source: specs/001-provider-contract/spec.md -> "The four patterns are the four in the codebase today"]
- **AS-005**: Enrollment remains the only trust anchor. The key store makes the
  identity established there durable and checkable; it does not change how an
  agent is accepted, nor introduce a second way to become trusted.
  [Source: specs/002-agent-key-store/spec.md -> "Enrollment remains the only trust anchor"]
- **AS-006**: Agents hold a key pair and sign responses, and the controller holds
  a key pair and signs jobs.
  [Source: specs/002-agent-key-store/spec.md -> "Agents already hold a key pair"]
- **AS-007**: The grace period for an agent key follows the pattern already used
  for the controller key rather than inventing a second mechanism.
  [Source: specs/002-agent-key-store/spec.md -> "The grace period for an agent key"]
- **AS-008**: Transport credentials are not identity. NATS credentials control who
  may connect; the key store decides whose messages are believed once connected.
  [Source: specs/002-agent-key-store/spec.md -> "Transport credentials are not identity"]
- **AS-009**: Controller key rotation, the enrollment handshake itself, and NATS
  authorization are out of scope, the last being deployment configuration rather
  than osapi behaviour.
  [Source: specs/002-agent-key-store/spec.md -> "Out of scope"]
