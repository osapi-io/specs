# Feature Specification: Per-agent public key store

**Feature Branch**: `feat/agent-key-store`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Persist each accepted agent's public key so the
controller can verify what an agent sends: its job responses, and the
registration that decides where work is routed. Closes the deferred half of
GHSA-3jh4 and the identity half of GHSA-j73r together, because both need the
same missing store."

osapi has PKI enrollment, signing on both sides, and verification code on both
sides. What it does not have is anywhere for the controller to keep an agent's
public key after enrollment. An accepted agent's key is written into the
pending-enrollment record and deleted when the record is, so every
controller-side verification path finds no key and skips. This specifies the
store and what must depend on it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The controller can tell a real agent's answer from a forged one (Priority: P1)

An operator asks for a command to run on a host. The result that comes back is
checked against the key of the agent that enrolled as that host, so a result
written by something else does not reach the operator as fact.

**Why this priority**: Agents already sign their responses. Nothing checks the
signature, so the signing is decorative. Everything else here builds on the
store this requires.

**Independent Test**: With the store in place, a response carrying a valid
signature is accepted, and the same response re-signed by a different key is
rejected, without the operator's request appearing to succeed.

**Acceptance Scenarios**:

1. **Given** an accepted agent, **When** it answers a job, **Then** the
   controller verifies the response against that agent's stored key before
   treating it as a result.
2. **Given** a response signed by a key that is not the stored key for that
   agent, **When** it arrives, **Then** it is rejected and the job does not
   report success.
3. **Given** an agent with no stored key, **When** a response claiming to be
   from it arrives, **Then** it is rejected rather than accepted unverified.

______________________________________________________________________

### User Story 2 - A host's name cannot be claimed by another machine (Priority: P1)

Work targeted at `web-01` reaches the machine that enrolled as `web-01`. A
second machine that announces the same hostname does not receive that work, and
does not replace the first in the operator's view of the fleet.

**Why this priority**: Registration is what targeting reads. An unauthenticated
registration means the identity established at enrollment can be overridden
afterwards by anything able to write, which makes enrollment's guarantee
conditional on the transport alone.

**Independent Test**: A registration whose signature does not verify against the
stored key for its machine ID is not visible to targeting, and work aimed at
that hostname continues to reach the enrolled machine.

**Acceptance Scenarios**:

1. **Given** an enrolled agent, **When** it registers, **Then** the registration
   is signed and verified against its stored key before targeting will use it.
2. **Given** a registration claiming a hostname already held by a different
   enrolled machine, **When** it is verified, **Then** it does not displace the
   enrolled machine for targeting purposes.
3. **Given** a registration that is unsigned or fails verification, **When**
   targeting resolves a hostname or label, **Then** that registration is not
   among the candidates.

______________________________________________________________________

### User Story 3 - Keys change without an outage, and leave when the agent does (Priority: P2)

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

1. **Given** an agent that rotates its key, **When** it re-enrolls or presents
   the new key through the supported path, **Then** the stored key is replaced
   and subsequent messages verify against it.
2. **Given** a rotation in progress, **When** a message signed with the previous
   key arrives inside the grace period, **Then** it verifies, and after the
   grace period it does not.
3. **Given** an agent that is removed or rejected, **When** anything signed by
   its key arrives afterwards, **Then** it does not verify.

### Edge Cases

- An agent enrolled before this feature exists has no stored key. The system
  must state which of "reject its messages" or "accept until it re-enrolls"
  applies, and the same answer must hold for responses and registrations, so an
  upgrade does not silently create a trusted-by-default class of agent.
  Evidence: `internal/controller/enrollment/accept.go` deletes the pending
  record, so no existing deployment has a stored key.
- Two machines present the same hostname. Enrollment records identity by machine
  ID, so both can exist; targeting must choose deterministically rather than by
  iteration order. Evidence: GHSA-j73r; `internal/validation/target.go` resolves
  a hostname to the first registry entry claiming it.
- A machine ID is reused, for example a restored VM image. The stored key must
  be replaced only through an accepted enrollment, never by the arrival of a
  message signed with a different key.
- The store is unavailable when a response or registration arrives. Verification
  cannot silently pass; the behaviour must be stated, and it must not be "treat
  as verified".
- An agent is accepted while a previous registration for its hostname is still
  present. The older entry must stop being authoritative for targeting once the
  new agent is accepted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST retain an accepted agent's public key beyond the
  lifetime of its enrollment request, keyed by machine ID, so the key remains
  available for every later verification. Evidence:
  `internal/controller/enrollment/types.go` holds `PublicKey` on the pending
  record; `accept.go` deletes that record on acceptance.
- **FR-002**: The system MUST record the key only as part of accepting an
  enrollment. No message, registration or heartbeat may introduce or change a
  stored key. Evidence: GHSA-j73r, where unauthenticated registration is the
  attack.
- **FR-003**: The controller MUST verify an agent's job response against that
  agent's stored key before the response is treated as a result, and MUST NOT
  fall back to accepting an unverified response. Evidence: GHSA-3jh4;
  `internal/job/client/signing.go` currently skips verification when no
  counterpart key is set.
- **FR-004**: The agent MUST sign what it registers, and the controller MUST
  verify that signature against the stored key before the registration is used
  for targeting, labels, facts or fleet status. Evidence:
  `internal/agent/heartbeat.go` writes the registration unsigned;
  `internal/validation/target.go` reads it to resolve a target.
- **FR-005**: A registration that is unsigned, unverifiable, or signed by a key
  other than the stored key for its machine ID MUST NOT be visible to target
  resolution, and MUST NOT replace the entry of an enrolled machine.
- **FR-006**: Where a hostname is claimed by more than one machine, target
  resolution MUST be deterministic and MUST prefer the enrolled machine, rather
  than depending on iteration order. Evidence: GHSA-j73r.
- **FR-007**: The system MUST support replacing a stored key through an accepted
  enrollment, and MUST accept the previous key for a bounded grace period after
  replacement, so a rotation does not reject messages signed just before it.
  Evidence: the controller key already has this shape —
  `ControllerPKI.RotationGracePeriod`, `internal/agent/pki` `VerifyWithGrace`
  and `PreviousControllerPublicKey`.
- **FR-008**: The system MUST remove a stored key when its agent is removed or
  its enrollment is rejected, after which nothing signed by that key verifies.
- **FR-009**: The system MUST state, and apply consistently across responses and
  registrations, what happens when no key is stored for an agent — including
  agents enrolled before this feature existed. Whichever behaviour is chosen
  MUST NOT be "treat as verified".
- **FR-010**: Verification failures MUST be distinguishable by cause: no stored
  key, signature mismatch, and store unavailable are different conditions and
  MUST be reported differently, so an operator can tell "not enrolled yet" from
  "something is forging messages". Evidence: the agent side already does this
  with three distinct sentinels, added for GHSA-3jh4.
- **FR-011**: The behaviour MUST be governed by the existing PKI switches rather
  than a new one, and with PKI disabled the system MUST behave exactly as it
  does today. Evidence: `ControllerPKI.Enabled`, `AgentPKI.Enabled`.
- **FR-012**: Operators MUST be able to see which agents have a stored key, and
  its fingerprint, so a fleet can be checked before verification is enforced.
- **FR-013**: The documentation MUST state the rollout order, the failure modes
  from FR-010, and what an operator does when an agent reports no stored key.

### Key Entities

- **Stored agent key**: An accepted agent's public key, held against its machine
  ID, with the fingerprint recorded at acceptance and, during rotation, the
  previous key and the moment it stops being accepted.
- **Registration**: What an agent publishes about itself — hostname, labels,
  machine ID and status — which targeting reads. Authenticated under FR-004.
- **Job response**: What an agent returns for a unit of work. Authenticated
  under FR-003.
- **Enrollment acceptance**: The only event that may create or replace a stored
  key.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A response or registration signed by a key other than the one
  recorded at acceptance is rejected in every case, and never reaches an
  operator as a result or as fleet state.
- **SC-002**: Work targeted at a hostname reaches the machine that enrolled
  under that hostname, including when another machine is publishing the same
  hostname.
- **SC-003**: An operator can determine, for any agent, whether the controller
  holds its key and which key that is, without reading storage directly.
- **SC-004**: Rotating an agent's key causes no rejected messages for correctly
  behaving agents, and messages signed with the old key stop verifying once the
  grace period lapses.
- **SC-005**: With PKI disabled, behaviour is unchanged from before this
  feature.
- **SC-006**: Every rejection is attributable to one of the stated causes, and
  no rejection is reported only as a generic failure.

## Assumptions

- Enrollment remains the only trust anchor. This feature makes the identity
  established there durable and checkable; it does not change how an agent is
  accepted, nor introduce a second way to become trusted.
- Agents already hold a key pair and already sign responses, and the controller
  already holds a key pair and signs jobs. Evidence: `internal/agent/pki` and
  the GHSA-3jh4 fix merged as `f00dca607`.
- The grace period for an agent key follows the pattern already used for the
  controller key rather than inventing a second mechanism.
- Transport credentials are not identity. NATS credentials continue to control
  who may connect; this feature decides whose messages are believed once
  connected.
- Out of scope: controller key rotation, which exists; the enrollment handshake
  itself; and NATS authorization, which is deployment configuration rather than
  osapi behaviour.
- The two advisories this closes are GHSA-3jh4 (its deferred
  response-verification half) and GHSA-j73r. Both remain draft until the
  implementation merges.
