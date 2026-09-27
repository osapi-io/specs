# Provider

The operations layer. Providers run on the agent, not the controller. A provider
receives parameters from the job payload, does the work, and returns a result.

```
CLI -> SDK -> REST API -> job client -> NATS -> agent -> provider
```

## The contract is in the corpus, not here

Every rule a provider obeys is stated in
[001-provider-contract](../../../../components/osapi/specs/001-provider-contract/spec.md).
Read it before writing one. This file holds only what that specification does
not: where the files go, what they are called, and the scaffolding to start
from.

That split is deliberate, and the specification requires it (FR-016). A rule
restated here would drift from the one in the corpus, and the copy an agent
happened to load would win.

| What you need to know                                     | Where    |
| --------------------------------------------------------- | -------- |
| A provider is the operations layer, and what it returns    | FR-001-3 |
| The idempotency contract, as a table of operation outcomes | FR-004   |
| `ErrUnsupported` is a fourth outcome, not a failure        | FR-005   |
| The four implementation patterns, and how to choose        | FR-006   |
| Platform variants, and how the agent selects one           | FR-007   |
| How a provider obtains host facts                          | FR-008   |
| Why the provider validates what the API already validated  | FR-009   |
| Secrets reach a command without appearing in it            | FR-010   |
| A caller's value never becomes an option                   | FR-011   |
| Filesystem access, and why not the `os` package            | FR-012   |
| A file is not written in place                             | FR-013   |
| The testing obligations that belong to the provider        | FR-014   |
| What a provider does not touch                             | FR-015   |

Read the reference domain's provider package alongside it. The specification
says what must hold; an existing domain shows it holding.

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

## Naming

| Struct         | Constructor                  | Files                          |
| -------------- | ---------------------------- | ------------------------------ |
| `Debian`       | `NewDebianProvider(...)`     | `debian.go`, `debian_{op}.go`  |
| `DebianDocker` | `NewDebianDockerProvider(...)` | `debian_docker.go`           |
| `Darwin`       | `NewDarwinProvider(...)`     | `darwin.go`                    |
| `Linux`        | `NewLinuxProvider()`         | `linux.go`                     |
| `Client`       | `New()`, `NewWithClient(c)`  | `{domain}.go`                  |

`DebianDocker` either embeds `Debian`, delegating reads and overriding writes,
or stands alone. `node/host` embeds and blocks `UpdateHostname`; `network/dns`
stands alone and reads `/etc/resolv.conf` directly.

## Scaffolding

The shapes to start from. What they have to satisfy is FR-002, FR-003 and
FR-008.

```go
// types.go, package {domain}
type Provider interface {
    List(ctx context.Context) ([]Entry, error)
    Get(ctx context.Context, name string) (*Entry, error)
    Create(ctx context.Context, entry Entry) (*CreateResult, error)
    Update(ctx context.Context, entry Entry) (*UpdateResult, error)
    Delete(ctx context.Context, name string) (*DeleteResult, error)
}

var _ Provider = (*Debian)(nil)
var _ provider.FactsSetter = (*Debian)(nil)

type Debian struct {
    provider.FactsAware
    logger *slog.Logger
    fs     avfs.VFS
}
```

A stub for a platform that does not support the domain:

```go
// darwin.go
func (d *Darwin) List(
    _ context.Context,
) ([]Entry, error) {
    return nil, fmt.Errorf("{domain}: %w", provider.ErrUnsupported)
}
```

A meta provider depends on the narrow interface rather than the file provider's
implementation:

```go
type Deployer interface {
    Deploy(ctx context.Context, req DeployRequest) (*DeployResult, error)
    Undeploy(ctx context.Context, req UndeployRequest) (*UndeployResult, error)
}
```

## Mocks

```
internal/provider/{category}/{domain}/mocks/generate.go
```

One `//go:generate go tool go.uber.org/mock/mockgen` directive per interface the
domain defines, output committed. Never hand-write a double for an interface this
organization defines: `just generate` regenerates them, and a hand-written one
silently stops matching the interface it stands in for.
