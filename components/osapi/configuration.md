# Configuration

One config file, one struct, resolved once at startup and validated before
anything runs. `internal/config` holds the shape; `cmd/root.go` resolves it.

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

Viper, with four sources. Later beats earlier:

1. the defaults, `config.Defaults` in `internal/config/keys.go`, and the field
   values of each behavior's declared settings
2. the config file, YAML, found by the `--osapi-file` flag
3. the environment
4. a flag bound to the key, such as `controller --port`

An environment variable is the config path with `OSAPI_` in front and dots
replaced by underscores, so `controller.api.port` is
`OSAPI_CONTROLLER_API_PORT`. `config.Read` binds every key to its variable.
Before it did, `AutomaticEnv` reached only keys viper already knew from a
default or the file, so a variable for any other key was silently ignored.

`config.Defaults` names keys of the config struct, and a test fails on one that
is not. Two sets of defaults in `cmd/root.go` were set on
`controller.api.nats.*` and `nats.api.*`, keys that do not exist, and never
applied until they moved.

## The binary describes its own settings

`config.Keys` walks the config struct's `mapstructure` tags, so the list of
settings is the code rather than a page about it. Every field carries a `doc`
tag, and a test fails on one without.

```sh
osapi config list                           # every key: value, source, env var
osapi config list --json                    # plus type, default, rules, description
osapi config get --key controller.api.port  # one key in full
osapi config validate                       # the checks start runs, starting nothing
```

`list` and `get` read the config the way `start` does but skip the checks, and
work without a file, so they can show what is wrong. Each value's source is
`env`, `file`, `default` or `unset`. A field tagged `mask:"password"` prints as
`********`. The site's configuration page points at these commands rather than
listing the keys, because the list it carried had drifted: its sample YAML
nested NATS settings where osapi never reads them.

## The shape

Four top-level sections and a flag.

| Section      | For                                              |
| ------------ | ------------------------------------------------ |
| `controller` | the API, the UI, metrics, PKI, notifications     |
| `agent`      | the agent's NATS connection, consumer and PKI    |
| `nats`       | the embedded server, and the streams and buckets |
| `telemetry`  | tracing and the metrics server                   |
| `debug`      | a boolean, set from the CLI                      |
| `behaviors`  | each behavior's own settings, under its name     |

`behaviors` is not in the config struct. Each behavior declares its settings
beside its definition, and they join the registry under `behaviors.<name>`;
[behaviors](behaviors.md#settings-a-behavior-declares) has how.

`agent` is `omitempty`, because a controller-only deployment does not need it.
The same binary reads the same file and takes the half it needs.

## Validation happens before the process starts

`config.Validate` runs the struct through the shared validator, and the
validator registers osapi's own rules first. So a bad value fails at startup
with a message naming the field rather than at the moment the value is first
used.

That is the same validator [building a domain](domains.md) describes for request
input, which is why a custom rule registered for one is available to the other.

## Secrets are masked before the config is logged

The controller logs its whole resolved config at startup, which would otherwise
put every password in the log.

Struct tags mark what must not appear:

```go
Controller Controller `mapstructure:"controller" mask:"struct"`
Password   string     `mapstructure:"password"   mask:"password"`
```

`cmd/controller.go` runs the config through go-masker in `PersistentPreRun`
before logging it, so the tags are read rather than decorative. Seven fields
carry one.

**The agent does not mask, because it does not log the struct.** It logs named
fields instead, host, port and client name, and never a password. Two different
approaches to the same problem, and the agent's only stays safe as long as
nobody adds a secret to the list of fields it names.

## Where this connects

The two clocks a job runs under, both configured here, are
[the job system](job-system.md).

`controller.ui.enabled`, the one setting an operator has over the dashboard, is
[the embedded UI](ui.md).

The PKI switches that let enforcement be staged across a live fleet are
[agent identity](agent-identity.md).

______________________________________________________________________

Written from `cmd/root.go` and `internal/config/`.
