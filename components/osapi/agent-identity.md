# Agent identity

The controller has to know that an answer came from the machine it addressed,
and that a machine claiming a hostname is the one that enrolled under it. Both
come down to one stored public key per agent.

## Enrollment is the only thing that writes a key

An accepted agent's public key is retained beyond the enrollment handshake, held
against its **machine ID** rather than its hostname, with the fingerprint
recorded at the moment of acceptance.

**Accepting an enrollment is the only event that may create or replace that
key.** Not a message signed with a different key, not a re-registration, not a
restart. So an attacker who can publish to the bus cannot rotate a key by
publishing, and the trust anchor stays where an operator put it.

A key is destroyed on two events and no others: an operator rejecting a pending
enrollment, and an operator removing an enrolled agent. Both take effect
immediately, with no interval in which a removed agent's signature still
verifies.

## What gets verified

Two things, and they answer different questions.

**A job response** is verified against the key recorded at acceptance. That is
what makes a result trustworthy: the controller knows which machine produced it.

**A registration** is signed by the agent and verified by the controller. That
is what makes *targeting* trustworthy, and it is the less obvious half.

Registration carries hostname, labels, machine ID and status, and targeting
reads it. Without verification, a second machine could publish the same hostname
and receive work addressed to the first. **Targeting resolves only verified
registrations**, so an unverified registration is not a candidate for work.

What that looks like in a result depends on how the job was addressed. A job
sent to a named host that has no verified registration fails to resolve a
target. A broadcast is different: `ExpectedAgentHostnames` builds the expected
set from verified registrations, so an unverified agent is **not in the set and
produces no row at all**. It does not appear as `timeout`, because nothing was
expecting it.

That distinction matters when an enrollment has gone wrong. A broadcast
returning nineteen rows for a twenty-machine fleet is the symptom, and the
missing row is silent. `GET /agent` reporting `key_stored` and `verified` is
where to look.

## Rotation without an outage

A replaced key keeps its predecessor accepted for a grace period, so an agent
rotating its key does not have a window where its messages are refused.

`ControllerPKI.RotationGracePeriod` sets it. Once it lapses, messages signed
with the old key stop verifying.

## Failure is never silent

**Verification does not fail open.** When the key store is unavailable, the
outcome is not "treat as verified"; a message that cannot be checked is not
believed.

Every rejection is attributable to a named cause rather than a generic failure,
so an operator can tell an unenrolled agent from a wrong signature from an
unreachable store.

## Enabling it on a live fleet

Enforcement is separately switchable per side: `ControllerPKI.Enabled` for the
controller, `AgentPKI.Enabled` for the agent. **With PKI disabled, behaviour is
byte-for-byte what it was before the key store existed.**

`GET /agent` reports `key_stored` and `verified` per agent, which is what makes
a staged rollout possible: turn on one side, see which agents would be refused,
re-enrol them, and finish the rollout at a moment of your choosing rather than
the moment you flipped a flag.

## What this is not

**Transport credentials are not identity.** NATS credentials control who may
connect. This controls whose messages are believed once connected. An attacker
with valid NATS credentials still cannot forge a response.

Two machines presenting the same hostname is a supported state rather than an
error, because identity is the machine ID. Both exist, and targeting chooses
deterministically rather than by whichever arrived last.

A reused machine ID, a restored VM image being the usual cause, does not inherit
trust: the stored key is replaced only through an accepted enrollment.

## Where this connects

What a signed response is answering, and where the signature sits in the job
lifecycle, is [the job system](job-system.md).

______________________________________________________________________

Written from `internal/agent/` and `internal/job/registration.go`.
