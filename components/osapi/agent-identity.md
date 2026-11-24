# Agent identity

The controller must know two things. An answer came from the machine that it
addressed. A machine that claims a hostname is the machine that enrolled with
that hostname. The two facts come from one stored signing key for each agent.

## Enrollment is the only thing that writes a key

osapi keeps the public key of an accepted agent after the enrollment handshake.
It keeps the key for the **machine ID** of the agent, not for its hostname. It
records the fingerprint at the time of acceptance.

**Only the acceptance of an enrollment can make or replace that key.** A message
with a different key cannot do it. A new registration cannot do it. A restart
cannot do it. Thus an attacker who can publish to the bus cannot change a key by
a publish. The trust anchor stays where an operator put it.

The agent obeys the same rule for its own keys. It makes the signing keypair
only when neither file exists. A key file that it cannot read stops the agent
with an error. Examples are a file that root still owns after the user of the
agent changed, or one half of a pair. A replacement key gives no signal. The new
key is not the accepted key. Thus the host stops getting jobs, and nothing at
the agent tells why.

Only two events destroy a key:

- an operator rejects a pending request
- an operator revokes an admitted machine

The two take effect immediately. There is no time when the signature of a
removed agent still verifies.

The revocation is `POST /api/admission/{machine_id}/revoke`, or
`osapi client admission revoke`. It deletes the admitted record and removes the
cached key. The machine ID selects the machine, because a hostname is not an
identity. [Admission](admission.md) has the decisions and who can make them.

osapi does not tell the removed agent. The agent keeps the key of the controller
from its acceptance. Thus it thinks that it is enrolled, and does not ask again.
To enroll it again, do a step on the host: delete `controller.pub` and restart
the agent.

## The encryption key

Each agent has two keys in `agent.pki.key_dir`:

| File         | Key     | Use                                      |
| ------------ | ------- | ---------------------------------------- |
| `agent.key`  | Ed25519 | signs job responses and registrations    |
| `agent.pub`  | Ed25519 | the public half of the signing key       |
| `agent.xkey` | X25519  | opens a value that the controller sealed |

One key does not do both jobs. The signing key signs, and the encryption key
opens. `agent.xkey` is an nkeys curve seed, and the seed contains its public
key. Thus it is one file, and there is no half pair.

The agent makes the encryption key when it loads the signing key. It makes the
key only when `agent.xkey` does not exist. A file that it cannot read, or a file
that is not a curve seed, stops the agent with an error, as for the signing key.

The enrollment request sends the two public keys. The fingerprint covers the
two. It is the SHA-256 hash of the 32 bytes of the Ed25519 public key, then the
32 bytes of the X25519 public key, in the form `SHA256:<hex>`. The controller
calculates it from the two keys in the request. Thus the operator who admits the
fingerprint admits the two keys. The admitted record in the enrollment KV keeps
the two public keys. `GET /agent` and the signed registration show the same
fingerprint.

The controller does not keep a request that has no encryption key, or one that
is not an X25519 public key. It writes a warning to its log. An agent older than
the controller sends a request of this type. Upgrade the agent.

The controller has no encryption key. Its fingerprint is the hash of its Ed25519
public key only.

The job client seals the job key of each job with secrets to this key, and the
agent opens it
([Job system](job-system.md#a-secret-in-the-definition-is-sealed)).

### An agent that was admitted before the encryption key

osapi has no compatibility for an agent that was admitted before the encryption
key. When the new agent starts, it makes `agent.xkey`, and its fingerprint
changes. Its signing key does not change. Thus it keeps its work, but its
admitted record has no encryption key. Enroll it again:

1. On the host, delete `controller.pub` in `agent.pki.key_dir`, and restart the
   agent. The agent sends a new request with the two keys.
2. On the host, run `osapi agent key fingerprint`.
3. Admit the machine with that fingerprint. The pending record shows the old
   fingerprint as `previous_fingerprint`.

## What gets verified

osapi verifies two things. They answer different questions.

**A job response.** The controller verifies it against the key that it recorded
at acceptance. This makes a result trustworthy: the controller knows which
machine made it.

**A registration.** The agent signs it, and the controller verifies it. This
makes *targeting* trustworthy. This half is less clear.

A registration has the hostname, labels, machine ID and status, and targeting
reads it. Without verification, a second machine can publish the same hostname
and get the jobs for the first machine. **Targeting uses only verified
registrations.** Thus an unverified registration cannot get work.

The effect on a result depends on the target of the job:

- A job for a named host that has no verified registration cannot find a target.
- A broadcast is different. `ExpectedAgentHostnames` makes the expected set from
  verified registrations. Thus an unverified agent is **not in the set and makes
  no row**. It does not show as `timeout`, because nothing expected it.

This difference is important when an enrollment has a problem. The symptom is a
broadcast that returns nineteen rows for a fleet of twenty machines. The missing
row gives no error. Look at `GET /agent`, which reports `key_stored` and
`verified`.

## Rotation without an outage

After a key changes, osapi accepts the old key for a grace period. Thus an agent
that changes its key has no time when osapi refuses its messages.

`ControllerPKI.RotationGracePeriod` sets the period. After it ends, messages
with the old key do not verify.

## Failure is never silent

**Verification does not fail open.** When the key store is not available, osapi
does not treat a message as verified. osapi does not believe a message that it
cannot check.

Each rejection has a named cause, not a general failure. Thus an operator can
tell these causes apart:

- an agent that did not enroll
- an incorrect signature
- a key store that osapi cannot reach

## Always on

PKI is always on (osapi-io/osapi#1307). `controller.pki.enabled` and
`agent.pki.enabled` do not exist, and the config check refuses them as unknown
keys. The controller always runs admission and signs each job. The agent always
enrolls at its first start and verifies each job. An agent takes no job until
the controller admits it. `controller.pki.auto_admit` stays, `false` by default,
for a test fleet such as the lab and the integration suite.

The default key directories differ: `/etc/osapi/pki` for the controller and
`/etc/osapi/pki/agent` for the agent. The agent keeps the public key of the
controller as `controller.pub` in its directory, and the controller keeps its
own key with the same name in its directory. With one directory, an agent on the
controller host read the key of the controller as its own enrollment, and never
asked to join.

`GET /agent` reports `key_stored` and `verified` for each agent. An upgrade of
an agent that has no stored key, or no X25519 key, makes it enroll again.

## What this is not

**Transport credentials are not identity.** NATS credentials control who can
connect. This mechanism controls which messages osapi believes after the
connection. An attacker with valid NATS credentials still cannot make a false
response.

Two machines with the same hostname is a supported state, not an error, because
the identity is the machine ID. The two machines exist. Targeting selects one by
a fixed rule, not by the order of arrival.

A machine ID that a second machine uses again does not get trust. The usual
cause is a restored VM image. Only an accepted enrollment replaces the stored
key.

## Where this connects

[The job system](job-system.md) tells what a signed response answers, and where
the signature is in the life of a job.

______________________________________________________________________

Written from `internal/agent/`, `internal/pki/` and
`internal/job/registration.go`.
