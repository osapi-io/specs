# Data Model: Per-agent public key store

Phase 1. Entities, their rules, and the transitions between them.

## AcceptedAgent

The stored record. One per accepted agent, in the enrollment KV bucket under
`accepted.<machine-id>`.

| Field            | Meaning                                         | Rules                                                                 |
| ---------------- | ----------------------------------------------- | --------------------------------------------------------------------- |
| Machine ID       | The agent's permanent identifier                | Required; the key of the record; never changes for a record           |
| Hostname         | The hostname claimed at acceptance              | Required; what a registration's hostname is checked against           |
| Public key       | The key every later message is verified against | Required; recorded only at acceptance (FR-002)                        |
| Fingerprint      | Digest of the public key                        | Required; what the fleet view shows                                   |
| Accepted at      | When acceptance happened                        | Required                                                              |
| Superseded key   | The key replaced by the most recent rotation    | Optional; absent unless a rotation is inside its grace period         |
| Superseded until | When the superseded key stops being accepted    | Required when a superseded key is present; an instant, not a duration |

**Identity**: machine ID. Two records cannot share one, and a record is replaced
in place rather than duplicated.

**Lifecycle**:

```text
(none) ──accept──> current key
current key ──accept again (rotation)──> new current key + superseded key + expiry
current key + superseded ──expiry passes──> current key only
any state ──reject or remove──> (none)
```

Only enrollment acceptance moves a record rightwards. Nothing an agent sends
creates, changes or refreshes one (FR-002).

## Registration claim

What the agent publishes about itself, already present as `AgentRegistration` in
the registry bucket. This feature adds a signature and reclassifies two fields.

| Field       | Before                               | After                                                                                  |
| ----------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| Machine ID  | Self-reported, trusted               | Self-reported, used only to find the stored record                                     |
| Hostname    | Self-reported, trusted for targeting | A claim, valid only when the signature verifies against the record found by machine ID |
| Fingerprint | Self-reported, unchecked             | A claim, must match the stored fingerprint                                             |
| Signature   | Absent                               | Required when the controller is enforcing; covers the identity-bearing fields          |

**Rule**: a registration is *resolvable* — visible to target resolution, labels,
facts and fleet status — only when its signature verifies against the stored
record for its machine ID (FR-004, FR-005). An unresolvable registration is not
an error to the agent; it is simply not authoritative.

**Contested hostname**: when more than one registration claims a hostname, only
resolvable ones are candidates, and among those the enrolled machine wins
deterministically (FR-006).

## Job response claim

What an agent returns for a unit of work. Already signed by the agent; this
feature makes the signature checkable.

| Property            | Rule                                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Verified            | Signature checks out against the stored record for the responding agent                                          |
| Rejected            | Signature absent, malformed, or signed by a key that is neither current nor within-grace superseded              |
| Effect of rejection | The response is not a result: single-target reports failure, broadcast drops it from that agent's tally (FR-003) |

## Verification outcome

Every verification resolves to exactly one of these, and they are never
collapsed (FR-010):

| Outcome            | Meaning                                                 | What an operator does                                   |
| ------------------ | ------------------------------------------------------- | ------------------------------------------------------- |
| Verified           | Signature matched current or within-grace key           | Nothing                                                 |
| No stored key      | The agent has not been accepted since the store existed | Re-enrol that agent; expected during rollout            |
| Signature mismatch | A key that is not this agent's signed the message       | Investigate; this is the attack the advisories describe |
| Store unavailable  | The record could not be read                            | Investigate the store; never treated as verified        |
| Not enforcing      | PKI is off for this side                                | Nothing; pre-existing behaviour (FR-009)                |

## Relationships

```text
AcceptedAgent 1 ──── * Registration claim     (by machine ID; verifies it)
AcceptedAgent 1 ──── * Job response claim     (by machine ID; verifies it)
AcceptedAgent 0..1 ── 1 Superseded key        (only during a rotation grace period)
```

The store is the authority. Both claim types carry self-reported identity, and
neither may write to the store.
