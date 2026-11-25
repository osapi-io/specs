# Agent join

An agent host joins osapi with two values: the URL of the controller and a join
token. The agent gets the rest of its config from the controller over HTTPS.
Today each agent host needs a full `osapi.yaml` with the NATS address and the
NATS credentials, and configuration management must write it. The agent also
enrolls over NATS, so it needs the NATS settings before it can enroll.

This page is the design of osapi-io/osapi#1313. The join tokens
(osapi-io/osapi#1377) and the join (osapi-io/osapi#1378) are built: an agent
with `agent.join` set joins at its first start, and is admitted at once. Until
osapi-io/osapi#1379, the agent still has its NATS settings in its own config,
and the controller answers the join with its public key only. The config and the
NATS credentials of [The config of the agent](#the-config-of-the-agent) and
[NATS credentials](#nats-credentials) are not built yet.

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
osapi controller join token create --expires 1h [--uses 1] [--labels k=v]
osapi controller join token list
osapi controller join token revoke --id <id>
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

An invalid token answers 403 and admits nothing. The agent logs the reason, and
enrolls over NATS as today, to wait for an operator.

The join is `POST /api/agent/join`, in the agent group. It is public, because
the join token authorizes it, and it has no CLI command: the agent calls it, not
a person (`.NoCommand()` in the [endpoint DSL](endpoints.md)). The spec marks it
`x-osapi-program`, so the SDK has the method and needs no example of it, which
would spend a token. The agent signs the request over each field with a domain
prefix, `osapi-join-v1`, so that the signature is not a signature of anything
else. The controller checks the signature before it takes a use of the token.
Thus a request that does not hold its key spends nothing.

The agent pins the controller's certificate: it skips the check of the roots and
compares the SHA-256 of the leaf certificate with the fingerprint of the join
string, so a self-signed certificate works. A certificate that renews, such as a
Let's Encrypt certificate every 90 days, makes the join strings made before it
not match. A join token is short-lived, so this is a small cost.

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

## NATS credentials

The join, the token, HTTPS and the config do not depend on how NATS
authenticates. Only the NATS credentials that the config carries change with the
auth type of the server:

| NATS server                                                                                          | The agent gets                                                                  | A revoked agent                                                          |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| osapi's embedded server, in operator mode                                                            | its own user JWT, which the controller signs, valid for a short time            | loses its NATS connection at once                                        |
| a server that osapi does not run, in operator mode, with a signing key for osapi                     | its own user JWT, valid for a short time                                        | loses its connection when its JWT expires, which is at most one lifetime |
| a server in operator mode with no key for osapi, or with nkeys, users and passwords, or a creds file | the agent credentials that the controller's config has, the same for each agent | keeps its connection until an operator changes those credentials         |
| none, in a lab                                                                                       | no credentials                                                                  | the same as the row above                                                |

In operator mode (`nats.server.auth.type` with `resolver_file`, which the
embedded server supports), the controller holds a signing key of the account of
the agents. At a join, and at each config fetch, it signs a user JWT for the
agent with the subjects that an agent can use, valid for a short time, such as
one hour. Thus a revoked agent, whose config fetch answers 403, gets no new JWT.
When osapi runs the server, the controller also adds the agent's public key to
the revocation list of the account, and the server closes the connection at
once. No reload is necessary.

A server that another team runs gives osapi a scoped signing key of one account,
not the key of the operator. With that key osapi signs the JWTs of the agents,
but it cannot change the revocation list of the account. The short lifetime cuts
the agent off. A team that gives osapi no key gives it the agent credentials of
the shared row instead. The owner chose operator mode as the recommended setup
on 25 Nov 2026, over a static list that the server reloads for each agent.

In each mode, the NATS credentials are not the identity of the agent. The
controller verifies each answer and each registration with the key that it
admitted ([Agent identity](agent-identity.md)). Thus a revoked agent gets no job
and cannot answer for a host in each mode. Operator mode adds only the immediate
cut from the bus.

## Revocation

An operator revokes an agent with the command of today, for each NATS server:
`osapi client admission revoke --machine-id <id>`, or `reject` or `delete`
([Admission](admission.md)). No new command is necessary. An agent authenticates
with its key, not with a user token, so no new role is necessary either.

The next config request of the agent answers 403, and the controller refuses
each answer and each registration that the agent signs. Thus in each mode the
agent gets no job and cannot answer for a host. The cut from the bus depends on
the server:

| NATS server                                  | What osapi does                                            | What the owner of the server does                                                                                                                                                                        |
| -------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| osapi's embedded server                      | adds the agent's key to the revocation list of the account | nothing                                                                                                                                                                                                  |
| another server, with a signing key for osapi | signs no new JWT, so the agent's JWT expires               | nothing, or revokes the agent's key with its own tools, such as `nsc revocations add-user`, for an immediate cut                                                                                         |
| another server, with shared credentials      | gives no new config to the agent                           | to cut it from the bus: an operator changes the credentials in the controller's config, the other agents get them at their next config version, and then the old credentials are removed from the server |

A revocation that the owner of a server makes with its own tools needs nothing
from osapi. The agent cannot connect, logs the error of the server, tries again
with a backoff, and shows as an agent that stopped reporting
([Admission](admission.md#machines-that-stop-reporting)).

## What this page does not cover

- The controller makes its own secrets at its first start (after #1308).
- Zero-touch joins: a build with the controller URL in it, DNS SRV discovery,
  and an install from the controller over SSH.
- Signed extension binaries (#1064).
