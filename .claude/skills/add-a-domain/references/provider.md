# Provider

The operations layer. Providers run on the agent, not the controller. A provider
receives parameters from the job payload, does the work, and returns a result.

```
CLI -> SDK -> REST API -> job client -> NATS -> agent -> provider
```

Read the reference domain's provider package before writing.

## Which pattern

| Pattern | Writes files | Platform variants | Example |
| --- | --- | --- | --- |
| Direct | no | yes | `node/process`, `node/power` |
| Meta | through `file.Deployer` | yes | `scheduled/cron`, `node/service` |
| Direct-write | itself, via `avfs.VFS` | yes | `node/sysctl` |
| SDK-based | no | no | `container/docker` |

**Meta** providers get SHA tracking, idempotency, drift detection and template
rendering from the file provider, and store domain metadata in
`FileState.Metadata`. Depend on the narrow interface, not the implementation:

```go
type Deployer interface {
    Deploy(ctx context.Context, req DeployRequest) (*DeployResult, error)
    Undeploy(ctx context.Context, req UndeployRequest) (*UndeployResult, error)
}
```

**Direct-write** providers own their files and mark them with an `osapi-`
filename prefix so they can tell managed files from hand-written ones.

**SDK-based** providers talk to an external API, so there is nothing
OS-specific to vary. Availability is checked at startup instead, such as a
Docker daemon ping.

## Files

```
internal/provider/{category}/{domain}/
  types.go              Provider interface, domain types, compile-time checks
  debian.go             Debian family: Ubuntu, Debian, Raspbian
  debian_{operation}.go one file per large operation
  debian_docker.go      container-aware variant, when behaviour differs
  darwin.go             macOS stub
  linux.go              generic Linux stub
  mocks/generate.go     //go:generate mockgen directive
```

`types.go` holds only types. A function belongs in a file named for what it
does. Categorized domains live under `internal/provider/{category}/{domain}/`,
uncategorized ones directly under `internal/provider/{domain}/`.

## Interface

```go
// types.go, package {domain}
type Provider interface {
    List(ctx context.Context) ([]Entry, error)
    Get(ctx context.Context, name string) (*Entry, error)
    Create(ctx context.Context, entry Entry) (*CreateResult, error)
    Update(ctx context.Context, entry Entry) (*UpdateResult, error)
    Delete(ctx context.Context, name string) (*DeleteResult, error)
}
```

Context first on every method. Mutation results carry `Changed bool`, and
result types carry `Error string` where per-operation errors are reported.

## Idempotency, which is the contract

Desired-state semantics, as Ansible has them.

| Operation | Resource exists | Resource absent |
| --- | --- | --- |
| Create | `Changed: false`, no error | creates it |
| Update | updates it | error, not found |
| Delete | removes it | `Changed: false`, no error |

`ErrUnsupported` is a fourth outcome, not a failure: the agent maps it to
`StatusSkipped`, which tells the caller the operation does not exist on that
host rather than that it broke.

```go
// darwin.go
func (d *Darwin) List(
    _ context.Context,
) ([]Entry, error) {
    return nil, fmt.Errorf("{domain}: %w", provider.ErrUnsupported)
}
```

Test that every stub method returns `ErrUnsupported`, on Darwin and on Linux.

## Naming

| Struct | Constructor | Files |
| --- | --- | --- |
| `Debian` | `NewDebianProvider(...)` | `debian.go`, `debian_{op}.go` |
| `DebianDocker` | `NewDebianDockerProvider(...)` | `debian_docker.go` |
| `Darwin` | `NewDarwinProvider(...)` | `darwin.go` |
| `Linux` | `NewLinuxProvider()` | `linux.go` |
| `Client` | `New()`, `NewWithClient(c)` | `{domain}.go` |

`DebianDocker` either embeds `Debian`, delegating reads and overriding writes,
or stands alone. `node/host` embeds and blocks `UpdateHostname`; `network/dns`
stands alone and reads `/etc/resolv.conf` directly. The agent chooses via
`platform.IsContainer()`, from `pkg/sdk/platform`.

## Facts

Embed `provider.FactsAware` in every concrete struct and assert the contract at
compile time:

```go
var _ Provider = (*Debian)(nil)
var _ provider.FactsSetter = (*Debian)(nil)

type Debian struct {
    provider.FactsAware
    logger *slog.Logger
    fs     avfs.VFS
}
```

Facts reach the provider through `provider.WireProviderFacts()` in
`internal/agent/agent.go`, and reach file templates as `{{ .Facts.os_family }}`.
A provider that is constructed but never passed to that call has nil facts at
runtime.

## Validating input here as well

The API validates, and the provider validates again wherever a value becomes a
path, a filename, or a command argument. The API is one caller; a job replayed
from KV is another.

- Reject a name or key that escapes its directory, and anything with a
  separator, whitespace or control character in it. `node/sysctl` and
  `node/certificate` carry the pattern.
- Reject a value that could add a second line to a file the provider writes.
- Pass secrets on stdin, never in arguments: arguments are logged and visible in
  the process list. `RunPrivilegedCmdWithStdin` exists for this.
- Put `--` before a user-supplied name in a command, so a name starting with `-`
  cannot become an option.

## Filesystem and commands

Use [avfs](https://github.com/avfs/avfs): `memfs.New()` in tests, `failfs.New()`
for error injection. Never `afero`, and never the `os` package directly in a
provider.

Commands go through `internal/exec`. Prefer the variants that take a timeout,
and write a file by rendering to a temporary path and renaming, so a crash
cannot leave a half-written config behind.

## Tests

Conventions are in the repository's `CONTRIBUTING.md` under Testing. What is
specific here:

- One `*_public_test.go` suite per production file, one suite method per method
  under test, cases as table rows with a `validateFunc`.
- Mock `FileDeployer`, `KeyValue` and `ObjectStore` from `{package}/mocks/`,
  generated with mockgen and committed. Never hand-write a double for an
  interface this organization defines.
- Cover the idempotency rows above explicitly: the create-when-present and
  delete-when-absent paths are the ones that regress silently.
- Cover every rejection added above, asserting no command ran and no file was
  written. A gomock controller fails an unexpected call, which is the assertion.
