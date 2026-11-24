# Secrets

A plan, not built. This page records where the secrets of osapi live, how a
behavior gets one, and how they rotate. Each part moves into the page of its
subject when it is built, and this page goes when the last part is built.
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

## One reference syntax

A secret is a reference in each location that takes one:

```
secret://<vault>/<key>
```

`secret://default/registry-token` is the key `registry-token` in the vault
`default`. A config value, a behavior input and a step of a plan all take the
same form. The controller resolves a reference when it uses the value: at
startup for a config value, and when it dispatches the job for a behavior input.
It does not keep a resolved value between two uses.

A field that takes a reference is a field tagged `secret:"true"`. A literal
value in such a field still operates, and the plan below keeps it out of NATS
too. A reference is the form to use, because then the value is not in the
request, the shell history or the plan file.

The API never returns the value of a secret. It returns names, and whether a key
exists.

## A vault is a backend that you can replace

A vault has a name and a type. The config names each vault:

```yaml
controller:
  secrets:
    vaults:
      - name: default
        type: nats
        key_file: /etc/osapi/secrets.key
      - name: ops
        type: vault # from an extension
        config:
          address: https://vault.internal:8200
```

A type is a Go interface with four methods, as in the vaults of swamp:

```go
type Vault interface {
    Name() string
    Get(ctx context.Context, key string) ([]byte, error)
    Put(ctx context.Context, key string, value []byte) error
    List(ctx context.Context) ([]string, error)
}
```

`Delete` is the fifth method, for the CLI. osapi ships one type, `nats`. A
different store, such as HashiCorp Vault, 1Password or a cloud secret manager,
is a type that an extension adds
([osapi #1064](https://github.com/osapi-io/osapi/issues/1064)). The extension
gives a constructor and a schema for its `config` block. A reference names the
vault, not the type. Thus you can move the keys of a vault to a different type,
and each reference still resolves.

swamp has the same design. Its backend interface is `get`, `put`, `list` and
`getName`, each vault has a name and a type, and only its local backend is built
in. AWS, Azure and 1Password are extensions. `swamp vault migrate` copies the
keys to a new type and keeps the name.

## The built-in vault

NATS does not have a secret store. The `nats` type is code in osapi that keeps
each value encrypted in a JetStream KV bucket, `osapi-secrets`:

- Each value is encrypted with AES-256-GCM under the vault key, with a new nonce
  each time. The KV holds only the encrypted value.
- The vault key comes from `key_file`, or from an environment variable that the
  config names. A KMS or a TPM can give the key later, through the same setting.
- A rotation adds a new key and keeps the old key for reads. A command encrypts
  each value again with the new key, then the old key goes. This is the model of
  `JetStreamOldKey` in NATS.

osapi also turns on JetStream encryption at rest, with its own key. That key
protects each stream and bucket on the disk, not only the secrets, and NATS
derives each account's key from it. It does not protect against a NATS user,
which is why the vault encrypts each value too.

## A secret that the agent uses as it is

The controller resolves the reference, then seals the value to the agent that
runs the job. Only that agent can open it:

1. The route runs the `.Before` step, if the method has one.
2. The controller resolves each reference in a field tagged secret, from any
   vault.
3. For each target agent, it seals the value with NaCl `box` (X25519) to the
   agent's encryption key. nkeys gives this as xkeys `Seal` and `Open`, which
   the NATS auth callout already uses.
4. The job carries the sealed values, one for each target agent. JetStream, the
   job KV and the audit log never see the plain value.
5. The agent opens its sealed value before the provider runs, and drops it when
   the provider returns.

Thus an agent needs no credentials for any vault. A broadcast to `_all` carries
one sealed copy for each agent that it targets.

The agent gets an X25519 key of its own at enrollment, next to its Ed25519
signing key. One key does not do both jobs: the signing key signs, and the
encryption key opens. Enrollment sends both public keys, the fingerprint that
the operator admits covers both, and the controller keeps both in the enrollment
KV. A rotation of the agent's key seals nothing again, because the controller
seals at dispatch, not at storage.

## Redaction is a type

A tag that has a typo makes the field an ordinary field, and nothing reports it
([osapi #1062](https://github.com/osapi-io/osapi/issues/1062)). Thus the value
of a secret is a type, `secret.Value`. Its `String`, `Format`, `MarshalJSON` and
`LogValue` give `[redacted]`. Only `Reveal` gives the bytes, and only the agent
and the vault call it. A field of this type is a secret without a tag, and a
test fails on each print of a `secret.Value` in a log, a span, an error or the
output of the CLI.

## Setting a secret

The CLI reads the value from standard input, or asks for it with the echo off.
The value never goes on the command line, so it is not in the shell history:

```bash
osapi client secret set --vault default --key registry-token < token.txt
osapi client secret list --vault default
osapi client secret delete --vault default --key registry-token
```

The UI shows a field tagged secret as a password field with a reference picker.
It never keeps a value in the browser's storage, and an exported plan has the
reference, not the value.

The permissions are `secret:read`, which lists the names, and `secret:write`,
which sets and deletes a value. No permission reads a value.

## Rotation

- **The JWT signing key.** The controller accepts tokens from more than one key,
  each with its own `kid`, and signs with the newest. Thus a new key goes in
  first, and the old one goes after the last token that it signed expires.
- **The vault key.** A new key and a command that encrypts each value again, as
  in [the built-in vault](#the-built-in-vault).
- **The PKI keys.** As now, with the grace period of
  [Agent identity](agent-identity.md#rotation-without-an-outage).
- **NATS credentials.** Out of scope here. The embedded server reads them from
  the config, and a change needs a restart.

## The parts

Each part is an issue in osapi, in this order:

1. The `Vault` interface, the `nats` type and the `controller.secrets` config.
2. JetStream encryption at rest, with its key in the config.
3. `secret://` references in the config, resolved at startup.
4. `osapi client secret` and the `secret` permissions.
5. The agent's X25519 key at enrollment.
6. Sealed values in the job, with the docker `env` fields as the first users.
7. `secret.Value` in place of the `secret` tag.
8. More than one JWT signing key.
9. The vault types of extensions, after osapi #1064.

## What this page does not cover

- An external store as a built-in type. Vault, 1Password and the cloud stores
  are extensions.
- A secret that the controller cannot read. Use a backend that enforces that.
- Secrets of the NATS server itself, such as its own TLS key.
