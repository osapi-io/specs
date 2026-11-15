# Agent identity

The controller must know two things. An answer came from the machine that it
addressed. A machine that claims a hostname is the machine that enrolled with
that hostname. The two facts come from one stored public key for each agent.

## Enrollment is the only thing that writes a key

osapi keeps the public key of an accepted agent after the enrollment handshake.
It keeps the key for the **machine ID** of the agent, not for its hostname. It
records the fingerprint at the time of acceptance.

**Only the acceptance of an enrollment can make or replace that key.** A message
with a different key cannot do it. A new registration cannot do it. A restart
cannot do it. Thus an attacker who can publish to the bus cannot change a key by
a publish. The trust anchor stays where an operator put it.

The agent obeys the same rule for its own key. It makes a keypair only when
neither file exists. A key file that it cannot read stops the agent with an
error. Examples are a file that root still owns after the user of the agent
changed, or one half of a pair. A replacement key gives no signal. The new key
is not the accepted key. Thus the host stops getting jobs, and nothing at the
agent tells why.

Only two events destroy a key:

- an operator rejects a pending enrollment
- an operator removes an enrolled agent

The two take effect immediately. There is no time when the signature of a
removed agent still verifies.

The removal is `DELETE /api/agent/{hostname}`, or `osapi client agent remove`.
It deletes the accepted record and removes the cached key. A hostname is not an
identity. Thus when two accepted agents have the same hostname, the call answers
409 with the two machine IDs, and `machine_id` selects one. The call does not
guess.

osapi does not tell the removed agent. The agent keeps the key of the controller
from its acceptance. Thus it thinks that it is enrolled, and does not ask again.
To enroll it again, do a step on the host: delete `controller.pub` and restart
the agent.

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

## Enabling it on a live fleet

You can switch enforcement on each side separately: `ControllerPKI.Enabled` for
the controller, `AgentPKI.Enabled` for the agent. **When PKI is off, osapi
operates exactly as it did before the key store existed.**

`GET /agent` reports `key_stored` and `verified` for each agent. Thus you can
enable PKI in stages:

1. Turn on one side.
2. See which agents osapi will refuse.
3. Enroll them again.
4. Complete the change at a time that you select, not at the time that you
   changed a flag.

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

Written from `internal/agent/` and `internal/job/registration.go`.
