# Research: Per-agent public key store

Phase 0. Each decision below was open when planning began; the Technical Context
now carries no NEEDS CLARIFICATION.

## 1. Where the store lives

**Decision**: The existing enrollment KV bucket, under an `accepted.` key
prefix, keyed by machine ID. Pending records keep the `enrollment.` prefix.

**Rationale**: Acceptance is the only writer (FR-002), and the enrollment
watcher already holds that bucket handle and runs at exactly that moment. The
bucket is already declared, provisioned and configured, so no new bucket name,
config field or startup path appears — and nothing new can be forgotten in a
deployment. Key material here is public, so bucket-level sensitivity does not
change.

**Alternatives considered**:

- *A new dedicated KV bucket.* Cleaner separation, but adds a bucket name to
  config, a creation path at startup, and an upgrade step, for one small record
  per agent.
- *A field on `AgentRegistration` in the registry bucket.* Rejected outright:
  the registry is what the agent writes, so storing the authority there would
  let the attacker supply the key that validates their own message. That is
  GHSA-j73r.
- *A file on the controller's disk beside its own keypair.* Breaks with more
  than one controller and has no replication story; the KV already replicates.

## 2. What identifies an agent

**Decision**: Machine ID, matching enrollment.

**Rationale**: Enrollment already records identity by machine ID, and both
advisories stem from hostname being self-asserted and mutable. Hostname becomes
a claim checked against the stored record rather than an identifier.

**Alternatives considered**: *Hostname* — the thing being attacked.
*Fingerprint* — derived from the key, so it cannot be the lookup for the key
without circularity.

## 3. How rotation and removal are represented

**Decision**: The record holds the current key, optionally a superseded key, and
the instant the superseded key stops being accepted. Verification tries current,
then superseded while inside the grace period. Removal deletes the record.

**Rationale**: Mirrors what the controller key already does — `VerifyWithGrace`,
`PreviousControllerPublicKey` and `ControllerPKI.RotationGracePeriod` — so
operators meet one rotation concept, not two. Storing the expiry instant rather
than a duration means a restart cannot silently extend the window.

**Alternatives considered**: *Key history list* — unbounded, and nothing needs
the third-oldest key. *No grace at all* — rejects messages signed moments before
a rotation, which is the reason operators turn verification off.

## 4. How enforcement is switched on

**Decision**: No new configuration. `ControllerPKI.Enabled` governs the
controller side, `AgentPKI.Enabled` the agent side, per FR-009 and the clarify
answer. Enforcement begins only when the operator sets the flag for that side.

**Rationale**: Both flags are already documented as covering PKI enrollment
*and* signing, so this makes the documented behaviour true rather than adding a
knob. A new flag would also create a second way to be "half on".

**Alternatives considered**: *A separate `enforce_signatures` flag* — more
precise, but three states to reason about and a migration story for a field that
duplicates an existing one.

## 5. What a verification failure reports

**Decision**: Three distinguishable causes, on both sides: no stored key,
signature mismatch, and store unavailable. Never collapsed into one error.

**Rationale**: FR-010, and the agent side already does this — GHSA-3jh4 shipped
`ErrControllerKeyUnknown`, `ErrJobEnvelopeMissing` and `ErrJobSignatureInvalid`.
An operator staging a rollout needs "this agent has not re-enrolled yet" to look
nothing like "something is forging messages".

**Alternatives considered**: *A single verification error* — indistinguishable
in logs at exactly the moment it matters.

## 6. How the fleet view shows readiness

**Decision**: `ListAgents` reports, per agent, whether a key is stored and its
fingerprint, and the agent list endpoint surfaces it.

**Rationale**: SC-003 and SC-007 require an operator to see who would be refused
*before* enabling enforcement. `ListAgents` already walks the registry, so this
is one lookup per agent on a path that is already a list operation.

**Alternatives considered**: *A separate command* — another surface to learn for
something the fleet view is already for.

## 7. Cost of verification

**Decision**: Cache the stored key per machine ID in the controller, invalidated
on acceptance and removal.

**Rationale**: Verification touches responses and every heartbeat, so an
uncached KV read per message would scale with fleet chatter. Acceptance and
removal are rare and already flow through one package, which makes invalidation
exact rather than time-based.

**Alternatives considered**: *No cache* — simplest, and acceptable at current
scale, but the read sits on the heartbeat path. *TTL cache* — reintroduces a
window where a removed agent still verifies, which FR-008 forbids.

## 8. What the agent signs in a registration

**Decision**: A canonical serialisation of the registration's identity-bearing
fields, with the signature carried beside the record rather than inside the
signed bytes.

**Rationale**: `AgentRegistration` already carries a self-reported
`Fingerprint`, and today nothing checks it. The stored key is the authority; the
fingerprint becomes a claim that must match. Signing requires a byte sequence
both sides derive identically, which rules out signing the marshalled struct
as-is if field order or optional fields can vary.

**Alternatives considered**: *Sign the whole marshalled record* — fragile
against serialisation differences and any added field. *Sign only the machine
ID* — a valid signature would then authenticate a registration whose hostname
and labels had been altered, leaving GHSA-j73r open.
