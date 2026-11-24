# Secrets

A plan, not built. This page records where the secrets of osapi live, how the
three DSLs take one, how a value gets to the agent that uses it, and how a
secret rotates. Each part moves into the page of its subject when it is built,
and this page goes when the last part is built.
[osapi #1065](https://github.com/osapi-io/osapi/issues/1065) has the decision.

## What osapi has today

Each kind of secret has its own solution, and none of them is a store:

- The JWT signing key and the NATS passwords are values in `osapi.yaml` or in an
  environment variable. [Configuration](configuration.md) masks them before the
  controller logs its config.
- The PKI keys are files in `key_dir`. [Agent identity](agent-identity.md) has
  their rotation.
- A behavior input tagged `secret:"true"` stays out of the audit log, the spans
  and the chain records. [Behaviors](behaviors.md#secret-inputs) has the tag.

The tag does not keep a value out of NATS. The input of a behavior is the data
of its job, and JetStream and the job KV keep that data. A `.Before` step solves
this when the agent needs only a value made from the secret, such as the hash of
a password. It does not solve it when the agent uses the secret as it is.
`docker.create` and `docker.exec` take `env`, tagged secret, with no step. Thus
an API token in a container's environment sits in JetStream as plain text now.

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

A secret is a type, not a tag. `internal/secret` has `secret.Value`. An input
field of this type is a secret in each of the three DSLs, and the `secret` tag
goes. A tag with a typo makes the field an ordinary field, and nothing reports
it ([osapi #1062](https://github.com/osapi-io/osapi/issues/1062)). A type cannot
have a typo.

A `secret.Value` holds a reference or a literal value. Its `String`, `Format`,
`MarshalJSON` and `LogValue` give `[redacted]`. Only `Reveal` gives the bytes.
The resolver, the vault and the dispatch of the agent call it. A provider calls
it only where it gives the value to a command's standard input, an environment
or a file. A map of secrets is `map[string]secret.Value`, such as the
environment of a container.

What each part of a DSL ([The parts that each DSL shares](dsls.md)) does with a
`secret.Value` field:

| Part                    | What it does                                                                                                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spec of the API         | `type: string`, `format: password`, `writeOnly: true` and `x-osapi-secret: true`. The description says that it takes `secret://<vault>/<key>`.                                     |
| `validate`              | refuses a secret field with `telemetry:"attr"`, with `in:"path"` or `in:"query"` (a URL goes in logs), or as the key of a chain record. One rule, `secret`, in each DSL.           |
| `dslcheck`              | fails on a `string` field whose JSON name is on the audit denylist (`password`, `token`, `secret` and the others), unless its allowlist gives a reason. This finds a missing type. |
| CLI                     | the flag takes a reference, or `-` to read the value from standard input. It refuses a literal value, because the shell history keeps it. A map flag takes `NAME=secret://...`.    |
| SDK                     | a field of type `string` with a doc comment that it takes a reference. The SDK sends a literal or a reference as it gets it.                                                       |
| `method get` and docs   | marks the field as a secret, with the two forms that it takes.                                                                                                                     |
| Audit, spans and chains | record the reference, such as `secret://default/registry-token`, or `[redacted]` for a literal. A literal value never reaches a record.                                            |
| UI                      | a secret field takes a reference from a picker, next to the `@fact.` picker. A plan holds only references. The UI does not keep a value, and an exported plan has no value in it.  |

A command of the command DSL calls no API. Thus a command that uses a secret
resolves the reference itself, from the vaults of its config.
`osapi controller token generate` is one: it reads the signing key from the
config, and that value can be a reference.

## The order on the controller

The generated route of a behavior method does these steps, in this order:

1. Validate the input. A secret field passes as a reference or a value.
2. Resolve each reference, from any vault. A reference to a vault or a key that
   does not exist gives 400, with the reference and not a value.
3. Check that the caller may use each secret
   ([Who may use a secret](#who-may-use-a-secret)). A refusal gives 403.
4. Validate each resolved value against the `validate` tags of its field, such
   as `no_linebreak` on a password.
5. Run the `.Before` step, if the method has one. A step can change a secret to
   a value made from it, such as a password to its hash. A secret that the step
   clears is not sent.
6. Seal each secret that is still set, for the target agents
   ([How a value gets to the agent](#how-a-value-gets-to-the-agent)).
7. Queue the job.

Today a guard fails the request when a `.Before` step leaves a secret field set
(`internal/behavior/before.go`). After step 6 exists, the guard goes: a value
that is still set is sealed, not refused.

An endpoint method runs on the controller, so it does steps 1 to 4, and gives
the value to its handler. It queues nothing, so it seals nothing.

## How a value gets to the agent

The controller seals the values of a job once, then lets each target agent open
them:

1. It makes a new random key for the job, and encrypts each secret value of the
   job with it (XChaCha20-Poly1305).
2. It seals the job key to each target agent's X25519 key, with NaCl `box`.
   nkeys gives this as xkeys `Seal` and `Open`, which the NATS auth callout of
   nats-server already uses.
3. The job data has each secret field as `{"sealed": "<ciphertext>"}`, and one
   `sealed_keys` map from machine ID to the sealed job key. JetStream, the job
   KV and the audit log never see the plain value.
4. The dispatch of the agent opens the job key with its own X25519 key, opens
   each value into the `secret.Value` of its field, and calls the provider. It
   drops the values when the provider returns.

The job key is the only part that has one copy for each agent. Thus a large
value, such as a certificate key, goes in the job one time, also to `_all`.

The controller seals for the agents that the target names when it queues the
job. An agent that joins after that has no sealed key in the job. It reports the
job as failed, with the reason "the job was not sealed to this agent", and does
not run it.

## Secrets in a chain

A vault is not a behavior. A behavior runs on a host, as a job. A vault as a
behavior gives each agent credentials for the vault, and the agent then reads
each secret that the vault has. The design gives an agent only the values of its
job, so the vault stays on the controller.

A chain moves the value, not the vault. A parent behavior calls its children on
the agent, in the same job. Thus a `secret.Value` field of a parent goes to a
child as each other field does. For example, `certificate.create` takes a
private key and gives it to `managedfile.update` as the content of the file. The
controller resolves and seals the key one time, for the top method. The agent
opens it one time, and each method of the chain gets the opened value. The chain
records show the reference, not the value.

`behavior validate` checks the type across a chain: a parent that gives a
`secret.Value` to a child field of a different type fails under the rule
`secret`. Thus a chain cannot change a secret into an ordinary string, which the
child then records.

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

Three limits apply to each reference in a request. All three must pass:

- **The permission `secret:use`.** `admin` and `automation` have it. A secret
  goes into a write that changes the configuration of a host, and `automation`
  is the role that writes. `operator` runs actions, such as a restart, and no
  action takes a secret. `read`, `auditor` and `observer` do not have it.
- **The target scope of the token.** It limits the hosts, as for each other
  request ([Permissions](permissions.md#a-tokens-target-scope)).
- **The targets of the vault.** A vault can name the targets that its secrets go
  to, such as `group:prod`. The controller refuses to seal a secret of that
  vault for an agent outside them. A vault with no targets goes to each host.

The audit entry of the request records each reference that it used. Thus
`osapi client audit list` shows who used a secret, when, and on which hosts.

## The secret endpoint group

A secret is set and read through an endpoint group, `secret`, in the endpoint
DSL ([Endpoints](endpoints.md)). It is not a new DSL. A DSL is for a thing that
a contributor defines in Go, many times. A secret is data that an operator adds
at run time, as a file in the Object Store is. Thus the group gets each part of
the endpoint DSL with no new code: its OpenAPI spec, `endpoint validate`, the
SDK service, the CLI commands, the docs pages, its permissions and the
`apicontract` golden file.

| Method | Path                        | Permission     | CLI                              |
| ------ | --------------------------- | -------------- | -------------------------------- |
| GET    | `/api/secret`               | `secret:read`  | `osapi client secret vault list` |
| GET    | `/api/secret/{vault}`       | `secret:read`  | `osapi client secret list`       |
| GET    | `/api/secret/{vault}/{key}` | `secret:read`  | `osapi client secret get`        |
| PUT    | `/api/secret/{vault}/{key}` | `secret:write` | `osapi client secret update`     |
| DELETE | `/api/secret/{vault}/{key}` | `secret:write` | `osapi client secret delete`     |

- `vault list` lists each vault with its type, its targets and whether it
  answers.
- `get` gives the metadata of a key: its version, when it changed, and who
  changed it. It never gives the value. No method gives a value.
- `update` takes the value as a `secret.Value` body field. Thus the generated
  CLI reads it from standard input, or asks for it with the echo off:

```bash
osapi client secret update --vault default --key registry-token < token.txt
osapi client secret list --vault default
```

The commands are under `osapi client`, as the commands of each endpoint group
are, because they go through the API: they work from each host, and each call
has a permission check and an audit entry. The vault key is different. It is a
file on the controller host, and the API does not give it or change it. Thus its
two commands are under `osapi controller`, by the rule of the CLI that a command
goes where it runs
([osapi #1239](https://github.com/osapi-io/osapi/issues/1239)), as
`osapi controller key fingerprint` reads the PKI key in `key_dir`. They run on
the controller host, and read the config there:

| Command                                            | What it does                                         |
| -------------------------------------------------- | ---------------------------------------------------- |
| `osapi controller vault key create --name default` | makes the key of the `nats` vault in `key_file`      |
| `osapi controller vault key rotate --name default` | adds a new key, encrypts each value again, drops old |

The group is in a new area, `secrets`, as the Object Store has its own area. A
secret is not a step of a plan, because a plan file holds no values. The UI has
a Secrets page in the Admin menu that lists the names and sets a value with a
write-only field, under `canCall` of the group's operations.

## A vault is a backend that you can replace

A vault has a name, a type and its targets. The config names each vault:

```yaml
controller:
  secrets:
    vaults:
      - name: default
        type: nats
        key_file: /etc/osapi/secrets.key
      - name: prod
        type: vault # from an extension
        targets: [group:prod]
        config:
          address: https://vault.internal:8200
```

A type is a Go interface, as in the vaults of swamp:

```go
type Vault interface {
    Name() string
    Get(ctx context.Context, key string) (secret.Value, Meta, error)
    Put(ctx context.Context, key string, value secret.Value) (Meta, error)
    Delete(ctx context.Context, key string) error
    List(ctx context.Context) ([]Meta, error)
}
```

osapi ships one type, `nats`. A different store, such as HashiCorp Vault,
1Password or a cloud secret manager, is a type that an extension adds
([osapi #1064](https://github.com/osapi-io/osapi/issues/1064)). A type registers
with a name, a constructor and the Go struct of its `config` block. The struct
gives the config table of the docs and the check of the config, as each other
config block does. When extensions exist, a vault type gets the parts of a DSL
through the extension work: a spec, `validate` and a scaffold. A reference names
the vault, not the type. Thus you can move the keys of a vault to a different
type, and each reference still resolves.

swamp has the same design. Its backend interface is `get`, `put`, `list` and
`getName`, each vault has a name and a type, and only its local backend is built
in. AWS, Azure and 1Password are extensions. `swamp vault migrate` copies the
keys to a new type and keeps the name.

## The built-in vault

NATS does not have a secret store. The `nats` type is code in osapi that keeps
each value encrypted in a JetStream KV bucket, `osapi-secrets`:

- Each value is encrypted with AES-256-GCM under the vault key, with a new nonce
  each time. The KV holds only the encrypted value and its metadata.
- The KV keeps the earlier versions of a key, so `get` can show its history.
- The vault key comes from `key_file`, or from an environment variable that the
  config names. A KMS or a TPM can give the key later, through the same setting.
- A rotation adds a new key and keeps the old key for reads.
  `osapi controller vault key rotate --name default` encrypts each value again
  with the new key, then the old key goes. This is the model of
  `JetStreamOldKey` in NATS.
- `osapi controller vault key create --name default` makes the vault key in
  `key_file`.

osapi also turns on JetStream encryption at rest, with its own key.
`osapi nats key create` makes that key, on the NATS host. That key protects each
stream and bucket on the disk, not only the secrets, and NATS derives each
account's key from it. It does not protect against a NATS user, which is why the
vault encrypts each value too.

## References in the config

A config field that has a `mask` tag takes a reference, such as
`controller.api.security.signing_key: secret://default/jwt-signing-key`. The
controller resolves it at startup.

Two values cannot come from the `nats` vault, because the controller needs them
before it can read the vault:

- the vault key itself.
- the NATS credentials of the controller.

Each of these comes from a file, from the environment, or from a vault of a
different type, such as Vault.

## What an AI agent learns

A coding agent learns about a secret from the same generated parts as a person.
`method get` and the docs page of a method mark each secret field and its two
forms. `osapi client secret list` gives the names to reference. The skill in the
binary ([Agent skills](agent-skills.md)) has one rule for it: put a value in
with `osapi client secret update` from standard input, then use its reference.
Do not put a value in a command, a plan or a file.

## Rotation

- **A secret.** `update` writes a new version. A job that the controller queues
  after the change gets the new value. A host that has the old value, in a file
  or a container, keeps it until a job runs on it again. `secret get` shows when
  the key changed, and the audit log shows which hosts used it.
- **The JWT signing key.** The controller accepts tokens from more than one key,
  each with its own `kid`, and signs with the newest. Thus a new key goes in
  first, and the old one goes after the last token that it signed expires.
- **The vault key.** `osapi controller vault key rotate --name default`, on the
  controller host, as in [the built-in vault](#the-built-in-vault).
- **The PKI keys.** As now, with the grace period of
  [Agent identity](agent-identity.md#rotation-without-an-outage).
- **NATS credentials.** Out of scope here. The embedded server reads them from
  the config, and a change needs a restart.

## The parts

Each part is an issue in osapi, in this order:

01. `secret.Value` in `internal/secret`, in place of the `secret` tag, with the
    `secret` rule in each DSL and the `dslcheck` guard.
02. The `Vault` interface, the `nats` type, the `controller.secrets` config, and
    `osapi controller vault key create --name default` and `rotate`.
03. JetStream encryption at rest, with its key in the config and
    `osapi nats key create`.
04. The `secret` endpoint group and its area, `secret:read`, `secret:write` and
    `secret:use`, and the Secrets page of the UI.
05. Resolution on the controller: the order above, the three limits of use, and
    the references in the audit entry.
06. `secret://` references in the config, resolved at startup.
07. The agent's X25519 key at enrollment. Built:
    [Agent identity](agent-identity.md#the-encryption-key).
08. Sealed values in the job, opened by the dispatch of the agent, with the
    docker `env` fields as the first users.
09. The reference picker of the UI, and the rule in the skill.
10. More than one JWT signing key.
11. The vault types of extensions, after osapi #1064.

## What this page does not cover

- An external store as a built-in type. Vault, 1Password and the cloud stores
  are extensions.
- A secret that the controller cannot read. Use a backend that enforces that.
- Secrets of the NATS server itself, such as its own TLS key.
- A push of a new value to the hosts that have the old one. A plan or a workflow
  runs the job again.
