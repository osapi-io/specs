# nats-server

`nats-server` runs a NATS server inside its consumer's process. It is a library,
not a daemon: one package, one constructor, no binary, no entry point of its own.
The server it starts is a goroutine in somebody else's program.

```go
srv := server.New(logger, &server.Options{
    Options:      &natsserver.Options{Host: "127.0.0.1", Port: 4222},
    ReadyTimeout: 5 * time.Second,
})
if err := srv.Start(); err != nil {
    return err
}
defer srv.Stop()
```

## Where it sits

`osapi` embeds it to run the message bus its controller and agents talk over.
Nothing else in the organization depends on it, and it depends on nothing in the
organization.

osapi pins it by commit rather than by tag, so a change to this package's surface
breaks osapi at the bump rather than at the change. Land a rename and its bump
together.

`nats-client` wraps the client end of the same upstream library. Anybody working
on osapi's transport reads both; neither imports the other.

The build fetches `osapi-justfiles` through a justfile recipe, from `main` rather
than from a release. That edge is in no `go.mod`.

## The package (`pkg/server/`)

```
server.go           Server, New, Start, Stop
types.go            Options — embeds *natsserver.Options, adds ReadyTimeout
server_wrapper.go   NATSServerInstance, the interface Start() constructs behind
logger.go           SlogWrapper — NATS's logger interface onto slog
mocks/              generated
```

A consumer holds one `Server` and calls two methods. `Start` returns an error;
`Stop` returns nothing.

### `Start()`

```go
natsServer, err := NewNATSServer(s.Opts.Options)   // construct
go natsServer.Start()                              // run
if !natsServer.ReadyForConnections(s.Opts.ReadyTimeout) {
    return fmt.Errorf("server not ready for connections")
}
natsServer.SetLogger(slogWrapper, true, true)       // logging attached here
```

The logger is attached last, after the server is already accepting connections.
Anything the server logs while starting goes to NATS's own default logger, not to
the `slog` handler passed to `New`. A consumer debugging a server that never
became ready finds their logger empty and the reason on stderr.

`SetLogger`'s second and third arguments are debug and trace. Both are literals.
Nothing in `Options` or `New` reaches them, so every embedded server runs with
trace logging on.

### `Options`

```go
type Options struct {
    *natsserver.Options
    ReadyTimeout time.Duration
}
```

Four lines, and the most consequential file in the repository. The upstream
option struct is embedded whole, so a consumer configures host, port,
authentication, JetStream and clustering through upstream's fields, and an
upstream release changes this package's surface with no commit here.

`ReadyTimeout` is the one field this package adds and it has no default. `New`
performs no defaulting, so leaving it unset passes a zero duration to
`ReadyForConnections`. All four examples set it to five seconds.

### `SlogWrapper` (`logger.go`)

NATS logs through its own interface; `slog` has no trace level. The wrapper maps
`Tracef` onto `slog.Debug`, so trace and debug arrive indistinguishable at the
consumer's handler.

| NATS      | slog          |
| --------- | ------------- |
| `Noticef` | `slog.Info`   |
| `Warnf`   | `slog.Warn`   |
| `Errorf`  | `slog.Error`  |
| `Fatalf`  | `slog.Error`  |
| `Debugf`  | `slog.Debug`  |
| `Tracef`  | `slog.Debug`  |

## What a consumer cannot change

Logging verbosity, and whether startup is observable. Both are settled inside
`Start()` and neither is reachable from `Options`. A consumer who needs quieter
logs or wants to see the server come up has to change this package.

## Known limitations

Three, and each needs a change here rather than a workaround in a consumer.

**Trace logging cannot be turned off.** `SetLogger(wrapper, true, true)` — see
`Start()` above. `docs/server/logging.md` documents where trace output lands and
not that it is always on.

**Startup logging bypasses the consumer's logger.** The attachment order in
`Start()`. `SetLogger` appears in no documentation page.

**`ReadyTimeout` has no default.** `docs/server/configuration.md` lists the field
with a type and a description; its table has no Default column, so there is
nowhere for the absence to be recorded and a reader sees an example value and has
no reason to ask.

## What was measured

At `7ac142e`, 2026-09-30.

| Measurement                    | Value | Command                                                                                            |
| ------------------------------ | ----: | -------------------------------------------------------------------------------------------------- |
| Go files                       |    12 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                               |
| Go files excluding tests       |    10 | the same, plus `-not -name '*_test.go'`                                                            |
| Non-test files in `pkg/server` |     4 | `find pkg/server -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                         |
| Exported functions             |     1 | the same, with `grep -hE '^func [A-Z]'`                                                            |
| Exported methods               |     8 | the same, with `grep -hE '^func \([a-z]+ \*[A-Za-z]+\) [A-Z]'`                                     |
| Exported types                 |     4 | the same, with `grep -hE '^type [A-Z]'`                                                            |
| Interfaces                     |     1 | the same, with `grep -hE '^type [A-Z][A-Za-z]* interface'`                                         |
| Documentation pages            |     5 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                     |
| Runnable examples              |     4 | `ls -d examples/*/ \| wc -l`                                                                       |

## Not covered here

How NATS itself works — clustering, JetStream, accounts, authentication — and the
fields of the upstream option struct. Both are upstream's, and restating another
project's settings drifts while continuing to read as authoritative.

The five documentation pages under `docs/`, which cover configuration, lifecycle
and logging for a consumer.

Whether embedding a NATS server is the right design for osapi. That is osapi's
question.

______________________________________________________________________

Traced to `specs/001-nats-server-baseline/`, which inventoried the repository at
`7ac142e`.
