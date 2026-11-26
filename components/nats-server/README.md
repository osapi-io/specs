# nats-server

`nats-server` runs a NATS server in the process of its consumer. It is a
library, not a daemon. It has one package, one constructor, no binary and no
entry point of its own. The server that it starts is a goroutine in a different
program.

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

`osapi` embeds it to run the message bus. The controller and the agents of osapi
use that bus. Nothing else in the organization depends on it, and it depends on
nothing in the organization.

osapi pins a released tag of it. Thus a change to the API of this package breaks
osapi when somebody updates the pin, not when the change merges. Merge a rename
and its pin update together.

`nats-client` wraps the client end of the same upstream library. A person who
works on the transport of osapi reads the two. Neither imports the other.

The build gets `osapi-justfiles` through a justfile recipe, from `main`, not
from a release. No `go.mod` shows that connection.

## The package (`pkg/server/`)

```
server.go           Server, New, Start, Stop
types.go            Options. Embeds *natsserver.Options, adds ReadyTimeout
server_wrapper.go   NATSServerInstance, the interface Start() constructs behind
logger.go           SlogWrapper. NATS's logger interface onto slog
mocks/              generated
```

A consumer keeps one `Server` and calls two methods. `Start` returns an error.
`Stop` returns nothing. A mutex guards the two, so they are safe from different
goroutines.

### `Start()`

```go
natsServer, err := NewNATSServer(s.Opts.Options)   // construct
natsServer.SetLogger(NewSlogWrapper(s.logger),
    s.Opts.Debug, s.Opts.Trace)                    // logger attached first
go natsServer.Start()                              // run
if !natsServer.ReadyForConnections(timeout) {
    natsServer.Shutdown()                          // no server left running
    natsServer.WaitForShutdown()
    return fmt.Errorf("server not ready for connections")
}
```

`Start()` refuses nil options, and a second call before `Stop()`. If the server
does not become ready, `Start()` shuts it down and waits for it before it
returns the error. Thus a failed start leaves no listener and no goroutine.

`Start()` attaches the logger before the server runs. Thus the startup messages
of the server, such as a port that is in use, go to the `slog` handler that
`New` got. A nil logger is `slog.Default()`.

Debug and trace come from `Options.Debug` and `Options.Trace` of the upstream
struct. Both are false by default, so a consumer gets no trace unless it asks.

### `Stop()`

`Stop()` calls `Shutdown()` and then `WaitForShutdown()`, and forgets the
server. When `Stop()` returns, the port and the JetStream store are free. A
second `Stop()` does nothing, and `Start()` can run the server again.

### `Options`

```go
type Options struct {
    *natsserver.Options
    ReadyTimeout time.Duration
}
```

This file has four lines, and it has the largest effect in the repository.
`Options` embeds all of the upstream struct. Thus a consumer configures host,
port, authentication, JetStream and clustering through the upstream fields. An
upstream release changes the API of this package, and no commit here shows it.

For the same reason, operator mode (decentralized JWT) needed no change here.
`nsc generate config --mem-resolver` writes a file. osapi makes the upstream
options from that file with the upstream `ProcessConfigFile`, and gives all of
the options to this package. If osapi copies the fields one by one, it loses the
preloaded account JWTs, because upstream keeps them in an unexported field.
[The transport page of osapi](../osapi/transport.md#who-may-connect) has the
rest.

`ReadyTimeout` is the only field that this package adds. When it is zero,
`Start()` waits `DefaultReadyTimeout`, which is 10 seconds. `Start()` refuses a
negative value.

### `SlogWrapper` (`logger.go`)

NATS logs through its own interface, and `slog` has no trace level.
`NewSlogWrapper(logger)` makes the wrapper. The wrapper sends `Tracef` to
`slog.Debug`. Thus the handler of the consumer cannot tell trace messages from
debug messages.

| NATS      | slog         |
| --------- | ------------ |
| `Noticef` | `slog.Info`  |
| `Warnf`   | `slog.Warn`  |
| `Errorf`  | `slog.Error` |
| `Fatalf`  | `slog.Error` |
| `Debugf`  | `slog.Debug` |
| `Tracef`  | `slog.Debug` |

## What a consumer changes

A consumer sets the log level through its `slog` handler, and debug and trace
through `Options.Debug` and `Options.Trace`. The wrapper formats a message only
when the handler takes its level. It sees the startup messages, because
`Start()` attaches the logger first.

## How big it is

There are four files that are not tests in `pkg/server`, and eight exported
methods.

## Not covered here

How NATS works: clustering, JetStream, accounts and authentication. Also the
fields of the upstream option struct. The two belong to upstream. A copy of the
settings of a different project becomes incorrect, but it continues to look
correct.

The five documentation pages under `docs/`. They cover configuration, lifecycle
and logging for a consumer.

If an embedded NATS server is the correct design for osapi. osapi decides that.

______________________________________________________________________

Written from `pkg/server/`.
