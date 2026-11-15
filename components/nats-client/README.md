# nats-client

`nats-client` wraps the upstream NATS client. It has one package, `pkg/client`,
one constructor and no binary. A consumer keeps one `Client`. Through it, the
consumer gets these parts of NATS:

- the connection
- core publish and subscribe
- JetStream streams and consumers
- key-value buckets
- object stores

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

It does not add a new protocol, a new wire format or its own reconnection
policy.

## It does not hide NATS

Upstream types get to a consumer through the signatures of the wrapper. A
message handler gets `jetstream.Msg`, and the connection gives `nats.Conn`. Thus
this is a convenience layer over NATS. It is not an abstraction over NATS. A
consumer is not isolated from the upstream library.

Nothing in the repository says so. A consumer learns it from a signature.

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
types.go             Options, AuthOptions, AuthType
connect.go           connecting and authenticating
connect_wrapper.go   NATSConnWrapper, the only substitutable seam
connection.go        connection state and lifecycle
core.go              core publish and subscribe
jetstream.go         streams
consumer.go          consumers
kv.go                key-value
kv_stream.go         key-value with publish
objectstore.go       object stores
mocks/               generated
```

`NATSConnector` is the only interface that the package declares. With it, a test
can replace the connection. A test cannot replace other parts.

The repository has five examples that you can run: one for each authentication
mode and one for each JetStream pattern. They are the documentation in a form
that runs. They are not a separate thing to keep current.

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

The contract is the exported API of `pkg/client`: one constructor, 25 `Client`
methods and 9 exported types. Everything under `pkg/client/mocks/` is generated
and is not part of it.

The contract does not promise these things:

- a retry or reconnection policy of the wrapper
- isolation from the upstream types above
- **stability between releases.** A consumer depends on a tag. A rename on
  `main` gets to the consumer at the next pin update.

## How big it is

There are eleven files that are not tests in `pkg/client`, and 25 methods on
`Client`.

```sh
find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' | wc -l   # 11
```

## Known limitations

**The leak of upstream types has no documentation.** The design above is
deliberate, but no page states it. A consumer who expects an abstraction learns
the truth from a signature.

## Not covered here

How NATS works. Streams, consumers, key-value and object stores are upstream
concepts. This page tells what the wrapper does with them.

What each of the 25 methods does. They are the contract. The eight documentation
pages under `docs/` describe how they operate.

The generated mocks.

If this wrapper has the correct shape for its one consumer. osapi decides that.

______________________________________________________________________

Written from `pkg/client/`.
