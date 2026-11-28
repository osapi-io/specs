# Admission

Admission decides which machines can join osapi. PKI is always on: a new agent
asks to join, and it gets no work until an operator admits it. The operator can
also reject the request, or revoke a machine that was admitted before.
[Agent identity](agent-identity.md) tells what the stored key proves after
admission. This page tells how a machine gets that key, and who decides.

## The four states

Each machine has one admission record. The **machine ID** is the key of the
record, not the hostname. A hostname can change, and two machines can have the
same hostname.

| State      | Means                                                 | Next                   |
| ---------- | ----------------------------------------------------- | ---------------------- |
| `pending`  | The machine asked to join. Nobody decided.            | `admit` or `reject`    |
| `admitted` | The controller stores the key, and the machine works. | `revoke`               |
| `rejected` | An operator refused the request, with a reason.       | The machine asks again |
| `revoked`  | An operator removed the key of an admitted machine.   | The machine asks again |

The store is the enrollment bucket in NATS KV. Each state has a key prefix:
`enrollment.` for pending, `accepted.` for admitted, `rejected.` and `revoked.`
for the decisions. The prefixes of pending and admitted are older than the word
admission. They stay, because a new name would orphan the keys that a running
controller has. `internal/controller/admission/store.go` reads the four.

The type of the four states is `types.AdmissionState`, in `pkg/sdk/types`. The
states cross the API: the `state` filter of the list and the state of each
record use the type. Thus the spec has one `AdmissionState` schema, and the SDK
and the UI use it.

One machine can have more than one record at a time. A revoked machine that asks
again has a `revoked.` record and an `enrollment.` record. The store returns one
record for each machine, in this order: pending, admitted, rejected, revoked.
When the first is pending and there is a second, the record shows the second as
`previous`, with its fingerprint as `previous_fingerprint`. Thus an operator
sees that a request comes from a machine that was rejected or revoked before,
and sees when its key changed. Admission deletes the `rejected.` and `revoked.`
records of the machine.

## The API

The admission group is an [endpoint group](endpoints.md), in
`internal/controller/endpoints/admission`. The CLI commands, the spec and the
CLI pages are generated from it.

| Route                                     | CLI                             | Permission        |
| ----------------------------------------- | ------------------------------- | ----------------- |
| `GET /api/admission[?state=]`             | `osapi client admission list`   | `admission:read`  |
| `GET /api/admission/{machine_id}`         | `osapi client admission get`    | `admission:read`  |
| `POST /api/admission/{machine_id}/admit`  | `osapi client admission admit`  | `admission:write` |
| `POST /api/admission/{machine_id}/reject` | `osapi client admission reject` | `admission:write` |
| `POST /api/admission/{machine_id}/revoke` | `osapi client admission revoke` | `admission:write` |
| `DELETE /api/admission/{machine_id}`      | `osapi client admission delete` | `admission:write` |

The three decisions and the delete answer 204. A machine ID with no record, or
with no record in the state that the decision needs, answers 404. The controller
always runs admission, and does not start when the enrollment bucket does not
open. Thus no route answers that admission is off.

`admin` has the two permissions. `operator`, `automation` and `read` have only
`admission:read`. `auditor` and `observer` have neither. Admission decides which
machines can run jobs. Thus it is a separate permission, not part of
`agent:write`, and a token that can drain agents cannot admit one.
[Permissions](permissions.md) has the roles.

## Admit needs the fingerprint from the machine

`admit` takes a fingerprint, and the controller compares it with the fingerprint
of the keys in the request. The fingerprint covers the signing key and the
encryption key of the agent
([Agent identity](agent-identity.md#the-encryption-key)). A different
fingerprint answers 409, and the machine stays pending.

The fingerprint that `admission list` shows comes from the request, and so does
the key. A copy of that value proves nothing. The operator reads the fingerprint
on the machine:

```bash
osapi pki key get --name agent  # on the machine: the keys, the fingerprint, the admit command
osapi client admission admit --machine-id <id> --fingerprint SHA256:...
```

`osapi pki key get --name agent` reads the keys in `agent.pki.key_dir`, and
shows the fingerprint that covers the two keys, with the command that admits the
machine. It makes no key: the agent makes its keys at its first start, and
`osapi pki key create --name agent` makes them before then.
`osapi pki key get --name agent-encryption` shows the public encryption key, in
the nkeys form that starts with `X`. When the two fingerprints are the same, the
request came from the machine that the operator looked at, not from a different
publisher on the bus. The controller calculates the fingerprint of the request
from its two public keys. It does not use the fingerprint that the request
states. Each record of the API has the public encryption key as
`encryption_key`.

A pending agent writes the same instruction to its log, with its machine ID and
fingerprint, when it starts.

## Reject, revoke and delete

`reject` takes an optional reason, up to 1024 characters. The controller sends
the rejection to the agent, deletes the request, and keeps a `rejected.` record
with the reason and the time.

`revoke` removes the stored key at once. After that, nothing that the machine
signs verifies, and it gets no work. The controller keeps a `revoked.` record.
It does not tell the agent. [Agent identity](agent-identity.md) tells how to
make the machine ask again.

`delete` removes the stored key and each record of the machine, in each state,
and keeps none. A machine that asks again after a delete is new: its request
shows no `previous`.

Revoke and delete both stop the machine at once. They differ in what remains.
Revoke is for a machine that is not trusted: the record stays, so the machine is
flagged if it asks again. Delete is for a machine that goes away on purpose,
such as a VM that is rebuilt or removed. Nothing about it was wrong, so nothing
about it remains. Automation that rebuilds a machine deletes it first.

## Machines that stop reporting

A machine that goes away without a delete keeps its key, and a stored key is
trust that nobody uses. `controller.pki.delete_after` deletes an admitted
machine that has not reported for that long, such as `720h`. It is empty by
default, and empty is never.

The controller looks once a minute (`RunStaleCleanup` in
`internal/controller/admission/delete.go`). A machine is stale when it is not in
the registry, and its last report is older than `delete_after`. A machine that
never reported uses the time of its admission. Only admitted machines are
deleted. A pending, rejected or revoked record stays.

When the registry or the last reports do not read, the controller deletes
nothing. A machine that the controller cannot see is not a machine that is gone,
and an outage of the bus must not delete the fleet. A machine that was offline
for less than `delete_after` keeps its key, because its last report stays in the
state bucket while the registry entry expires.

## Online and last seen

Each record shows whether the agent reports now, and when it reported last.
`online` comes from the agent registry: an agent with a live heartbeat is
online, and its last report is the time of that heartbeat. The registry entry
expires with its TTL. Thus each agent also writes `seen.<machine_id>` to the
state bucket, once a minute (`seenInterval` in `internal/agent/heartbeat.go`).
That key keeps the last report of an agent that stopped. A machine that never
reported has no last seen.

## A join token admits

A join token is an operator's decision made ahead of time. An agent that joins
with one ([Agent join](agent-join.md)) is admitted at once, with no pending
record, and its admitted record names the token as `join_token`. A join clears
an earlier pending, rejected or revoked record of the machine, as an admit does.

A join does not replace the key of an admitted machine. A join for a machine ID
that is admitted with different keys is refused with a 409
(`admission.ErrMachineAdmitted`), before the token loses a use. A join with the
same keys and a new token admits the machine again. To join a machine with new
keys, an operator deletes its admission first. An agent that changes its own
keys uses a rotation, which its old key signs
([Agent identity](agent-identity.md#rotation-without-an-outage)).

## Automatic admission

`controller.pki.auto_admit: true` admits each request when it arrives, with no
check of the fingerprint. It is for development and tests, such as a lab that
makes new VMs at each push. The setting was `auto_accept` before 18 November
2026\. The old name does nothing now.

Automatic admission does not admit a request whose keys are not the keys of an
admitted machine with the same ID. That request stays pending, so that an
operator compares its fingerprint with the host. A request carries no proof that
it comes from the machine, so an automatic admission of it would replace the
admitted key.

## Traces

Each store operation is a span: `admission.list`, `admission.get`,
`admission.admit`, `admission.reject`, `admission.revoke` and
`admission.delete`, with the attribute `osapi.agent.machine_id`.
`admission.list` has `osapi.admission.count`. The trace table of the CLI and the
UI show the machine ID as `machine=<id>`. [Observability](observability.md) has
the others.

## The UI

Admin › Admission shows the records in four sections, in the order of the states
above. Each card shows the fingerprint and the public encryption key. A pending
card has Admit and Reject. Admit opens a field for the fingerprint, and the
button stays off until it has a value. An admitted card has Revoke, which needs
a second click. Each card has Delete, which also needs a second click. A token
without `admission:write` sees the cards without the buttons.

## What this page does not cover

- The key handshake, job signatures and key rotation:
  [agent identity](agent-identity.md).
- Why a pending agent gets no work, and the drain states:
  [the job system](job-system.md).
