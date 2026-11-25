# Agent join

An agent host joins osapi with two values: the URL of the controller and a join
token. The agent gets the rest of its config from the controller over HTTPS.
Today each agent host needs a full `osapi.yaml` with the NATS address and the
NATS credentials, and configuration management must write it. The agent also
enrolls over NATS, so it needs the NATS settings before it can enroll.

This page is the design of osapi-io/osapi#1313. Nothing on it is built yet.

## What stays on the host

The first contact needs these values only:

| Value               | Why it stays                                            |
| ------------------- | ------------------------------------------------------- |
| the controller URL  | The agent must find the controller before anything.     |
| the join token      | It admits the agent. The agent deletes it after a join. |
| `agent.pki.key_dir` | The agent makes its keys there before it sends them.    |

A join string, `osapi://<host>:<port>?token=<token>&fp=<fingerprint>`, carries
the three facts that the first contact needs: the URL, the token and the
fingerprint of the controller's certificate.

## Join tokens

An operator makes a join token on the controller:

```bash
osapi controller join-token create --expires 1h [--uses 1] [--labels k=v]
osapi controller join-token list
osapi controller join-token revoke --id <id>
```

A token has an expiry, a number of uses, and labels that each agent that uses it
gets. The controller stores a hash of the token, not the token. The token
carries the controller URL and the fingerprint of the controller's TLS
certificate. Thus the agent checks the controller before it sends anything, and
a host in the path cannot answer for the controller.

## The join

The agent does these steps one time, at its first start:

1. The agent makes its signing key and its encryption key in
   `agent.pki.key_dir`, as it does for an enrollment today
   ([Agent identity](agent-identity.md)).
2. The agent connects to the controller over HTTPS. It refuses a certificate
   whose fingerprint is not the fingerprint of the token.
3. The agent sends `POST /api/agent/join` with the token, its hostname, its
   machine ID and its two public keys. The request is signed with its signing
   key.
4. The controller checks the token: not expired, uses left, not revoked. A valid
   token **admits the machine at once**. The operator made the token, so the
   token is the decision that `admit` records today ([Admission](admission.md)).
   The admission record names the token.
5. The controller answers with the agent's config and its NATS credentials.
6. The agent stores its credentials in `agent.pki.key_dir`, deletes the token,
   and connects to NATS.

An invalid token answers 403 and admits nothing. The machine can still enroll
over NATS as today, and wait for an operator.

## The config of the agent

The controller holds each agent's config. `GET /api/agent/config` answers it,
signed by the controller, to an agent that signs the request with its key. It
has:

- the NATS URLs, and the agent's own NATS credentials
- the labels, the queue group and the maximum number of jobs
- the facts: the collectors and the interval
- the metrics settings and the log level

The config has a version, one more at each change. The agent sends the version
that it runs in each heartbeat. When the controller has a newer version, the
agent gets it. The labels, the facts, the log level and the maximum number of
jobs apply at once. A change of the NATS URL or of the credentials makes the
agent connect again. Nothing needs a restart.

`osapi client agent get` and the UI show the version that the agent runs, when
it got it, and `behind` when the agent does not have the newest version.

## NATS credentials for each agent

Each agent gets its own NATS credentials, so a revoked agent is cut off from
NATS at once, not at its next start. The NATS server must let the controller
make and remove credentials while it runs. A static list of users or nkeys needs
a reload of the server for each agent.

**Decision needed:** the embedded NATS server supports operator mode
(`nats.server.auth.type` with `resolver_file`). In operator mode the controller
holds an account signing key, signs a user JWT for each agent, and adds a
revoked agent to the account's revocation list. The other way is a static list
that the controller writes and the server reloads. Operator mode is the
recommendation: it needs no reload, and a revocation takes effect at once.

## Revocation

An operator removes or rejects an agent as today. The next config request of the
agent answers 403. Its NATS credentials are revoked, so it is cut off from NATS
at once. An agent authenticates with its key, not with a user token. Thus no new
role is necessary.

## What this page does not cover

- The controller makes its own secrets at its first start (after #1308).
- Zero-touch joins: a build with the controller URL in it, DNS SRV discovery,
  and an install from the controller over SSH.
- Signed extension binaries (#1064).
