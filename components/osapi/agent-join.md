# Agent join

An agent host joins osapi with one value: a join string. The agent needs to
reach NATS, and nothing else. The controller admits it, and gives it the rest of
its config and its NATS credentials over NATS. Thus a host can come up from an
image or a cloud-init file with no configuration management.

This page is the design of osapi-io/osapi#1313. The parts that are built:

- the join tokens (osapi-io/osapi#1377)

- the join over HTTPS (osapi-io/osapi#1378): an agent with `agent.join` set
  joins at its first start, and is admitted at once

- the NATS permissions of each role (osapi-io/osapi#1415): the controller, an
  agent and setup. `osapi nats permissions get --role <role>` prints them, and
  the embedded server applies them to a user with a `role`

- the join over NATS with static users (osapi-io/osapi#1416): osapi's embedded
  server, or a server with a join user and an agent user. The join user has the
  role `join`, which can send the join request and nothing else

- the join over NATS in operator mode (osapi-io/osapi#1416): with an account
  signing key, the controller mints a bootstrap JWT for each token and a JWT for
  each agent's own user key. The keys are scoped (osapi-io/osapi#1432): the
  template of the agent's key and of the join's key is the permissions of the
  role, and the JWTs that they sign carry no permissions or limits. Thus the
  controller cannot give more than an agent or a join user has

- `osapi nats auth password create` and `operator create` (osapi-io/osapi#1420):
  a credential for each role, made by osapi. `operator update`
  (osapi-io/osapi#1531) signs the account and each role's credentials again with
  the same keys, for an upgrade that adds a subject to a role: the account's JWT
  holds the agents' permissions as the template of their signing key, and each
  credentials file holds the permissions of its role

- the labels of a join token: the agent takes them, and its own `agent.labels`
  win

- JWTs that expire and renew (osapi-io/osapi#1380): with
  `controller.join.agent_ttl`, an agent renews its JWT over NATS
  (`<ns>.join.renew`) when a third of its life is left, with a request that its
  admitted key signs. The controller renews only an admitted machine, so a
  revoked agent is cut from NATS when its JWT expires

- the rotation of an agent's keys (osapi-io/osapi#1531):
  `osapi pki key rotate --name agent` sends the new public keys over NATS
  (`<ns>.join.rotate`), signed with the admitted key and the new key, and the
  controller moves the admission to them with no new admission.
  [Agent identity](agent-identity.md#the-rotation-of-an-agents-keys) has the
  steps

- the join with a NATS server's auth callout (osapi-io/osapi#1416): the server
  sends each connection to the controller. A join token that admits now gets the
  join role for ten minutes at most; the NATS user key that an agent sent at its
  join gets the agent role while the machine is admitted, when the connection
  signs the server's nonce with it; the controller refuses the rest, and each
  decision is a `nats.connect` audit entry. The server must have an nkey user,
  such as the callout user, or it offers no nonce

The parts that are not built: the config in KV (osapi-io/osapi#1379), and the
account's revocation list for an instant cut on osapi's embedded server
(osapi-io/osapi#1380).

## Why NATS is the transport

An agent must reach NATS to take a job. Often NATS is the only thing that it can
reach: a NATS leaf node in its site, an edge cluster, or a NATS port that a
firewall lets through when it blocks each other port. An agent that must also
reach the controller's API needs a second route, and that breaks a zero-touch
join at such a site. Thus the rule is: an agent needs to reach NATS, and nothing
else. The owner decided this on 25 Nov 2026.

To give an agent its NATS config over NATS is not circular. The join string
carries the minimum that a first contact needs, as the HTTPS join string carries
the API's URL.

The join over HTTPS stays, for a site where the API is the route that the agent
has. The two transports send the same signed request and get the same answer.

## The join string

| Transport | Join string                                                                             |
| --------- | --------------------------------------------------------------------------------------- |
| NATS      | `tls://<host>:<port>?token=<token>&fp=SHA256:<hex>&user=<user>&pass=<password>&ns=<ns>` |
| HTTPS     | `osapi://<host>:<port>?token=<token>&fp=SHA256:<hex>`                                   |

- `token` is the join token. It admits the agent.
- `fp` is the fingerprint of the server's certificate: the NATS server's, or the
  API's. The agent refuses a server whose certificate does not match it. Thus a
  host in the path cannot answer for the server. A `nats://` string, with no
  TLS, has no `fp`.
- `creds` is, in operator mode, the bootstrap user's credentials: a JWT with the
  join role that expires with the token, and its seed.
- `user` and `pass` are the bootstrap user, where the NATS setup has static
  users ([What each NATS setup needs](#what-each-nats-setup-needs)). The user
  can send the join request and nothing else, so the string gives no access to
  osapi's data.
- `ns` is the namespace of osapi's subjects.

`join token create` makes the NATS string by default, and the HTTPS string with
`--transport https`. For a `tls://` server, it reads the fingerprint when it
connects as the bootstrap user, so a string that it prints has a user that
connects.

The agent also needs `agent.pki.key_dir`, where it makes its keys before it
sends them. The default, `/etc/osapi/pki`, needs no setting.

## Join tokens

An operator makes a join token on the controller:

```bash
osapi controller join token create --expires 1h [--uses 1] [--labels k=v]
osapi controller join token list
osapi controller join token revoke --id <id>
```

A token has an expiry, a number of uses, and labels that each agent that uses it
gets. The controller stores a hash of the token, not the token. In operator
mode, `create` also makes a bootstrap JWT that expires with its token, signed
with `controller.join.signing_key_file`. The admission record keeps the token's
labels, and the join reply gives them to the agent.

## The join over NATS

The agent does these steps one time, at its first start:

1. The agent makes its signing key and its encryption key in `agent.pki.key_dir`
   ([Agent identity](agent-identity.md)).
2. The agent connects to NATS with the bootstrap credential. It refuses a server
   whose certificate does not match `fp`.
3. The agent sends the join request as a NATS request: the token, its hostname,
   its machine ID and its two public keys, signed with its signing key. The
   bootstrap credential can send this request and get its reply, and nothing
   else.
4. The controller checks the signature, then the token: not expired, uses left,
   not revoked. A valid token **admits the machine at once**, and the admission
   record names the token ([Admission](admission.md)).
5. The controller replies with the controller's public key, the agent's NATS
   user and the labels of the token. In operator mode, the user is a JWT for the
   user key that the agent sent in the request; its seed never leaves the host.
   The controllers answer in a queue group, so one controller answers each join
   and takes one use of the token.
6. The agent saves the key as `enrolled-controller.pub`, and the user and the
   server's certificate in `nats-join.json` (mode 0600), in `agent.pki.key_dir`.
   It connects again with its own user. Each later start reads `nats-join.json`
   and does not join again.

A token that does not admit gets a reply that says why, and admits nothing. The
agent stops with the reason.

A reply can be lost after the controller admitted the machine. The agent then
asks again, and the controller answers again with no second use of the token:
the machine is admitted, by that token, with the keys that the request has. The
signature shows that the request holds those keys.

Each join writes an audit entry: the actor is `join-token:<id>`, the operation
is `agent.join`, the response code is 200 or 403, and the summary is the machine
ID and the hostname. The agent's join has an `agent.join` span, and the
controller's has `admission.join`. None of them holds the token or a password.

The controller checks the signature before it takes a use of the token. Thus a
request that does not hold its key spends nothing. The signature covers each
field with the domain prefix `osapi-join-v1`, so that it is not a signature of
anything else.

## A rotation of the NATS server's certificate

It is built (osapi-io/osapi#1533). Each joined agent pins the NATS server's
self-signed certificate, so a new certificate must reach each agent before the
server serves it. The rotation has an overlap, as the rotation of the
controller's key has:

1. `osapi client pki nats rotate`, or `osapi pki cert rotate --name nats` on the
   controller's host, makes the next certificate, `nats.next.crt`, beside
   `nats.crt`. The controller writes a record to the state bucket, at
   `pki.cert.nats`, with both certificates. The controller's key signs it, with
   the domain prefix `osapi-cert-v1`.
2. At its next heartbeat, each agent reads the record. When a controller key
   that the agent trusts signed it, the agent writes both certificates to the CA
   file of its join, and its signed registration reports the next one as
   `nats_cert_next`. An agent on the NATS server's host that trusts `nats.crt`
   itself only reports it.
3. When each admitted agent that reported within
   `controller.pki.rotation_grace_period` trusts the next certificate, or when
   the grace period ends, the controller renames the next files into place: the
   key first, then the certificate.
4. NATS serves the new certificate at its next handshake, with no restart. The
   connections of the agents stay up. The controller writes the record of the
   switch, with the new certificate alone, and each agent keeps only that one in
   its CA file.

Two changes make the switch work with no restart:

- Each server of osapi reads its certificate files again when they change, at
  its next handshake. This is also true for a `cert_file` of the operator.
- A NATS client with a `ca_file` reads the file again at each handshake. Thus an
  agent that connects again after the switch trusts the certificate that its
  file got after it first connected.

The new certificate is in the join strings that are made after the switch,
because `controller join token create` reads the certificate that the server
serves. An agent that was away for the whole overlap gets the new certificate
from the record if it still has a connection. If it does not, it joins again.
The rotation refuses a certificate of the operator's `cert_file`.

A rotation of the API's certificate has no overlap. The controller serves the
new certificate at its next handshake. An agent does not use the API after it
joins, so a join string made before the rotation is the only thing that stops
working.

## The join over HTTPS

It is built (osapi-io/osapi#1378). The agent sends the same signed request to
`POST /api/agent/join`, which is public, because the join token authorizes it.
The route has no CLI command: the agent calls it, not a person (`.NoCommand()`
in the [endpoint DSL](endpoints.md)). The spec marks it `x-osapi-program`, so
the SDK has the method and needs no example of it, which would spend a token.

The agent pins the API's certificate: it skips the check of the roots and
compares the SHA-256 of the leaf certificate with `fp`, so a self-signed
certificate works. A certificate that renews, such as a Let's Encrypt
certificate every 90 days, makes the join strings made before it not match. A
join token is short-lived, so this is a small cost.

## The config of the agent

The controller holds each agent's config in the state bucket, at
`config.<machine-id>` (`job.AgentConfig`). It has:

- the labels
- the maximum number of jobs
- the log level
- the interval of the facts

The agent watches its key. A change reaches it at once, with no poll and no
HTTP, and applies at once. Nothing needs a restart. The config has a version,
one more at each change. `osapi client agent get` and the UI show the version
that the agent runs, and `behind` when the agent does not have the newest one.

The config has no NATS settings. The join gives the agent its NATS server, its
TLS and its user, and the renewal gives it new credentials. The agent reads its
config over that NATS connection. Thus a config that changed the NATS server
would have to come over the connection that it replaces. If the new settings did
not operate, the agent would lose the controller and could not get a correction.
osapi-io/osapi#1524 decided this: the NATS server and its TLS change only
through a new join.

## A move to a different NATS server

The agent keeps the NATS server and the TLS of its join in `nats-join.json`, and
reads them at each start. To move an agent to a different NATS server or
address, it joins again:

1. Set `controller.join.url` to the new address of NATS. Make a join token with
   a use for each host and the labels of the hosts:
   `osapi controller join token create --uses <n> --labels <k=v>`.
2. On each host, stop the agent.
3. Remove `nats-join.json` from `agent.pki.key_dir`. Do not remove `agent.key`,
   `agent.ekey` or `enrolled-controller.pub`.
4. Set `agent.join` to the new join string, and start the agent.

The agent finds no `nats-join.json`, so it joins with the new string and the
keys that it has. The controller admits the machine again with those keys, and
the token gives its labels. The agent writes its NATS user and the certificate
of the new server again.

A new certificate on the same address does not need a join. The
[rotation](#a-rotation-of-the-nats-servers-certificate) gives it to each agent.

## What each NATS setup needs

The NATS server does not decide the role of an agent. What the agent connects
with carries its permissions. What osapi can give an agent depends on what the
NATS administrator, the person who runs the NATS infrastructure, gives osapi:

osapi's embedded server runs in operator mode by default (osapi-io/osapi#1413).
With no `resolver_file` it makes the operator, the account, a credential for
each role and the two scoped signing keys at its first start, in `nats-auth` of
`nats.server.key_dir`, and a controller or an agent on the same host uses them
with no setting.

| NATS server                               | The administrator provisions for osapi                                                                       | Bootstrap credential                | Agent credential                           | One agent cut from the bus             |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------------------------------ | -------------------------------------- |
| osapi's embedded server, in operator mode | nothing                                                                                                      | a JWT for each token                | a short-lived JWT for each agent           | at once: the account's revocation list |
| another server, in operator mode          | an account for osapi, and two scoped signing keys whose templates are the agent's and the join's permissions | a JWT for each token                | a short-lived JWT for each agent           | when its JWT expires                   |
| another server, with auth callout         | an `auth_callout` block that names osapi's issuer key (NATS 2.10 or later), and an nkey callout user         | the callout decides, per connection | the callout decides, per agent             | at its next connection: `agent_ttl`    |
| another server, with static users         | two users: a join user that can send only the join request, and an agent user, the same for each agent       | the join user, in the join string   | the agent user, which the controller gives | no: osapi refuses what the agent signs |
| no authentication, for development        | nothing                                                                                                      | none                                | none                                       | no                                     |

In operator mode, the role is in the user JWT. The controller signs a bootstrap
JWT that can send only the join request, and after the join an agent JWT with
the agent's subjects. The change of role is a new connection with the second
JWT. The server checks only the signature, and applies the permissions that the
JWT has. A scoped signing key keeps the operator's key with the administrator:
its template sets the most that osapi can give, and osapi cannot give more.

With static users, osapi cannot make a user. The administrator makes the two
users, and gives them to the controller's config. The join string carries the
join user. The join reply carries the agent user.

The permissions of each role come from `bus.RolePermissions` in osapi, built
from the names of the streams and buckets of the config. An agent cannot make or
change a stream or a bucket, and cannot write the secrets, the enrollment
records or the object store. A scoped signing key's template and the static
agent user take the agent's set. The join's bootstrap set is part of
osapi-io/osapi#1416.

In each setup, the NATS credential is not the identity of the agent. The
controller verifies each answer and each registration with the key that it
admitted ([Agent identity](agent-identity.md)). Thus a revoked agent gets no job
and cannot answer for a host in each setup. The table's last column is only the
cut from the bus.

A host that has the join string can send the join request. Without a valid token
and the agent's signature, the controller admits nothing.

## Hosts that come and go

A NATS administrator never makes a NATS user for each host. Agents share the
agent user, or the controller makes a JWT for each one. Thus a fleet that scales
up and down needs nothing from the administrator at each host.

- **One join token for each group of hosts.** A token with enough uses, an
  expiry that outlives the image, and the labels of the group, such as
  `role=web`. Each host that joins with it gets the labels. Rotate the token in
  the image or the launch template.
- **A machine ID for each host.** An agent's identity is `/etc/machine-id` on
  Linux. An image that ships a filled-in machine ID gives each clone the same
  identity, and the second clone replaces the first in admission. Ship the image
  with an empty `/etc/machine-id`, so that systemd makes one at the first boot.
- **Labels, not hostnames.** A host whose hostname is random is targeted by its
  labels: `--target role:web`.
- **`controller.pki.delete_after`.** It deletes an admitted machine that has not
  reported for that time, such as `24h`. Thus a host that went away leaves no
  record. Empty, the default, keeps each one.

## Revocation

An operator revokes an agent with the command of today:
`osapi client admission revoke --machine-id <id>`, or `reject` or `delete`
([Admission](admission.md)). No new command is necessary. The controller refuses
each answer and each registration that the agent signs, and writes no new config
for it. The cut from the bus is the last column of
[What each NATS setup needs](#what-each-nats-setup-needs). With static users, to
cut the agent from the bus, the administrator changes the agent user; the
controller gives the new one to the other agents in their config, and then the
administrator removes the old one.

A revocation that the administrator makes with their own tools, such as
`nsc revocations add-user`, needs nothing from osapi. The agent cannot connect,
logs the error of the server, tries again with a backoff, and shows as an agent
that stopped reporting ([Admission](admission.md#machines-that-stop-reporting)).

## The lab joins in the same way

The lab's images bake a join string, not the NATS settings and credentials of an
agent. The hub makes a token for the lab when it bakes the images, with enough
uses and an expiry that outlives them. Thus each VM joins as a host in
production does, and a break in the join breaks the lab first.

## What this page does not cover

- The controller makes its own secrets at its first start (after #1308).
- How the join string gets to a host: a value in an image, cloud-init, DNS SRV
  discovery, or an install over SSH.
- Signed extension binaries (#1064).
