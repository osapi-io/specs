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

Viper, with three sources. Later beats earlier:

1. the defaults in `cmd/root.go`
2. the config file, YAML, found by the `--osapi-file` flag
3. the environment

An environment variable is the config path with `osapi_` in front and dots
replaced by underscores, so `controller.api.port` is `OSAPI_CONTROLLER_API_PORT`.
`AutomaticEnv` means every key is reachable that way without being declared, so a
new setting is environment-configurable the moment it has a default.

## The shape

Four top-level sections and a flag.

| Section      | For                                                  |
| ------------ | ---------------------------------------------------- |
| `controller` | the API, the UI, metrics, PKI, notifications         |
| `agent`      | the agent's NATS connection, consumer and PKI        |
| `nats`       | the embedded server, and the streams and buckets     |
| `telemetry`  | tracing and the metrics server                       |
| `debug`      | a boolean, set from the CLI                          |

`agent` is `omitempty`, because a controller-only deployment does not need it. The
same binary reads the same file and takes the half it needs.

## Validation happens before the process starts

`config.Validate` runs the struct through the shared validator, and the validator
registers osapi's own rules first. So a bad value fails at startup with a message
naming the field rather than at the moment the value is first used.

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

`cmd/controller.go` runs the config through go-masker in `PersistentPreRun` before
logging it, so the tags are read rather than decorative. Seven fields carry one.

**The agent does not mask, because it does not log the struct.** It logs named
fields instead, host, port and client name, and never a password. Two different
approaches to the same problem, and the agent's only stays safe as long as nobody
adds a secret to the list of fields it names.

## Where this connects

The two clocks a job runs under, both configured here, are
[the job system](job-system.md).

`controller.ui.enabled`, the one setting an operator has over the dashboard, is
[the embedded UI](ui.md).

The PKI switches that let enforcement be staged across a live fleet are
[agent identity](agent-identity.md).

______________________________________________________________________

Written from `internal/config/` and `cmd/root.go` rather than from a feature.
