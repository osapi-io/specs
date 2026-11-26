# Configuration

There is one config file and one struct. osapi resolves the config one time, at
startup, and validates it before anything runs. `internal/config` has the shape.
`cmd/root.go` resolves it.

```yaml
controller:
  api:
    port: 8080
    job_timeout: 30s
  ui:
    enabled: true
nats:
  stream:
    name: JOBS
    subjects: jobs.>
  kv:
    bucket: job-queue
```

## Where a value comes from

Viper reads four sources. A later source replaces an earlier source:

1. the defaults: the values that the definition of each section declares, and
   the field values of the settings that each behavior declares
   ([Each default has one owner](#each-default-has-one-owner))
2. the config file, in YAML, at the path that the `--osapi-file` flag gives
3. the environment
4. a flag that is bound to the key, for example
   `controller start --controller-api-port`

The name of an environment variable is the config path with `OSAPI_` at the
start. Underscores replace the dots. Thus `controller.api.port` is
`OSAPI_CONTROLLER_API_PORT`. `config.Read` binds each key to its variable.

The name of a flag is the config path with dashes for its dots and underscores,
such as `--controller-api-port`. A process names its keys with `.Flag` in the
[command DSL](commands.md#processes), and `config.BindFlags` makes each flag
from the type, the default and the doc of its key. A flag with a name of its
own, such as `osapi client --url` for `controller.client.url`, uses
`config.BindFlagAs`. Thus the default of a key is in the definition that owns it
only, and `config get` shows the default that the flag has.

Before that change, `AutomaticEnv` read only the keys that viper already knew
from a default or from the file. Thus viper ignored a variable for each other
key, and nothing reported it.

## Each default has one owner

The process group that uses a section of the config declares its defaults, in
its definition, with `command.Config`:

| Group              | Section      | Defaults in                                       |
| ------------------ | ------------ | ------------------------------------------------- |
| `controller start` | `controller` | `internal/cli/commands/controllercmd/defaults.go` |
| `agent start`      | `agent`      | `internal/cli/commands/agentcmd/defaults.go`      |
| `nats start`       | `nats`       | `internal/cli/commands/natsserver/defaults.go`    |
| `start`            | `telemetry`  | `internal/cli/commands/startcmd/start.go`         |

A behavior declares the defaults of its settings with `behavior.Config`. The
value is a struct of the section's type, so a key that does not exist does not
compile. `command.Config` puts the value in `internal/settings`, a package that
imports nothing of osapi. `config.Keys` reads the defaults from there. Thus the
`config` package does not import the groups, and there is no cycle from config
to behavior to the command DSL. Two groups that claim one section panic at
startup.

Before osapi-io/osapi#1387, `config.Defaults` in `internal/config/keys.go` had
the defaults of each section, and `configs/osapi.yaml` had about 110 values that
no default had. Thus a config file without those keys did not get those values,
and the two lists disagreed.

Each key has a default, or the tag `choice:"<why>"` that says why the operator
picks it: a URL, a token, a certificate, the labels of a host. A test fails on a
key that has neither. Thus an empty config file runs a controller, an agent and
a NATS server on one host.

`osapi config default get` prints the whole config at its defaults, as YAML,
each key with its doc. A key that is a choice is commented out, with why. The
output loads as a valid config. osapi has no sample config file to keep up to
date.

## The signing key of the controller

`controller.api.security.signing_keys` can be empty. Then the controller makes
an HS256 key of 32 random bytes in `controller.pki.key_dir`, as `signing.key`
with mode 0600, at its first start, and uses it with the id `local`.
`controller token generate` on the same host reads the same file. Thus a token
that it signs passes the API with no key in the config. A key in the config, or
a reference to one, replaces the file. `config.EnsureSigningKey` runs after the
references resolve.

`controller.client.security.bearer_token` can be empty too. A request without a
token gets 401 from the API, which tells the person what to set.

## The binary describes its own settings

`config.Keys` reads the `mapstructure` tags of the config struct. Thus the code
is the list of settings, not a page about it. Each field has a `doc` tag, and a
test fails on a field without one.

```sh
osapi config list                           # every key: value, source, env var
osapi config list --json                    # plus type, default, rules, description
osapi config get --key controller.api.port  # one key in full
osapi config validate                       # the checks start runs, starting nothing
```

The commands come from the `config` group of the [command DSL](commands.md), in
`internal/cli/commands/config/`. `list` prints one table of each key, sorted by
key, so the keys of a section sit together; `--json` is the file and the keys,
`{file, items}`. `get` prints the file and the setting.

`list` and `get` read the config as `start` does, but they do not run the
checks. They also work without a file. Thus they can show what is incorrect. The
source of each value is `env`, `file`, `default` or `unset`. A field with the
tag `mask:"password"` prints as `********`.

`validate` runs the checks of `start`, which are the table `Checks` in
`internal/config/checks.go`: `file`, `parse`, `value`, `setting`, `bucket`,
`vault` and `reference`. `validate` lists each problem, not only the first, with
its rule, its key and the fix of the rule, in text and in `--json`. It prints
its report, then exits 1 when the config is not valid: the method returns its
output with `command.Fail()`, so a script or CI fails on it. That is the shape
of `behavior validate`. `validate --help` lists each rule with its fix. A value
that breaks its `validate` tag is named by its config key, such as
`controller.api.security.signing_keys[0].key`, not by its Go field. Thus the key
goes straight to `config get --key`. `start` reads the same problems through
`Load`, and refuses to start on any of them. A test fails on a `Rule` constant
without a check. It follows
[the commands that teach](cli.md#commands-that-teach-for-agents).

The configuration page of the site points to these commands. It does not list
the keys, because its old list was incorrect. Its sample YAML put NATS settings
in a location that osapi never reads.

## The shape

There are four top-level sections, a flag and the behavior settings.

| Section      | For                                              |
| ------------ | ------------------------------------------------ |
| `controller` | the API, the UI, metrics, PKI, notifications     |
| `agent`      | the agent's NATS connection, consumer and PKI    |
| `nats`       | the embedded server, and the streams and buckets |
| `telemetry`  | tracing and the metrics server                   |
| `debug`      | a boolean, set from the CLI                      |
| `behaviors`  | each behavior's own settings, under its name     |

`behaviors` is not in the config struct. Each behavior declares its settings
next to its definition. They join the registry under `behaviors.<name>`.
[Behaviors](behaviors.md#settings-a-behavior-declares) tells how.

`agent` is `omitempty`, because a deployment with only a controller does not
need it. The same binary reads the same file and uses the half that it needs.

## Validation happens before the process starts

`config.Validate` gives the struct to the shared validator. The validator
registers the rules of osapi first. Thus an incorrect value fails at startup,
with a message that names the field. It does not fail later, when osapi first
uses the value.

Each bucket name and each namespace must be a name that NATS accepts for a
bucket. The `nats_name` rule checks it. A namespace is in the rule because it
becomes the prefix of each bucket name. Then `config.Validate` checks that no
two settings name the same KV bucket, because each role keeps its own keys in
its bucket. An empty bucket turns its role off, and the check skips it. The
Object Store buckets are compared only with each other, because NATS keeps them
in different streams from the KV buckets.

[Behaviors](behaviors.md#types-become-json-schema) describes the same validator
for request input. Thus a custom rule that you register for one is also
available to the other.

## A secret never gets to a log or a printout

The tag `mask:"password"` marks a secret of the config. Five fields have it:
`NATSAuth.Password`, `NATSServerUser.Password`, `ServerSecurity.SigningKeys`,
`SigningKey.Key` and `ClientSecurity.BearerToken`.

```go
Password string `mapstructure:"password" mask:"password"`
```

Two parts of osapi read the tag. They are not decoration:

- `internal/config/keys.go` sets `Key.Secret` for the field. Thus
  `osapi config list` and `config get` print its value as `********`.
- `internal/config/references.go` lets the field be a reference,
  `secret://<vault>/<key>`, which a vault resolves.

**The controller and the agent log only named fields.** At start, the controller
logs the config file, the API port, the NATS host, port, client name, namespace
and auth type, and the CORS origins
(`internal/cli/commands/controllercmd/methods.go`). It never logs the config
struct. Before osapi #927, go-masker masked the struct before the controller
logged all of it. This stays safe only while nobody adds a secret to the fields
that are logged.

A key that osapi keeps on the disk is a file, and the config has only its path.
`nats.server.jetstream.key_file` is one: the key that encrypts the streams of
the embedded server. A path is not a secret, so it has no mask, and the
controller logs it.
[The message bus](transport.md#the-streams-are-encrypted-on-the-disk) has the
key.

## A secret can be a reference to a vault

A field with the tag `mask:"password"` takes a reference,
`secret://<vault>/<key>`, in place of its value. The file and the environment
take it in the same form:

```yaml
controller:
  api:
    security:
      signing_keys:
        - id: 2026-11
          key: secret://default/jwt-signing-key
  client:
    security:
      bearer_token: secret://default/cli-token
```

`internal/config/references.go` finds each reference. It walks the config struct
for the string fields with the mask tag, and names each one by its config key,
such as `controller.api.security.signing_keys[0].key`.

**The checks.** The rule `reference` of `validate` and `start` refuses three
references:

- a reference that does not parse. `vault.ParseReference` in
  `internal/secret/vault` has the syntax.
- a reference to a vault that `controller.secrets.vaults` does not have. A
  config with no vaults has one, `default`, so `secret://default/<key>` works on
  a new install ([Vaults](vaults.md) has its key file).
- a reference in a field with the tag `noref`. The tag holds the reason.

The rule `value` does not apply to a reference. The rule of the key applies to
the value when osapi resolves it. Thus `signing_key` does not refuse
`secret://default/jwt` because it is short.

**The resolution.** `config.ResolveReferences` resolves each reference under a
key prefix, and puts the value in its place. Then it checks the value against
the `validate` tag of its key. An error names the key and the reference. It
never shows the value. Each process resolves only the values that it reads:

| Process                                          | Prefix                                 | When                                  |
| ------------------------------------------------ | -------------------------------------- | ------------------------------------- |
| the controller                                   | `controller.api`                       | at startup, after it opens the vaults |
| `osapi controller token generate` and `validate` | `controller.api.security.signing_keys` | before the command signs or checks    |
| each `osapi client` command                      | `controller.client`                    | before the command makes its client   |

A command calls no API. Thus a command opens the vaults itself, with
`controller.OpenVaults` on a NATS connection of `controller.nats`, as the
controller does. It connects only when a value that it reads is a reference. A
host that cannot connect to NATS as the controller, or cannot read the vault
key, needs the value in its config.

**What cannot be a reference.** osapi needs some values before it can read a
vault. A reference to a vault in one of them is a loop:

- **A NATS password.** The `nats` vault reads its values through NATS. Thus
  `NATSAuth.Password` and `NATSServerUser.Password` have the tag `noref`. The
  tag covers `controller.nats.auth.password`, `agent.nats.auth.password` and
  `nats.server.auth.users[].password`. The agent never resolves a reference.
- **The vault key.** The rule `vault` refuses a reference in `key_file`. The
  `nats` type refuses a line of the key that is a reference, from the file or
  from the variable that `key_env` names. Thus the controller does not start
  with it.

A vault of a type that does not use NATS can hold a NATS password later. osapi
ships only the `nats` type now, so the tag refuses each NATS password.

## TLS

Each server and each connection over HTTP or gRPC has its own `tls` block. TLS
is off in each by default. There is no top-level block, and a block does not
take a value from another block. Two shapes are used, each in `internal/config`
with one function that builds its `tls.Config`:

| Shape  | Keys                                                                                 | Blocks                                                                                                                                       |
| ------ | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| server | `enabled`, `cert_file`, `key_file`                                                   | `controller.api.tls`, `nats.server.tls`, `controller.metrics.tls`, `agent.metrics.tls`, `nats.server.metrics.tls`                            |
| client | `enabled`, `ca_file`, `cert_file`, `key_file`, `server_name`, `insecure_skip_verify` | `controller.client.tls` (the CLI), `controller.nats.tls`, `agent.nats.tls`, `telemetry.tracing.tls` (the OTLP exporter and the trace reader) |

Each server serves TLS by default (osapi-io/osapi#1413). The certificate of a
server comes from one of two places:

- `controller.api.tls.cert_file` and `key_file`: a certificate from any source,
  such as `tailscale cert`, certbot, step-ca or a company CA. A new certificate
  replaces the old one with no other change.

- Neither set: the process makes a self-signed ECDSA P-256 certificate in its
  key directory at its first start, for this host and `localhost`, and uses it
  after that. One function makes each, `config.ServerTLS.WithSelfSigned`:

  | Server                    | Files                                                                                    | Directory                |
  | ------------------------- | ---------------------------------------------------------------------------------------- | ------------------------ |
  | the API                   | `api.crt`, `api.key`, also for the hosts of `controller.api.url` and `controller.ui.url` | `controller.pki.key_dir` |
  | the NATS server           | `nats.crt`, `nats.key`                                                                   | `nats.server.key_dir`    |
  | the controller's metrics  | `controller-metrics.crt`                                                                 | `controller.pki.key_dir` |
  | the agent's metrics       | `agent-metrics.crt`                                                                      | `agent.pki.key_dir`      |
  | the NATS server's metrics | `nats-metrics.crt`                                                                       | `nats.server.key_dir`    |

A metrics server whose certificate cannot be made or loaded does not start, and
does not serve plain HTTP in place of HTTPS; its process continues. A NATS
server whose certificate cannot be made does not start. Before
osapi-io/osapi#1413 only the API had a self-signed certificate, and TLS was off
by default everywhere.

A client trusts the system's roots, and `ca_file` if it is set, such as the
`api.crt` of a self-signed controller. A client of a server on the same host,
with no `ca_file`, trusts that server's self-signed certificate:
`config.TrustLocal` sets the CLI's `ca_file` to `api.crt` for an `https://` URL
of `localhost` or a loopback address, and the controller's and the agent's NATS
`ca_file` to `nats.crt` for a loopback NATS host. A client on another host needs
`ca_file`, or the pin of a join string. `cert_file` and `key_file` send a client
certificate to a server that asks for one. A URL that starts with `https://`
uses TLS without `enabled`. The OTLP endpoint has no scheme, so
`telemetry.tracing.tls.enabled` decides for the exporter. Before
osapi-io/osapi#1385 the exporter always connected in plain text.

`insecure_skip_verify` accepts each certificate. Thus it also accepts the
certificate of an attacker in the path. osapi logs a warning that names the
setting at each start that has it on. Use it only for a test.

A NATS connection has no scheme in the config, so `enabled` decides. Each of the
five places that dial NATS (the job client of the controller and of each agent,
`nats setup`, the references of the config, and the join token and vault key
commands) builds its options with `bus.ConnectionOptions`. Thus a new place that
dials NATS gets TLS without a change. The NATS server's own connection, for its
setup and heartbeat, trusts the certificate that the server serves and checks
the first name in it, because it dials its bind address. Health shows its
address as `tls://` (osapi-io/osapi#1396).

osapi has no ACME client. Let's Encrypt cannot issue a certificate for an
internal name, such as a `.internal` or `.local` name, without a DNS-01
challenge. Thus osapi takes a certificate from a tool that gets one. Agent join
([Agent join](agent-join.md)) needs HTTPS on, because the join token pins the
certificate (osapi-io/osapi#1381).

## Where this connects

[The job system](job-system.md) has the two clocks of a job. You configure the
two here.

[Secrets](secrets.md) has the plan of the secrets, and [Vaults](vaults.md) has
the vaults that a reference names.

[The embedded UI](ui.md) has `controller.ui.enabled`, the only dashboard setting
that an operator changes.

[Agent identity](agent-identity.md) has the PKI switches. With them, you can
enable enforcement in stages on a live fleet.

______________________________________________________________________

Written from `cmd/root.go`, `cmd/references.go` and `internal/config/`.
