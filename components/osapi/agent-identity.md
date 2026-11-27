# Agent identity

The controller must know two things. An answer came from the machine that it
addressed. A machine that claims a hostname holds that hostname: no other
admitted machine has it. The two facts come from one stored signing key for each
agent. The identity is the machine ID and the key. The hostname can change.

## Two things write a key

osapi keeps the public key of an accepted agent after the enrollment handshake.
It keeps the key for the **machine ID** of the agent, not for its hostname. It
records the fingerprint at the time of acceptance.

**Only the acceptance of an enrollment makes that key, and only an acceptance or
a rotation that the key signed replaces it.** A message with a different key
cannot do it. A new registration cannot do it. A restart cannot do it. Thus an
attacker who can publish to the bus cannot change a key by a publish, unless the
attacker holds the admitted private key. The trust anchor stays where an
operator put it.
[The rotation of an agent's keys](#the-rotation-of-an-agents-keys) has the
second case.

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
To enroll it again, do a step on the host: delete `enrolled-controller.pub` and
restart the agent.

The agent saves the controller's key as `enrolled-controller.pub`, not
`controller.pub`, which is the name of the controller's own key pair. The two
share `/etc/osapi/pki` by default. Before osapi-io/osapi#1398 an agent on the
controller's host read the controller's own file, thought that it was enrolled,
and never asked, so no job ran. An agent admitted before then still reads its
`controller.pub`, but only when no `controller.key` is beside it.

## A rename through osapi

The stored record holds the hostname of the machine. An agent cannot change it:
a registration or an answer with a different hostname does not verify. If an
agent could change it, an accepted agent could take the hostname of a different
machine and get its jobs (GHSA-j73r).

`node hostname update` changes it. The operator needs `hostname:write`. The
answer of the update has the old hostname, and the agent signs it, so it
verifies. When that answer is `completed`, the job client writes the new
hostname in the record of its machine ID (`RenameAgentKey`). When the update
completes, the agent reads its new hostname and registers with it at once, not
at its next heartbeat. Then its registrations and its answers have the new
hostname, and they verify.

A rename that osapi did not do, such as `hostnamectl` on the host, does not
change the record. The agent with the new hostname does not verify, and gets no
jobs, until an operator revokes it and it enrolls again (osapi-io/osapi#1352).

## The encryption key

Each agent has two keys in `agent.pki.key_dir`:

| File         | Key        | Use                                      |
| ------------ | ---------- | ---------------------------------------- |
| `agent.key`  | Ed25519    | signs job responses and registrations    |
| `agent.pub`  | Ed25519    | the public half of the signing key       |
| `agent.ekey` | P-256 ECDH | opens a value that the controller sealed |

One key does not do both jobs. The signing key signs, and the encryption key
opens. `agent.ekey` is a PKCS #8 PEM private key, which contains its public key.
Thus it is one file, and there is no half pair. P-256 ECDH is a FIPS 140-3
approved algorithm, from `crypto/ecdh` (osapi-io/osapi#1382).

The agent makes the encryption key when it loads the signing key. It makes the
key only when `agent.ekey` does not exist. A file that it cannot read, or a file
that is not a P-256 key, stops the agent with an error, as for the signing key.
When it makes the key, it removes `agent.xkey`, the X25519 key of an older
agent.

The enrollment request and the join request send the two public keys. The text
form of the encryption key is base64url, with no padding, of the 65 bytes of the
uncompressed P-256 point (`pki.EncryptionKeyEncoding`). The fingerprint covers
the two keys. It is the SHA-256 hash of the 32 bytes of the Ed25519 public key,
then the 65 bytes of the P-256 point, in the form `SHA256:<hex>`. The controller
calculates it from the two keys in the request. Thus the operator who admits the
fingerprint admits the two keys. The admitted record in the enrollment KV keeps
the two public keys. `GET /agent` and the signed registration show the same
fingerprint.

The controller does not keep an enrollment request that has no encryption key,
or one that is not a P-256 public key. It writes a warning to its log. It
refuses a join request of this type with `admission.ErrJoinEncryptionKey`, a
400, before the join token loses a use.

The controller has no encryption key. Its fingerprint is the hash of its Ed25519
public key only.

The job client seals the job key of each job with secrets to this key, and the
agent opens it
([Job system](job-system.md#a-secret-in-the-definition-is-sealed)).

### An agent that was admitted with an X25519 key

osapi has no compatibility for an agent that was admitted with the X25519 key of
the agents before osapi-io/osapi#1382. When the new agent starts, it makes
`agent.ekey`, removes `agent.xkey`, and its fingerprint changes. Its signing key
does not change. Thus it keeps its work, but its admitted record has the X25519
key. The controller cannot seal to that key, and a job with a secret for the
agent fails at the controller with `seal the job key`. Admit it again:

1. On the host, delete `enrolled-controller.pub` in `agent.pki.key_dir`, and
   restart the agent. The agent sends a new enrollment request with the two
   keys. An agent that joined with a join string does this too, because after
   its first join it reads its NATS user from `agent.pki.key_dir`, not the join
   string.
2. On the host, run `osapi pki key get --name agent`.
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

## The hostname follows the machine

An operator knows a host by its hostname, and targets it by its hostname. A
hostname can change: a rename through osapi, a rename by hand, or a rebuild that
keeps the machine ID. The record of the machine keeps its machine ID and its
key, and takes the new hostname.

When a verified registration or a verified answer has a hostname that is not the
hostname of the record, the controller does these steps:

1. It looks for another admitted machine whose registration and record have that
   hostname.
2. If there is one, it refuses the registration, and logs "registration claims
   the hostname of another admitted machine". Thus an admitted agent cannot take
   the name of a different host (GHSA-j73r).
3. If there is none, it moves the record to the new hostname, logs "an agent's
   hostname changed", and writes a `hostname_changed` event to the timeline of
   the machine.

An answer shows under the hostname of the record. A request to the new hostname
right after a rename finds the host: an agent that renames its host registers
with the new hostname before it answers the rename, and the target check reads
the registry again when its cached list does not have the name.

A config that sets `agent.hostname` pins the hostname. A rename of the host then
does not change the hostname that the agent reports.

## Rotation without an outage

After a key changes, osapi accepts the old key for a grace period. Thus an agent
that changes its key has no time when osapi refuses its messages.

`ControllerPKI.RotationGracePeriod` sets the period. After it ends, messages
with the old key do not verify.

### The rotation of an agent's keys

`osapi pki key rotate --name agent` runs on the agent's host. It replaces the
agent's two keys with no new admission:

1. It makes the new keys beside the old keys, as `agent.next.key`,
   `agent.next.pub` and `agent.next.ekey`.
2. It sends a rotation request to the controller over NATS, on `join.rotate`, as
   the agent connects. The request has the machine ID, the new public keys and
   the time. The old signing key signs it, and the new signing key signs it too,
   which shows that the agent holds the new key.
3. The controller checks the time with the skew of a renewal, that the machine
   is admitted, and the old signature against the admission. Then it writes the
   new keys and their fingerprint into the admission, and keeps the old signing
   key for the grace period. It audits the request as `agent.key.rotate`, also a
   refusal.
4. The command moves the new keys in place: the encryption key first and the
   public key last. A running agent reads the keys again at each heartbeat and
   before it opens a sealed job. It takes a set only when the private key is the
   pair of the public key, so it does not take a set that is halfway through the
   moves. It keeps the old encryption key, to open a job that the controller
   sealed before the rotation.

A refusal removes the new keys, and the agent keeps its keys. When no reply
arrives, the new keys stay, and a second run sends the same keys. The controller
answers a request for keys that the admission already holds as a success, with
the new key's signature as the proof. Thus a rotation whose reply was lost
completes. A replay of an old request cannot move the admission back, because
the old key no longer matches the admission. A revoked machine has no admission,
so it cannot rotate.

The rotation runs in the command, not in the agent process. Thus it works when
the agent is stopped too. The command connects to NATS with the agent's own
user: the one that its join saved, or the one in its config.

### The rotation of the controller's key

The controller's key signs each job. It rotates with no restart and no new
admission of the agents. The state bucket holds a record of the rotation at
`pki.controller`, and each agent reads it at each heartbeat:

1. `osapi client pki key rotate`, or `osapi pki key rotate --name controller` on
   the controller's host, makes the next key as `controller.next.key` and
   `controller.next.pub`. It writes a record with the current key and the next
   key, which the current key signs.
2. An agent takes a record only when a controller key that it has signed it.
   With the next key in the record, the agent keeps it as
   `enrolled-controller.next.pub`, and accepts a job that it signs. The agent's
   signed registration reports the next key, as `controller_key_next`.
3. The controller switches when each admitted agent that reported within the
   grace period has the next key, or when the period ends. It moves the next key
   in place, signs with it, and writes a record that the new key signs, with the
   old key as the previous key. The record also keeps each key that an earlier
   switch replaced, as a retired key. The controller verifies a job that it
   stored with its current key, its previous key or a retired key. Thus a job
   from before each rotation still shows in `job list` and `job get`. A retired
   key verifies no message from an agent. A job that no key verifies is listed
   with its status and the reason, so it can be deleted.
4. Each agent takes that record with its next key, makes the new key its
   controller key, and keeps the old key as the previous key. The previous key
   verifies the jobs that the old key signed before the switch.

`osapi client pki key get` shows the next key and each agent that the switch
waits for. An agent that is away for the whole grace period does not trust the
record of the switch, and needs a new admission.

The record goes in the state bucket, which each agent already reads, so the
rotation needs no new NATS subject or permission. An agent can also write that
bucket. Thus the controller takes a record only when its own key signed it. An
agent cannot start a rotation or cause a switch, but it can remove the record.
Only the controller that has the key files rotates the key.

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
an agent that has no stored key, or no P-256 key, makes it enroll again.

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

Written from `internal/agent/`, `internal/pki/`, `internal/job/registration.go`
and `internal/job/client/agent.go`.
