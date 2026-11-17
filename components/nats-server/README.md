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
`Stop` returns nothing.

### `Start()`

```go
natsServer, err := NewNATSServer(s.Opts.Options)   // construct
go natsServer.Start()                              // run
if !natsServer.ReadyForConnections(s.Opts.ReadyTimeout) {
    return fmt.Errorf("server not ready for connections")
}
natsServer.SetLogger(slogWrapper, true, true)       // logger attached here
```

`Start()` attaches the logger last, after the server accepts connections. Thus
the log messages of the server during startup go to the default logger of NATS.
They do not go to the `slog` handler that `New` got. If a server never becomes
ready, the logger of the consumer is empty, and the reason is on stderr.

The second and third arguments of `SetLogger` are debug and trace. The two are
literals. Nothing in `Options` or `New` changes them. Thus each embedded server
runs with trace logging on.

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

`ReadyTimeout` is the only field that this package adds, and it has no default.
`New` sets no defaults. Thus if you do not set it, `ReadyForConnections` gets a
zero duration. All four examples set it to five seconds.

### `SlogWrapper` (`logger.go`)

NATS logs through its own interface, and `slog` has no trace level. The wrapper
sends `Tracef` to `slog.Debug`. Thus the handler of the consumer cannot tell
trace messages from debug messages.

| NATS      | slog         |
| --------- | ------------ |
| `Noticef` | `slog.Info`  |
| `Warnf`   | `slog.Warn`  |
| `Errorf`  | `slog.Error` |
| `Fatalf`  | `slog.Error` |
| `Debugf`  | `slog.Debug` |
| `Tracef`  | `slog.Debug` |

## What a consumer cannot change

A consumer cannot change the log level, or see the startup. `Start()` decides
the two, and `Options` cannot change either. A consumer who needs fewer log
messages, or who wants to see the server start, must change this package.

## Known limitations

There are three. Each needs a change here, not a workaround in a consumer.

**You cannot turn off trace logging.** The cause is
`SetLogger(wrapper, true, true)`, which `Start()` above shows.
`docs/server/logging.md` tells where trace output goes. It does not tell that
trace is always on.

**Startup logging does not go to the logger of the consumer.** The attachment
order in `Start()` causes this. No documentation page names `SetLogger`.

**`ReadyTimeout` has no default.** `docs/server/configuration.md` lists the
field with a type and a description. Its table has no Default column, so there
is no location to record the missing default. A reader sees an example value
next to the field and has no reason to ask.

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
