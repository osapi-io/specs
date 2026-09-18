# Implementation Plan: Per-agent public key store

**Branch**: `002-agent-key-store` | **Date**: 2026-09-18 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/002-agent-key-store/spec.md`

## Summary

Keep an accepted agent's public key after enrollment, and make the two things an
agent sends — its job responses and its registration — verifiable against it.
Today the key is written onto the pending-enrollment record and deleted with
that record on acceptance, so every controller-side verification path finds no
key and skips. One store closes both open advisories: GHSA-3jh4's deferred
response half, and GHSA-j73r, where an unauthenticated registration lets a
machine claim a hostname it never enrolled under and receive that host's work.

Approach: store the key in the enrollment KV under a distinct prefix at the
moment of acceptance, sign registrations with the agent's existing key, and
verify both paths against the store. Enforcement is opt-in per side, so an
upgrade changes nothing until an operator turns it on.

## Technical Context

**Language/Version**: Go, `go 1.26.0` directive, CI builds the floor and stable.

**Primary Dependencies**: NATS JetStream KV (`nats-io/nats.go/jetstream`),
`crypto/ed25519`, the sibling `osapi-io/nats-client`. No new dependency.

**Storage**: NATS JetStream KV. The enrollment bucket already exists and already
holds `PendingAgent` records under the `enrollment.` prefix. Accepted keys go in
the same bucket under a second prefix, so no new bucket, config field, or
provisioning step appears.

**Testing**: `testify/suite` table tests with `validateFunc`, generated mocks,
`just test` as the gate at 99.9% coverage; integration under `test/integration`
behind the `integration` build tag.

**Target Platform**: Linux controller and agents; Darwin for development.

**Project Type**: Single Go module — controller, agent and shared packages.

**Performance Goals**: Verification adds one KV read per verified message on the
controller. Agents heartbeat every 10s and jobs are human-triggered, so the
added load is proportional to fleet size, not throughput. A per-machine-ID cache
with invalidation on acceptance and removal keeps steady-state reads near zero.

**Constraints**: No new configuration knob — `ControllerPKI.Enabled`,
`AgentPKI.Enabled` and `ControllerPKI.RotationGracePeriod` already exist and are
documented as covering exactly this. Behaviour with PKI disabled must be
byte-for-byte unchanged. Signature verification must never fail open.

**Scale/Scope**: Fleets in the hundreds. One key per machine ID, plus at most
one superseded key during a rotation grace period.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                                                                         | Assessment                                                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Documentation** — a repository states in full the conventions binding it        | `agent-identity.md` gains what is signed, what is verified, what each failure means, and the rollout order. Nothing is left to this plan alone. **Pass.**                                                                                              |
| **Verification** — a claim is measured, not inspected                             | Every requirement maps to a test: forged response rejected, unsigned registration invisible to targeting, contested hostname resolved deterministically, grace period honoured then expired, removal effective. `just test` is the evidence. **Pass.** |
| **Tooling** — a tool a repository invokes is declared where it declares its tools | No new tool or dependency. **Pass.**                                                                                                                                                                                                                   |
| **Correction** — when applying a rule shows the rule is wrong, fix the rule first | The spec already records one such correction: FR-009 began as an open question and was settled by clarify before planning, not during implementation. **Pass.**                                                                                        |
| **Workflow** — design output goes where the workflow reads it                     | This plan, its research and design artifacts live in the feature directory and consolidate into memory on archive. **Pass.**                                                                                                                           |

No violations. Complexity Tracking is therefore empty and omitted.

## Project Structure

### Documentation (this feature)

```text
specs/002-agent-key-store/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── key-store.md     # Phase 1 output: the store's contract and failure modes
├── checklists/
│   └── requirements.md  # From /speckit-specify, updated by /speckit-clarify
└── tasks.md             # Phase 2 output (/speckit-tasks, not created here)
```

### Source Code (repository root)

```text
internal/controller/enrollment/
├── types.go             # AcceptedAgent record, store interface
├── accept.go            # write the key on accept; remove it on reject
├── keystore.go          # new: lookup, put, remove, rotation grace
└── keystore_public_test.go

internal/job/client/
├── signing.go           # verify responses against the store, not a nil check
├── agent.go             # ListAgents surfaces whether a key is held
└── client.go            # response paths fail closed when enforcing

internal/agent/
├── heartbeat.go         # sign the registration
└── pki/                 # existing Sign/Fingerprint/VerifyWithGrace, unchanged

internal/validation/
└── target.go            # only verified registrations are resolvable

internal/controller/api/agent/
└── agent_list.go        # expose key-held state in the fleet view

docs/docs/sidebar/features/
└── agent-identity.md    # what is signed, what is verified, rollout order
```

**Structure Decision**: The store belongs to the enrollment package, because
acceptance is the only event allowed to write it (FR-002) and enrollment already
owns that moment and the KV handle. Verification callers depend on a narrow
lookup interface rather than on the enrollment package's internals, so the job
client and target resolution do not import enrollment wholesale.
