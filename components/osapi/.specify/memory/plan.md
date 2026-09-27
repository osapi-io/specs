# Main Implementation Plan

> **Revision**: 2026-09-26 — Seeded from the provider contract
> (`specs/001-provider-contract`). A documentation feature: no dependencies, no
> modules, no configuration, no routing. That feature's plan was written
> retrospectively to satisfy the archival gate, so what is recorded here is the
> shape the work had rather than a plan that directed it.

> **Revision**: 2026-09-26 — Composed the per-agent public key store
> (`specs/002-agent-key-store`) into the shared fields. This is the first feature
> with code, so Language/Version, Primary Dependencies, Storage, Testing, Target
> Platform, Project Type, Performance Goals, Constraints and Scale/Scope each now
> carry a real value beside the corpus one. No scalar conflicts: the corpus fields
> said "not applicable" where this feature states a value.

## Summary

The provider contract is stated in the corpus rather than inferred from whichever
sibling provider a reader opens first. Sixteen requirements, all of the form "the
corpus MUST state X", documenting practice the fourteen node providers and their
categorized siblings already follow.
[Source: specs/001-provider-contract/plan.md -> "Summary"]

## Technical Context

**Language/Version**: Go, `go 1.26.0` directive, CI builds the floor and stable.
The corpus itself is Markdown with no compiled artifact.
[Source: specs/002-agent-key-store/plan.md -> "Language/Version"]
[Source: specs/001-provider-contract/plan.md -> "Language/Version"]

**Primary Dependencies**: NATS JetStream KV (`nats-io/nats.go/jetstream`),
`crypto/ed25519`, and the sibling `osapi-io/nats-client`. The corpus itself
depends on nothing at runtime.
[Source: specs/002-agent-key-store/plan.md -> "Primary Dependencies"]
[Source: specs/001-provider-contract/plan.md -> "Primary Dependencies"]

**Storage**: NATS JetStream KV. The enrollment bucket holds pending records under
an `enrollment.` prefix and accepted agents' keys under `accepted.`, so no new
bucket, config field or provisioning step appears. Corpus content lives in
`components/osapi/specs/`, `.specify/memory/`, and the skill references that cite
them. [Source: specs/002-agent-key-store/plan.md -> "Storage"]
[Source: specs/001-provider-contract/plan.md -> "Storage"]

**Testing**: In osapi, `testify/suite` table tests with `validateFunc`, generated
mocks only, and `just test` as the gate at 99.9% coverage; integration tests live
under `test/integration` behind the `integration` build tag. In the specs
repository, `just test` runs `mdformat --check`, `just-fmt-check`, and
`scripts/validate-skills.py` over every `SKILL.md` and the relative links in its
references. [Source: specs/002-agent-key-store/plan.md -> "Testing"]
[Source: specs/001-provider-contract/plan.md -> "Testing"]

**Target Platform**: Linux controller and agents; Darwin for development. The
corpus has no target platform — its readers are contributors and agents.
[Source: specs/002-agent-key-store/plan.md -> "Target Platform"]
[Source: specs/001-provider-contract/plan.md -> "Target Platform"]

**Project Type**: Single Go module — controller, agent and shared packages —
alongside a documentation corpus.
[Source: specs/002-agent-key-store/plan.md -> "Project Type"]
[Source: specs/001-provider-contract/plan.md -> "Project Type"]

**Performance Goals**: Verification adds one KV read per verified message on the
controller. Agents heartbeat every 10s and jobs are human-triggered, so the added
load is proportional to fleet size rather than throughput; a per-machine-ID cache
invalidated on acceptance and removal keeps steady-state reads near zero.
[Source: specs/002-agent-key-store/plan.md -> "Performance Goals"]

**Constraints**: No new configuration knob — `ControllerPKI.Enabled`,
`AgentPKI.Enabled` and `ControllerPKI.RotationGracePeriod` already cover
enforcement and rotation. Behaviour with PKI disabled is byte-for-byte unchanged,
and signature verification never fails open. Separately, a rule lives in exactly
one place: two copies drift, and the copy an agent happened to load wins.
[Source: specs/002-agent-key-store/plan.md -> "Constraints"]
[Source: specs/001-provider-contract/plan.md -> "Constraints"]

**Scale/Scope**: Fleets in the hundreds. One stored key per machine ID, plus at
most one superseded key during a rotation grace period. The corpus side is sixteen
requirements covering one layer of one repository.
[Source: specs/002-agent-key-store/plan.md -> "Scale/Scope"]
[Source: specs/001-provider-contract/plan.md -> "Scale/Scope"]

## Project Structure

```text
internal/controller/enrollment/
├── types.go             AcceptedAgent record, AgentKeyStore interface
├── keystore.go          record, look up, remove, rotation grace, cache
├── keystore_adapter.go  adapts the watcher to the job client's lookup
└── accept.go            writes the key on accept, removes it on reject

internal/job/
├── registration.go      canonical bytes an agent signs when registering
└── client/
    ├── types.go         AgentKey, AgentKeyStore, the rejection causes
    ├── signing.go       verifies a response against the stored key
    └── agent.go         ListAgents reports verified and key-stored state

internal/agent/heartbeat.go    signs the registration
internal/validation/target.go  only verified registrations resolve

components/osapi/specs/001-provider-contract/spec.md    the provider contract
components/osapi/.specify/memory/spec.md                where archival puts it
.claude/skills/add-a-domain/references/provider.md      cites it, per FR-016
```

**Structure Decision**: The key store belongs to the enrollment package, because
acceptance is the only event allowed to write it and enrollment already owns that
moment and the KV handle. Verification callers depend on a narrow lookup interface
declared in the job client, so neither the client nor target resolution imports the
enrollment package wholesale.
[Source: specs/002-agent-key-store/plan.md -> "Structure Decision"]

For the corpus: the rule lives in it and the skill points at it.
FR-016 makes that direction binding rather than conventional, so the skill
reference holds only what the specification does not: where a provider's files
go, what they are called, and the scaffolding to start from.
[Source: specs/001-provider-contract/plan.md -> "Structure Decision"]

## Testing Strategy

`just test` in the specs repository is the gate for corpus work: mdformat over
the markdown, justfile formatting, and the skill validator, which checks each
`SKILL.md` against the Agent Skills specification and resolves every relative
link in its references. A citation into the corpus that does not resolve fails
the build, which is what keeps FR-016's direction enforceable rather than
aspirational.
[Source: specs/001-provider-contract/plan.md -> "Testing"]

## Configuration

No new configuration. `ControllerPKI.Enabled` governs controller-side enforcement,
`AgentPKI.Enabled` the agent side, and `ControllerPKI.RotationGracePeriod` how long
a replaced agent key keeps verifying. All three already existed and were already
documented as covering PKI enrollment and signing.
[Source: specs/002-agent-key-store/plan.md -> "Constraints"]

## Routing & Navigation

`GET /agent` reports `key_stored` and `verified` per agent, so a rollout can be
staged before enforcement is enabled. No new endpoint.
[Source: specs/002-agent-key-store/spec.md -> FR-012]
