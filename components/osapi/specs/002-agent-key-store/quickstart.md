# Quickstart: validating the key store

Phase 1. Scenarios that demonstrate the feature end to end. Each states what to
run and what proves it worked.

## Prerequisites

```bash
mise exec -- just react-build   # ui/dist must exist before anything lints
mise exec -- just deps
```

## 1. Nothing changes with PKI off

```bash
mise exec -- just test
```

**Proves**: with `controller.pki.enabled` and `agent.pki.enabled` unset, the
suite passes exactly as before. Responses and registrations behave as they do
today (FR-009, SC-005).

## 2. An accepted agent keeps its key

Start a controller and agent with PKI enabled on the controller, accept the
agent, then inspect the fleet view:

```bash
osapi client agent list
```

**Proves**: the agent shows a stored key and its fingerprint (SC-003). Before
acceptance it shows none.

## 3. A forged response is rejected

Exercised in unit tests rather than by hand, since forging requires a second
key:

```bash
mise exec -- go test ./internal/job/client/... -run Signature
```

**Proves**: a response signed by a key that is not the agent's is rejected, and
the job reports failure rather than a result (FR-003, SC-001).

## 4. A hostname cannot be stolen

```bash
mise exec -- go test ./internal/validation/... ./internal/job/client/... -run Resolve
```

**Proves**: an unsigned or mismatched registration is not resolvable, a second
machine claiming an enrolled hostname does not displace it, and resolution among
several claimants is deterministic (FR-004, FR-005, FR-006, SC-002).

## 5. Rotation does not cause an outage

```bash
mise exec -- go test ./internal/controller/enrollment/... -run Rotation
```

**Proves**: after a rotation the new key verifies, the superseded key verifies
until its expiry instant and not after, and a removed agent's key verifies never
(FR-007, FR-008, SC-004).

## 6. Failures are distinguishable

```bash
mise exec -- go test ./internal/job/client/... ./internal/controller/enrollment/... -run Verify
```

**Proves**: no stored key, signature mismatch and store unavailable produce
different, identifiable outcomes, and none of them is "verified" (FR-010,
SC-006).

## 7. A staged rollout works

Enable the controller side on a fleet where no agent has re-enrolled, then
observe: the fleet view lists every agent as having no stored key, and their
registrations are not authoritative. Re-enrol one agent and it becomes
authoritative without restarting the others.

**Proves**: enforcement begins when the operator chooses, and progress is
visible throughout (FR-009, SC-007).

## Gate before review

```bash
mise exec -- just ready
mise exec -- just test
mise exec -- just docusaurus-fmt-check
```

The last is not covered by the first two, and a change touching
`agent-identity.md` needs it.
