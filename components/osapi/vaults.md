# Vaults

A vault is a store of secrets on the controller. It has a name and a type. The
controller resolves a `secret://<vault>/<key>` reference through the vault that
the reference names. `internal/secret/vault` has the interface and the registry
of types. `internal/secret/vault/natsvault` has `nats`, the one type that osapi
ships. [Secrets](secrets.md) has the plan that uses the vaults: the reference
syntax, the `secret` endpoint group, and the values that the controller seals to
an agent.

## The interface

Each type makes a `vault.Vault`:

```go
type Vault interface {
    Name() string
    Get(ctx context.Context, key string) ([]byte, Meta, error)
    Put(ctx context.Context, key string, value []byte) (Meta, error)
    Delete(ctx context.Context, key string) error
    List(ctx context.Context) ([]Meta, error)
}
```

`Meta` is the key, its version, the time of the last `Put` and who did it. The
version is 1 for the first value of a key, and one more for each `Put` after it.
`List` gives the metadata of each key, and no value. `Get` and `Delete` of a key
that is not there give `vault.ErrNotFound`.

`Put` does not take the caller as an argument. The caller puts its subject in
the context with `vault.WithActor`, and the vault reads it with `vault.Actor`.
Thus the interface keeps the five methods of the plan, and a type that does not
record the caller ignores it.

A value is `[]byte` now. It becomes `secret.Value` when that type is built
([osapi #1240](https://github.com/osapi-io/osapi/issues/1240)).

A key is 1 to 128 letters, digits, `-` or `_`. `vault.CheckKey` checks it. A dot
is not in a key, because the `nats` type uses the dot to separate the vault from
the key.

## A type plugs in through a registry

A type registers its name, one line that tells what it is, the Go struct of its
`config` block, a check of the vault spec, and a constructor:

```go
var Type = vault.Register(vault.Define(
    "nats",
    "Each value encrypted with AES-256-GCM under the vault key, ...",
    check, // func(vault.Spec) error
    build, // func(ctx, vault.Env, vault.Spec, Config) (vault.Vault, error)
))
```

`vault.Define` is generic over the config struct. Thus a constructor gets its
config as a typed value, not as a map. `Type.Decode` decodes the `config` block
of a vault into the struct. A key that the struct does not have is an error that
names the key, so a typo does not pass.

The struct does the same work as each other config block of osapi:

- **The config check.** `osapi config validate`, and `start` through
  `config.Load`, run the rule `vault`. It decodes each block, validates the
  struct with its `validate` tags, and runs the check of the type. A problem
  names its key, such as `controller.secrets.vaults[0].config.address`.
- **The docs table.** `config.VaultKeys` walks the spec of a vault, then the
  struct of each registered type, under `controller.secrets.vaults[]`. A
  `<!-- osapi:config controller.secrets -->` table on the docs site shows them,
  with the type in front of the doc of each setting of a type.

`vault.Env` is what the controller gives each constructor: the NATS client, the
secrets bucket with its namespace, the file system and `os.LookupEnv`. A type
that does not use NATS ignores the client.

A type of an extension registers in the same way, after extensions exist
([osapi #1064](https://github.com/osapi-io/osapi/issues/1064)). A reference
names the vault, not the type. Thus the keys of a vault can move to a different
type, and each reference still resolves.

## The config

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
nats:
  secrets:
    bucket: secrets
    history: 10
```

Each item of `controller.secrets.vaults` is a `vault.Spec`:

| Field      | What it is                                                        |
| ---------- | ----------------------------------------------------------------- |
| `name`     | the name in a reference. Letters, digits, `-` and `_`, 64 at most |
| `type`     | a registered type, such as `nats`                                 |
| `targets`  | the targets that its secrets can go to. Empty is each host        |
| `key_file` | the file of the key, for a type that encrypts, such as `nats`     |
| `key_env`  | the environment variable of the key, in place of `key_file`       |
| `config`   | the settings of the type, which the struct of the type gives      |

The rule `vault` also refuses two vaults with one name, and two vaults with one
`key_file`. A rotation of a shared file would drop the key of the other vault,
and each value of that vault would then not decrypt.

`targets` is in the spec now. The controller enforces it when it seals a value
for an agent ([Who may use a secret](secrets.md#who-may-use-a-secret)).

The controller opens each vault at startup, in `internal/controller/vaults.go`,
after it connects to NATS. A type that is not registered, a block that does not
decode, a check that fails, a bucket that is not there or a key that does not
load stops the controller, with the name of the vault and the fix:

```
start the controller: vault "default": read the vault key: open /etc/osapi/secrets.key:
no such file or directory: make it with osapi controller vault key create
```

The controller does not start with a vault that it cannot use, because each
request that uses a secret of that vault would fail later.

## The nats type

NATS has no secret store. The `nats` type keeps each value encrypted in the KV
bucket of `nats.secrets`, which is `osapi-secrets` with the namespace `osapi`.
`osapi nats setup` and `osapi nats start` make the bucket with each other
bucket. The bucket keeps `nats.secrets.history` versions of each key, 10 by
default and 64 at most.

The KV key of a value is `<vault>.<key>`, such as `default.registry-token`. Thus
two `nats` vaults share one bucket, and `List` reads only the keys of its own
vault, with the filter `<vault>.>`.

Each KV value is a JSON record:

```json
{
  "version": 3,
  "changed": "2026-11-23T22:56:50Z",
  "by": "ops@example.com",
  "key_id": "7a10fe4922e2390a",
  "nonce": "...",
  "data": "..."
}
```

- **The encryption.** `data` is the value, encrypted with AES-256-GCM under the
  vault key, with a new random nonce at each `Put`. The additional data is
  `<vault>/<key>`. Thus a value that somebody copies to a different key does not
  decrypt.
- **The metadata.** `version`, `changed` and `by` are plain text. Thus `List`
  reads the metadata with no key, and the metadata of an earlier version stays
  readable after a rotation.
- **The key ID.** It is the first 16 hex digits of the SHA-256 of the key. The
  record tells which key encrypts it, and the key never leaves the controller
  host.

A `Put` writes with the revision that it read: `KVCreate` for a new key, and
`KVUpdate` at the revision for a key that is there. Thus a `Put` at the same
time as a different `Put` fails, and does not overwrite it. A `Delete` writes a
delete marker, and the bucket keeps the earlier versions as its history allows.
A `Put` after a `Delete` starts again at version 1.

The vault reads its key at each call, not one time at startup. The cost is a
read of a small file. The advantage is that a rotation applies to a controller
that runs, with no restart.

## The vault key

The key file has one key on each line, as 64 hex digits. The first key is the
current key, which encrypts. Each key decrypts. A blank line and a line that
starts with `#` are not keys. `key_env` holds the same text in an environment
variable.

The two commands run on the controller host, under `osapi controller`, because
the key is a file there and the API does not give it or change it. They read the
config of the controller:

| Command                                            | What it does                                                      |
| -------------------------------------------------- | ----------------------------------------------------------------- |
| `osapi controller vault key create --name default` | writes a new key to `key_file`, with the mode 0600                |
| `osapi controller vault key rotate --name default` | adds a new key, encrypts each value again, then drops the old one |

Each prints the name of the vault, the file and the ID of the new key, not the
key. `rotate` also prints how many values it encrypted again.

`create` does not replace a key that is there. Each value under the old key
would then not decrypt. Use `rotate` for that.

`rotate` follows the model of `JetStreamOldKey` in NATS:

1. It writes the file with the new key first and the old keys after it.
2. It connects to NATS as the controller does, and encrypts each value of the
   vault that is not under the new key again. The metadata of each value stays.
   When a `Put` changes a value during the rotation, the command reads it again,
   up to three times.
3. It writes the file with only the new key.

A controller that runs puts each new value under the new key after step 1,
because it reads the file at each call. If the rotation stops in step 2, the
file keeps the old keys, so each value still decrypts, and a second rotation
completes it.

A rotation does not encrypt the earlier versions in the history of the bucket
again. The KV cannot change an earlier version. Thus an earlier version stays
under the old key, and does not decrypt after step 3. Its metadata stays
readable.

`create` and `rotate` refuse a vault whose key is in `key_env`, because they
write `key_file`. A key in an environment variable is rotated outside osapi.
They also refuse a vault of a type that is not `nats`.

## How a route resolves a reference

Built in osapi-io/osapi#1244. `Serve` in `internal/controller/endpoint/server`
resolves each reference of the input before it calls the handler of the method.
Thus each method of the behavior DSL and of the endpoint DSL resolves a
reference, with no code in the method. The controller gives the server its
vaults as `server.Secrets`. `secrets.go` does these steps, in this order:

1. **Find the vault.** Each reference has the form `secret://<vault>/<key>`, a
   key that `CheckKey` accepts, and a vault of `controller.secrets.vaults`. If
   not, the request gets 400.
2. **Check the limits of use.** The token has the permission `secret:use`. The
   host of the route is in the `targets` of each vault that has targets. If not,
   the request gets 403. A route with no host, such as a method that runs on the
   controller, gets no secret from a vault with targets. A target such as `_all`
   is not in the targets, as it is not in a target scope. The middleware refused
   a host outside the target scope of the token before this step.
3. **Read each value.** `secret.Resolve` reads each value from its vault, and
   puts it in place of the reference. A key that the vault does not have gives
   400\. A vault that does not answer gives 500, and the controller logs the
   cause.
4. **Validate the values.** `Valid` checks the input again, so each value obeys
   the `validate` tags of its field, such as `no_linebreak` on a password.

The limits come before the read. Thus a caller without `secret:use` does not
learn if a key exists, and the controller reads no value that it does not use.
Each refusal gives the reference, never the value.

The middleware puts the permissions of the token in the context of the request
with `authtoken.WithPermissions`. `authtoken.Granted` reads them.

The handler gets the value. A `.Before` step runs on the value, and the job
keeps the value that the step leaves. The audit entry keeps the reference,
because the audit records the body of the request. A span never records a
secret. A chain record on the agent has `[redacted]`, because the job has the
value. The sealed values of osapi-io/osapi#1247 keep the value out of the job.

## What this page does not cover

- The `secret` endpoint group, and who may read or write a secret
  ([osapi #1243](https://github.com/osapi-io/osapi/issues/1243)).
- The seal of a value to an agent. [Secrets](secrets.md) has the plan.
  [Configuration](configuration.md#a-secret-can-be-a-reference-to-a-vault) has
  the references in the config, which `Set.Resolve` resolves.
- JetStream encryption at rest, with its own key and `osapi nats key create`.
  That key protects each stream and bucket on the disk. It does not protect
  against a NATS user, which is why the vault encrypts each value too.
- A key from a KMS or a TPM. It can come through the same setting later.

______________________________________________________________________

Written from `internal/secret/vault/`, `internal/secret/vault/natsvault/`,
`internal/config/vaults.go` and `internal/cli/commands/vaultkey/`.
