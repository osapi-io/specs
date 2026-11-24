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

1. the defaults: `config.Defaults` in `internal/config/keys.go`, and the field
   values of the settings that each behavior declares
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
from the type, the default and the doc of its key. Thus the default of a key is
in `config.Defaults` only, and `config get` shows the default that the flag has.

Before that change, `AutomaticEnv` read only the keys that viper already knew
from a default or from the file. Thus viper ignored a variable for each other
key, and nothing reported it.

`config.Defaults` names keys of the config struct. A test fails on a name that
is not a key. Two sets of defaults in `cmd/root.go` used `controller.api.nats.*`
and `nats.api.*`. These keys do not exist, so the defaults did not apply until
somebody moved them.

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
`internal/config/checks.go`: `file`, `parse`, `value`, `setting` and `bucket`.
`validate` lists each problem, not only the first, with its rule, its key and
the fix of the rule, in text and in `--json`. It prints its report, then exits 1
when the config is not valid: the method returns its output with
`command.Fail()`, so a script or CI fails on it. That is the shape of
`behavior validate`. `validate --help` lists each rule with its fix. A value
that breaks its `validate` tag is named by its config key, such as
`controller.api.security.signing_key`, not by its Go field. Thus the key goes
straight to `config get --key`. `start` reads the same problems through `Load`,
and refuses to start on any of them. A test fails on a `Rule` constant without a
check. It follows
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

## Secrets are masked before the config is logged

At startup, the controller logs all of its resolved config. Without masks, the
log gets each password.

Struct tags mark what must not appear:

```go
Controller Controller `mapstructure:"controller" mask:"struct"`
Password   string     `mapstructure:"password"   mask:"password"`
```

`cmd/controller.go` gives the config to go-masker in `PersistentPreRun`, before
it logs the config. Thus the code reads the tags. They are not decoration. Seven
fields have a mask tag.

A key that osapi keeps on the disk is a file, and the config has only its path.
`nats.server.jetstream.key_file` is one: the key that encrypts the streams of
the embedded server. A path is not a secret, so it has no mask, and the
controller logs it.
[The message bus](transport.md#the-streams-are-encrypted-on-the-disk) has the
key.

**The agent does not mask, because it does not log the struct.** It logs named
fields: host, port and client name. It never logs a password. These are two
different solutions to the same problem. The solution of the agent stays safe
only while nobody adds a secret to the list of fields that it logs.

## Where this connects

[The job system](job-system.md) has the two clocks of a job. You configure the
two here.

[The embedded UI](ui.md) has `controller.ui.enabled`, the only dashboard setting
that an operator changes.

[Agent identity](agent-identity.md) has the PKI switches. With them, you can
enable enforcement in stages on a live fleet.

______________________________________________________________________

Written from `cmd/root.go` and `internal/config/`.
