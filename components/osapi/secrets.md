# Secrets

A plan, built in part. This page records where the secrets of osapi live, how
the three DSLs take one, how a value gets to the agent that uses it, and how a
secret rotates. Each part moves into the page of its subject when it is built,
and this page goes when the last part is built.
[osapi #1065](https://github.com/osapi-io/osapi/issues/1065) has the decision.

## What osapi has today

Each kind of secret has its own solution, and none of them is a store:

- The JWT signing keys and the NATS passwords are values in `osapi.yaml` or in
  an environment variable. [Configuration](configuration.md) masks them before
  the controller logs its config.

- The PKI keys are files in `key_dir`. [Agent identity](agent-identity.md) has
  their rotation.

- A behavior input of type `secret.Value` stays out of the audit log, the spans
  and the chain records. [Secrets](dsls.md#secrets) has the type.

- The route of each method resolves a reference from its vault, after the limits
  of use. [Vaults](vaults.md#how-a-route-resolves-a-reference) has it.

- The job client seals each secret of a job to its target agents, and the
  dispatch of the agent opens it.
  [Job system](job-system.md#a-secret-in-the-definition-is-sealed) has it. PKI
  is always on (osapi-io/osapi#1307), so no secret goes in a job as plain text.

## Who the design protects against

The built-in store protects against two attackers:

- **A person who reads the disk or a backup** of the NATS server.
- **A NATS user who is not the controller**, such as an agent or a different
  client with access to the bus.

It does not protect against the controller. The controller can read each secret
in the built-in store, because it resolves references. An operator who needs a
store that the controller cannot read uses a backend that keeps the secret in
its own system, such as Vault, and gives the controller access to only the keys
that it needs.

**To use a secret is to read it.** A caller that can put a secret into a file or
an environment on a host can read it there. Thus the use of a reference has its
own permission and its own limits. [Who may use a secret](#who-may-use-a-secret)
has them.

## One reference syntax

A secret is a reference in each location that takes one:

```
secret://<vault>/<key>
```

`secret://default/registry-token` is the key `registry-token` in the vault
`default`. A config value, a behavior input, an endpoint input, a command flag
and a step of a plan all take the same form.

A reference is not a `@fact.` reference. The agent resolves `@fact.` from its
own facts (`internal/agent/factref.go`). The controller resolves `secret://`,
because the agent has no vault and no credentials for one. Thus an agent never
sees a reference, and the controller never sends a value that it did not seal.

The API never returns the value of a secret. It returns names, and the metadata
of a key.

## A secret in the DSLs

Built in osapi-io/osapi#1240. A secret is the type `secret.Value`, not a tag.
[The parts that each DSL shares](dsls.md#secrets) has what each part of the
three DSLs does with it, and the limit until the controller seals a value.
[Behaviors](behaviors.md#secret-inputs) has the rule `secret` of the behavior
DSL.

A command of the command DSL calls no API. Thus it resolves a reference itself,
from the vaults of its config. Built for a value of the config:
`osapi controller token generate` resolves the signing keys
([Configuration](configuration.md#a-secret-can-be-a-reference-to-a-vault)). Not
built: a reference in a `secret.Value` flag of a command.

## The order on the controller

The route of a behavior method does these steps, in this order:

1. Validate the input. A secret field passes as a reference or a value.
2. Resolve each reference, after the limits of use. Built in
   osapi-io/osapi#1244: [Vaults](vaults.md#how-a-route-resolves-a-reference) has
   the steps. The limits come before the read, so a caller that may not use a
   secret does not learn if its key exists. Each value then passes the
   `validate` tags of its field.
3. Run the `.Before` step, if the method has one. A step can change a secret to
   a value made from it, such as a password to its hash. A secret that the step
   clears is not sent.
4. Seal each secret that is still set, for the target agents, and queue the job.
   Built in osapi-io/osapi#1247:
   [Job system](job-system.md#a-secret-in-the-definition-is-sealed) has it. A
   value that a `.Before` step leaves set is sealed, not refused.

An endpoint method runs on the controller, so it does steps 1 and 2, and gives
the value to its handler. It queues nothing, so it seals nothing.

## How a value gets to the agent

Built in osapi-io/osapi#1247.
[Job system](job-system.md#a-secret-in-the-definition-is-sealed) has the job
key, the seal to each agent, and the open in the dispatch. The data has a sealed
value as the string `sealed:<base64>`, not as an object, so a `secret.Value`
field reads it with no new code. The operation has `sealed_from`, the public key
of a new X25519 key for the job, because the controller has no X25519 key of its
own.

## Secrets in a chain

A vault is not a behavior. A behavior runs on a host, as a job. A vault as a
behavior gives each agent credentials for the vault, and the agent then reads
each secret that the vault has. The design gives an agent only the values of its
job, so the vault stays on the controller.

The rest is built in osapi-io/osapi#1240:
[Secrets in a chain](behaviors.md#secrets-in-a-chain) has how a value moves from
a parent to a child, and the check of its type. Not built: the controller
resolves and seals the value one time, for the top method, and the agent opens
it one time, for each method of the chain.

## What the agent knows

The agent knows nothing about vaults or references. It knows three things:

- **Its X25519 key.** Built.
  [Agent identity](agent-identity.md#the-encryption-key) has it. A rotation of
  the agent's key seals nothing again, because the controller seals at dispatch,
  not at storage.
- **Which fields are secrets.** The dispatch of a behavior is generated from the
  same Go types. Thus the agent opens a `secret.Value` field, and the provider
  gets a value of the type that it declared. A provider has no code for sealed
  values.
- **The value, for the time of one job.** The agent does not write it to a log,
  to its state, or to the result. The type redacts it in each of them.

The agent never resolves a reference, also in its own config. The NATS
credentials of the agent stay in its config file or its environment.

## Who may use a secret

Built in osapi-io/osapi#1244, with `secret:use` from osapi-io/osapi#1243. Three
limits apply to each reference in a request. All three must pass:

- **The permission `secret:use`.** `admin` and `automation` have it. A secret
  goes into a write that changes the configuration of a host, and `automation`
  is the role that writes. `operator` runs actions, such as a restart, and no
  action takes a secret. `read`, `auditor` and `observer` do not have it.
- **The target scope of the token.** It limits the hosts, as for each other
  request ([Permissions](permissions.md#a-tokens-target-scope)).
- **The targets of the vault.** A vault can name the targets that its secrets go
  to, such as `group:prod`. The route refuses a reference to that vault when the
  host of the request is outside them, and when the request names no host. A
  vault with no targets goes to each host.

The audit entry of the request records each reference that it used, because the
audit keeps a reference in the body. Thus `osapi client audit list` shows who
used a secret, when, and on which hosts.

## The secret endpoint group

Built in osapi-io/osapi#1243.
[The secret endpoint group](vaults.md#the-secret-endpoint-group) has its
methods, its commands, its permissions and the roles that get them, and the
Secrets page of the UI. No method gives a value.

## A vault is a backend that you can replace

Built. [Vaults](vaults.md) has the `Vault` interface, the registry of types, the
`controller.secrets.vaults` config with `targets`, the default vault `default`
whose key the controller makes at its first start, the `nats` type in the
`osapi-secrets` bucket, and `osapi controller vault key create` and `rotate`.

swamp has the same design. Its backend interface is `get`, `put`, `list` and
`getName`, each vault has a name and a type, and only its local backend is built
in. AWS, Azure and 1Password are extensions. `swamp vault migrate` copies the
keys to a new type and keeps the name.

## Encryption at rest

JetStream encryption at rest is built
([osapi #1242](https://github.com/osapi-io/osapi/issues/1242)).
`nats.server.jetstream.key_file` turns it on, and `osapi nats key create` makes
its key. That key protects each stream and bucket on the disk, not only the
secrets. It does not protect against a NATS user, which is why the vault
encrypts each value too.
[The message bus](transport.md#the-streams-are-encrypted-on-the-disk) has it.

## References in the config

Built in osapi-io/osapi#1245.
[Configuration](configuration.md#a-secret-can-be-a-reference-to-a-vault) has
which fields take a reference, which process resolves each one, and the values
that cannot be a reference: a NATS password and the vault key.

## What an AI agent learns

Built in osapi-io/osapi#1248. A coding agent learns about a secret from the same
generated parts as a person. `method get` and the docs page of a method mark
each secret field and its two forms. `osapi client secret list` gives the names
to reference. Rule 5 of the skill in the binary tells it to put a value in with
`osapi client secret update` from standard input, then use its reference
([Agent skills](agent-skills.md#what-the-skill-tells-an-agent)). The Plans page
of the UI has a picker of the references ([The UI](ui.md#plans)).

## Rotation

- **A secret.** `update` writes a new version. A job that the controller queues
  after the change gets the new value. A host that has the old value, in a file
  or a container, keeps it until a job runs on it again. `secret get` shows when
  the key changed, and the audit log shows which hosts used it.
- **The JWT signing key.** Built. The controller accepts tokens from more than
  one key, each with its own `kid`, and signs with the first. Thus a new key
  goes in first, and the old one goes after the last token that it signed
  expires. [Permissions](permissions.md#the-keys-that-sign-a-token) has it.
- **The vault key.** `osapi controller vault key rotate --name default`, on the
  controller host, as in [Vaults](vaults.md#the-vault-key).
- **The PKI keys.** As now, with the grace period of
  [Agent identity](agent-identity.md#rotation-without-an-outage).
- **NATS credentials.** Out of scope here. The embedded server reads them from
  the config, and a change needs a restart.

## The parts

Each part is an issue in osapi, in this order:

01. Built: `secret.Value` in `internal/secret`, in place of the `secret` tag,
    with the `secret` rule in each DSL and the `dslcheck` guard.
02. Built: the `Vault` interface, the `nats` type, the `controller.secrets`
    config, and `osapi controller vault key create --name default` and `rotate`
    ([Vaults](vaults.md)).
03. JetStream encryption at rest, with its key in the config and
    `osapi nats key create`. Built: osapi #1242.
04. Built: the `secret` endpoint group and its area, `secret:read`,
    `secret:write` and `secret:use`, and the Secrets page of the UI
    ([Vaults](vaults.md#the-secret-endpoint-group)).
05. Resolution on the controller: the order above, the three limits of use, and
    the references in the audit entry. Built:
    [Vaults](vaults.md#how-a-route-resolves-a-reference).
06. Built: `secret://` references in the config, resolved at startup and by the
    commands that read them
    ([Configuration](configuration.md#a-secret-can-be-a-reference-to-a-vault)).
07. The agent's X25519 key at enrollment. Built:
    [Agent identity](agent-identity.md#the-encryption-key).
08. Built: sealed values in the job, opened by the dispatch of the agent, with
    the docker `env` fields as the first users.
09. Built: the reference picker of the UI, and the rule in the skill
    ([What an AI agent learns](#what-an-ai-agent-learns)).
10. More than one JWT signing key. Built, in
    [Permissions](permissions.md#the-keys-that-sign-a-token).
11. The vault types of extensions, after osapi #1064.
12. Built: the default vault `default`, whose key the controller makes at its
    first start ([Vaults](vaults.md#the-config)), osapi-io/osapi#1308.

## What this page does not cover

- An external store as a built-in type. Vault, 1Password and the cloud stores
  are extensions.
- A secret that the controller cannot read. Use a backend that enforces that.
- Secrets of the NATS server itself, such as its own TLS key.
- A push of a new value to the hosts that have the old one. A plan or a workflow
  runs the job again.
