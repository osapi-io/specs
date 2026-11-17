# nats-client

`nats-client` wraps the upstream NATS client. It has one package, `pkg/client`,
one constructor and no binary. A consumer keeps one `Client`. Through it, the
consumer gets these parts of NATS:

- the connection
- core publish and subscribe
- JetStream streams and consumers
- key-value buckets
- object stores
- OpenTelemetry spans and metrics for each call to NATS

```go
c := client.New(logger, &client.Options{
    Host: "127.0.0.1",
    Port: 4222,
    Name: "osapi-controller",
    Auth: client.AuthOptions{AuthType: client.NKeyAuth, NKeyFile: "/etc/osapi/seed.nk"},
})
if err := c.Connect(); err != nil {
    return err
}
defer c.Close()
```

The NATS documentation does not tell what the wrapper adds to the upstream
library. It adds these things:

- One `Client` keeps the connection and the JetStream context together.
- Authentication has four declared modes.
- Streams, consumers, key-value buckets and object stores get create-or-update
  helpers.
- Each call to NATS is a method of `Client`. The method takes `ctx` first, and
  then the name of the bucket or the stream. A consumer keeps no JetStream
  handle. `Client` keeps one handle for each bucket and each stream, and asks
  the server for it one time only.
- Each of these methods can make a span and records a metric. Thus a consumer
  that calls NATS only through `Client` gets all of its NATS calls in its traces
  and its metrics.

It does not add a new protocol, a new wire format or its own reconnection
policy.

## It does not hide NATS

Upstream types get to a consumer through the signatures of the wrapper. `KVGet`
returns `jetstream.KeyValueEntry`, a message handler gets `jetstream.Msg`, and
the connection gives `nats.Conn`. Thus this is a convenience layer over NATS. It
is not an abstraction over NATS. A consumer is not isolated from the upstream
library.

The package declares no interface for its own methods, and it returns concrete
types. A consumer declares the interface that it needs, in the package that uses
it, and makes its mocks from that interface. `docs/client/README.md` in the
repository states this.

## Where it sits

`osapi` imports it to connect to the message bus. Nothing else in the
organization depends on it, and it depends on nothing in the organization.

osapi pins a released tag of it. Thus a change to the exported API of
`pkg/client` breaks osapi when somebody updates the pin, not when the change
merges. Merge a rename and its pin update together.

`nats-server` wraps the server end of the same upstream library. A person who
works on the transport of osapi reads the two. Neither imports the other.

The build gets `osapi-justfiles` through a justfile recipe, from `main`, not
from a release. No `go.mod` shows that connection.

## The package (`pkg/client/`)

Each file has one type with one responsibility.

```
types.go             Options, AuthOptions, AuthType, Client
client.go            New
connect.go           connecting and authenticating
connect_wrapper.go   NATSConnWrapper, the only substitutable seam
connection.go        connection state and lifecycle
kv.go                key-value buckets and their keys
objectstore.go       object stores and their objects
stream.go            streams, durable consumers, and reads of a stream
messaging.go         publish, subscribe and consume, with handlers that get ctx
telemetry.go         spans, the metric, and MessageContext
mocks/               generated
```

`NATSConnector` is the only interface that the package declares. With it, a test
can replace the connection. A test cannot replace other parts.

The repository has six examples that you can run: one for each authentication
mode, one for a key-value bucket, and one for a work queue. They are the
documentation in a form that runs. They are not a separate thing to keep
current.

## Authentication

There are four modes. Each needs a different thing from a consumer.

| Mode           | Needs                                                    |
| -------------- | -------------------------------------------------------- |
| `NoAuth`       | nothing                                                  |
| `UserPassAuth` | `Username` and `Password`                                |
| `NKeyAuth`     | `NKeyFile`, the path to an Ed25519 private seed file     |
| `CredsAuth`    | `CredsFile`, a credentials file: a user JWT and its seed |

`AuthType` and `AuthOptions` in `types.go` declare them. If a mode needs a field
and does not get it, it fails at connect time, not at construction.

`CredsAuth` connects a client to a NATS server in operator mode (decentralized
JWT). In that mode, the JWT of each user has its permissions and expiry, and a
new user needs no change on the server. `nats.UserCredentials` reads the file on
each connect. Thus `Connect` first checks that the file exists. It reports a
missing file as `failed to read creds file`, not as the authorization error of
the server.

## Telemetry

`Options.Telemetry` turns on the spans and the metric. It is off by default.
`Options.TracerProvider` and `Options.MeterProvider` select the providers. When
they are nil, the client uses the global providers.

A call makes a span only inside a trace that the caller started. A heartbeat or
the setup of a stream at startup is not in a trace, so it makes no span. A root
span for each of these calls would hide the traces of the requests. Each call
records the histogram `nats.client.operation.duration`, also outside a trace.

| What                 | On the span | On the metric |
| -------------------- | ----------- | ------------- |
| `db.system.name`     | yes         | yes           |
| `db.operation.name`  | yes         | yes           |
| `db.namespace`       | yes         | yes           |
| `error.type`         | no          | on a failure  |
| key, object, subject | yes         | no            |

The metric never has a key, an object name or a subject. These values have no
limit, and a subject can name a host.

`Publish` and `PublishCore` put the trace context in the headers of the message.
`Subscribe` and `Consume` give their handler a `ctx` with that trace. Thus the
work of a handler is a child of the publish. The headers use the global text map
propagator, and the consumer sets it.

A key or an object that is not there is the answer of a read, not a failure. It
does not mark the span as an error.

## What happens when the connection drops

The default of the upstream library applies.

`Connect` gives exactly three options to the library: `nats.Name`, and then
`nats.UserInfo`, `nats.Nkey` or `nats.UserCredentials`, as the mode requires. It
sets no reconnection options. It registers no disconnect, reconnect or closed
handler. Thus the upstream default controls all reconnection, and **a consumer
never gets a notification of a drop or a recovery**, because there is no
callback.

You cannot configure resilience through the `Options` of this wrapper. A
consumer who needs a different operation must change this package.

This page does not give the upstream defaults. They belong to the NATS library
and change with it. Prose about the settings of a different project becomes
incorrect, but it continues to look correct.

## The contract

The contract is the exported API of `pkg/client`: the constructor `New`,
`MessageContext`, 30 `Client` methods and 9 exported types.

An empty bucket is an empty list from `KVKeys` and from `ObjectList`, not an
error. The two methods agree, and a consumer needs no special case. Everything
under `pkg/client/mocks/` is generated and is not part of it.

The contract does not promise these things:

- a retry or reconnection policy of the wrapper
- isolation from the upstream types above
- **stability between releases.** A consumer depends on a tag. A rename on
  `main` gets to the consumer at the next pin update.

## How big it is

There are ten files that are not tests in `pkg/client`, and 30 methods on
`Client`.

## Not covered here

How NATS works. Streams, consumers, key-value and object stores are upstream
concepts. This page tells what the wrapper does with them.

What each of the 30 methods does. They are the contract. The seven documentation
pages under `docs/client/` describe how they operate.

The generated mocks.

If this wrapper has the correct shape for its one consumer. osapi decides that.

______________________________________________________________________

Written from `pkg/client/`.
