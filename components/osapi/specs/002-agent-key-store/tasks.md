# Tasks: Per-agent public key store

**Input**: Design documents from `specs/002-agent-key-store/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md),
[research.md](research.md), [data-model.md](data-model.md),
[contracts/key-store.md](contracts/key-store.md), [quickstart.md](quickstart.md)

**Tests**: Included. Coverage is gated at 99.9% by `just test`, so a task that
adds a branch without a test cannot merge — test tasks are not optional here.

**Organization**: Grouped by the spec's three user stories. US1 and US2 are both
P1 and both independently shippable once the foundation lands; US3 is P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel — different file, no dependency on an incomplete
  task
- **[Story]**: the user story the task serves; Setup, Foundational and Polish
  carry no story label

## Path Conventions

Paths are relative to the `osapi` repository root, not this repository. The
design documents live here; the code lives in
`https://github.com/osapi-io/osapi`.

______________________________________________________________________

## Phase 1: Setup

**Purpose**: Make the local gate runnable before any code changes.

- [ ] T001 Run `mise exec -- just react-build` to populate `ui/dist`, without
  which `just ready` fails typechecking `ui/embed.go`
- [ ] T002 Record the baseline by running `mise exec -- just ready` and
  `mise exec -- just test`, capturing the current filtered coverage total from
  `just test` output so the 99.9% gate is measured against a known start

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The store itself, and the single write point. Every user story
verifies against this, so none can begin until it exists.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Add the `AcceptedAgent` record — machine ID, hostname, public key,
  fingerprint, accepted-at, optional superseded key and superseded-until instant
  — in `internal/controller/enrollment/types.go`, per
  [data-model.md](data-model.md)
- [ ] T004 Add the `accepted.` key prefix constant beside the existing
  `enrollment.` prefix in `internal/controller/enrollment/types.go`, so both
  prefixes are declared in one place
- [ ] T005 Add the three verification-outcome sentinels — no stored key,
  signature mismatch, store unavailable — in
  `internal/controller/enrollment/keystore.go`, mirroring the agent-side
  sentinels `ErrControllerKeyUnknown` / `ErrJobSignatureInvalid` /
  `ErrJobEnvelopeMissing` (FR-010)
- [ ] T006 Implement `Record`, `Lookup` and `Remove` against the enrollment KV
  bucket in `internal/controller/enrollment/keystore.go`, with a read failure
  returning the store-unavailable sentinel and a missing record returning the
  no-stored-key sentinel — the two must never be the same answer
  ([contracts/key-store.md](contracts/key-store.md))
- [ ] T007 Add the per-machine-ID lookup cache in
  `internal/controller/enrollment/keystore.go`, invalidated by `Record` and
  `Remove` and never by elapsed time (research decision 7; a TTL would leave a
  removed agent verifying, which FR-008 forbids)
- [ ] T008 Declare the narrow lookup interface the verification callers depend
  on in `internal/controller/enrollment/keystore.go`, so `internal/job/client`
  and `internal/validation` do not import the enrollment package wholesale (plan
  Structure Decision)
- [ ] T009 Write the accepted key at acceptance and remove it on rejection in
  `internal/controller/enrollment/accept.go`, replacing the current behaviour
  where deleting the pending record discards the only copy of the key (FR-001,
  FR-002, FR-008)
- [ ] T010 Wire the store through `setupEnrollmentWatcher` in
  `cmd/controller_setup.go` so the watcher, the job client and target resolution
  share one instance and therefore one cache
- [ ] T011 Register the lookup interface for mock generation and run
  `mise exec -- just generate`; generated mocks only, no handwritten fakes
- [ ] T012 Add `testify/suite` table tests with `validateFunc` for record,
  lookup, remove, cache invalidation and each distinct failure cause in
  `internal/controller/enrollment/keystore_public_test.go`
- [ ] T013 Add table tests covering key stored on accept and key removed on
  reject in the existing accept tests under `internal/controller/enrollment/`

**Checkpoint**: The controller retains an accepted agent's key, and can look it
up and remove it. US1 and US2 can now proceed in parallel.

______________________________________________________________________

## Phase 3: User Story 1 - The controller can tell a real agent's answer from a forged one (Priority: P1) 🎯 MVP

**Goal**: A job response is verified against the responding agent's stored key
before it is treated as a result. Closes the deferred half of GHSA-3jh4.

**Independent Test**: A response with a valid signature is accepted; the same
response re-signed by a different key is rejected and the job does not report
success.

- [ ] T014 [US1] Replace the nil-counterpart-key skip in `unwrapSignedEnvelope`
  in `internal/job/client/signing.go` with a store lookup by the responding
  agent's machine ID, so verification is inert only when the controller is not
  enforcing (FR-003, FR-011)
- [ ] T015 [US1] Map each lookup and verification result to its own outcome in
  `internal/job/client/signing.go` — verified, no stored key, signature
  mismatch, store unavailable, not enforcing — with no path collapsing two of
  them (FR-010)
- [ ] T016 [US1] Fail closed on the single-target response path in
  `internal/job/client/client.go`: a rejected response makes the job report
  failure rather than returning an unverified result
- [ ] T017 [US1] Fail closed on the broadcast response path in
  `internal/job/client/client.go`: a rejected response does not count as that
  agent's reply and the agent is reported as not having answered
  ([contracts/key-store.md](contracts/key-store.md) Response verification)
- [ ] T018 [P] [US1] Add table tests in `internal/job/client/` for a response
  signed by the stored key, one signed by a foreign key, one unsigned, one with
  no stored record, and one where the store read fails — asserting a distinct
  outcome for each
- [ ] T019 [P] [US1] Add a table test asserting that with
  `ControllerPKI.Enabled` false the response path behaves exactly as before,
  byte for byte (SC-005)

**Checkpoint**: Job response verification is live and enforceable. GHSA-3jh4 is
fully closed.

______________________________________________________________________

## Phase 4: User Story 2 - A host's name cannot be claimed by another machine (Priority: P1)

**Goal**: A registration is authenticated before targeting reads it, and a
contested hostname resolves to the machine that enrolled under it. Closes
GHSA-j73r.

**Independent Test**: A registration whose signature does not verify against the
stored key for its machine ID is not visible to targeting, and work aimed at
that hostname still reaches the enrolled machine.

- [ ] T020 [US2] Add the canonical serialisation of a registration's
  identity-bearing fields — machine ID, hostname, fingerprint — as a shared
  helper both sides derive identically, in a new `internal/job/registration.go`
  (research decision 8; do not sign the marshalled struct, whose field order and
  optional fields can vary)
- [ ] T021 [US2] Add the signature field to `AgentRegistration` in
  `internal/job/types.go` alongside its existing self-reported `Fingerprint`,
  carried beside the signed bytes rather than inside them
- [ ] T022 [US2] Sign the canonical bytes in `writeRegistration` in
  `internal/agent/heartbeat.go` using the agent's existing PKI manager, and
  leave the registration unsigned when `AgentPKI.Enabled` is false
- [ ] T023 [US2] Add registration verification against the stored record —
  signature valid, hostname matching, fingerprint matching — in
  `internal/validation/target.go` or a helper it calls, returning resolvable or
  one of the stated non-resolvable causes (FR-004, FR-005)
- [ ] T024 [US2] Filter `ResolveTarget` in `internal/validation/target.go` to
  resolvable registrations only, so an unverified registration is invisible to
  target resolution, label matching, facts and fleet status
- [ ] T025 [US2] Make a contested hostname deterministic in
  `internal/validation/target.go`, preferring the enrolled machine rather than
  the first registry entry claiming the name — the current first-entry-wins
  behaviour is GHSA-j73r (FR-006)
- [ ] T026 [P] [US2] Add table tests in `internal/agent/` asserting the
  registration is signed over the canonical bytes when agent PKI is on and
  unsigned when it is off
- [ ] T027 [P] [US2] Add table tests in `internal/validation/` for a verified
  registration, an unsigned one, one signed by a foreign key, one whose hostname
  differs from the record, one whose fingerprint differs, and one with no stored
  record — asserting resolvability for each
- [ ] T028 [P] [US2] Add a table test for two registrations claiming one
  hostname where only one is resolvable, asserting the enrolled machine resolves
  and the result does not depend on iteration order (SC-002)

**Checkpoint**: Targeting trusts only authenticated registrations. GHSA-j73r is
closed.

______________________________________________________________________

## Phase 5: User Story 3 - Keys change without an outage, and leave when the agent does (Priority: P2)

**Goal**: A rotation replaces the stored key and accepts the previous one for a
bounded grace period; a removal takes effect immediately.

**Independent Test**: After a rotation, messages signed with the new key verify,
messages signed with the previous key verify until the grace period lapses, and
messages signed with a removed key never verify.

- [ ] T029 [US3] On re-acceptance, move the outgoing key to the superseded key
  and set superseded-until from `ControllerPKI.RotationGracePeriod` in
  `internal/controller/enrollment/keystore.go` — store the instant, not the
  duration, so a restart cannot extend the window (FR-007)
- [ ] T030 [US3] Verify against the current key, then the superseded key while
  inside its grace period, in `internal/controller/enrollment/keystore.go`,
  mirroring `VerifyWithGrace` in `internal/agent/pki` so operators meet one
  rotation concept
- [ ] T031 [US3] Treat a signature that matches only an expired superseded key
  as a signature mismatch, not as a separate outcome
  ([contracts/key-store.md](contracts/key-store.md))
- [ ] T032 [US3] Remove the stored record and invalidate its cache entry in both
  `RejectAgent` and `RejectByHostname` in
  `internal/controller/enrollment/accept.go`, so nothing signed by the removed
  key verifies afterwards (FR-008) — note
  `internal/controller/enrollment/rotation.go` rotates the *controller* key and
  is out of scope
- [ ] T033 [P] [US3] Add table tests in `internal/controller/enrollment/` for
  rotation: new key verifies, superseded key verifies inside grace, superseded
  key fails after the instant passes, and a third key never verifies
- [ ] T034 [P] [US3] Add a table test asserting a removed agent's key stops
  verifying immediately, with no cached hit surviving the removal

**Checkpoint**: Verification can be enabled without rotation or decommissioning
becoming a reason to disable it.

______________________________________________________________________

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T035 Report per agent whether a key is stored, and its fingerprint, from
  `ListAgents` in `internal/job/client/agent.go` — the fields go on `AgentInfo`
  in `internal/job/types.go`, which is what `ListAgents` returns and is a
  separate struct from `AgentRegistration` (FR-012, SC-003)
- [ ] T036 Surface the key-held state and fingerprint in the fleet view response
  in `internal/controller/api/agent/agent_list.go`, then run
  `mise exec -- just generate` for the OpenAPI and SDK artifacts
- [ ] T037 Document what is signed, what is verified, what each of the failure
  causes means, and the rollout order — controller side first, re-enrol the
  agents the fleet view shows without a key, then agent side — in
  `docs/docs/sidebar/features/agent-identity.md` (FR-013, SC-007)
- [ ] T038 Bring the filtered coverage total back to 99.9% against the T002
  baseline, adding table rows rather than `//nolint` or ignore directives
- [ ] T039 Run the full gate in order:
  `mise exec -- just react-build && mise exec -- just generate && mise exec -- just ready && mise exec -- just test && mise exec -- just docusaurus-fmt-check`
  — the last is required because T037 touches `docs/`, which `just md-fmt`
  excludes
- [ ] T040 Walk [quickstart.md](quickstart.md) end to end against a running
  controller and agent, confirming each stated outcome
- [ ] T041 Add the fix to GHSA-3jh4 and GHSA-j73r once merged, so both
  advisories are ready to publish with the first release

______________________________________________________________________

## Dependencies

```text
Setup (T001-T002)
  └─> Foundational (T003-T013)   ← blocks everything below
        ├─> US1 (T014-T019)      ← independent of US2
        ├─> US2 (T020-T028)      ← independent of US1
        └─> US3 (T029-T034)      ← needs Foundational; verifies best after US1
              └─> Polish (T035-T041)
```

- **US1 and US2 are independent.** Both read the store; neither writes it, and
  they touch different files. Either can ship first, and either closes its own
  advisory on its own.
- **US3 depends only on Foundational**, but its grace-period tests are more
  meaningful once US1 exercises the verification path.
- **T036 depends on T035**; **T039 depends on T037**; **T041 depends on the
  whole thing being merged**.

## Parallel Execution Examples

Within Foundational, after T006 lands:

```text
T012 (keystore tests) and T013 (accept tests) — different test files
```

Within US1, after T014-T017 land:

```text
T018 (verification outcome tests) and T019 (PKI-disabled test)
```

Within US2, after T020-T025 land:

```text
T026 (agent signing tests), T027 (resolvability tests), T028 (contested hostname)
```

Across stories, once Foundational is complete, US1 and US2 can be worked
simultaneously by two people without touching the same file.

## Implementation Strategy

**MVP**: Setup + Foundational + US1. That alone closes GHSA-3jh4's deferred half
and makes agent response signing mean something, which is the larger of the two
open advisories.

**Increment 2**: US2. Closes GHSA-j73r. At this point both advisories are fixed
and only a release is needed to publish them.

**Increment 3**: US3 + Polish. Rotation, removal, the fleet view and the docs —
what an operator needs before turning enforcement on across a real fleet.

Enforcement stays off throughout: every increment is safe to merge because
`ControllerPKI.Enabled` and `AgentPKI.Enabled` govern when any of it takes
effect (FR-009, FR-011).
