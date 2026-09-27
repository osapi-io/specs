# Changelog

## Merged Features Log

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
