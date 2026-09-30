# nats-client

`nats-client` wraps the upstream NATS client. One package, `pkg/client`, one
constructor, no binary. A consumer holds one `Client` and reaches connection,
core publish and subscribe, JetStream streams, consumers, key-value buckets and
object stores through it.

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

What it adds over using the upstream library directly is the only part a
consumer cannot read in NATS's own documentation. One `Client` holds the
connection and the JetStream context together. Authentication reduces to three
declared modes. Streams, consumers, key-value buckets and object stores get
create-or-update helpers.

What it does not add: a new protocol, a new wire format, and no reconnection
policy of its own.

## It does not hide NATS

Upstream types reach a consumer through the wrapper's signatures. `jetstream.Msg`
arrives in a message handler, and `nats.Conn` is reachable through the
connection. So this is a convenience layer over NATS rather than an abstraction
over it, and a consumer who expected to be insulated from the upstream library
is not.

Nothing in the repository says so. A consumer finds out by reading a signature.

## Where it sits

`osapi` imports it to talk to the message bus. Nothing else in the organization
depends on it, and it depends on nothing in the organization.

osapi pins it by commit rather than by tag, so a change to `pkg/client`'s
exported surface breaks osapi at the bump rather than at the change. Land a
rename and its bump together.

`nats-server` wraps the server end of the same upstream library. Anybody working
on osapi's transport reads both. Neither imports the other.

The build fetches `osapi-justfiles` through a justfile recipe, from `main` rather
than from a release. That edge is in no `go.mod`.

## The package (`pkg/client/`)

One type with one responsibility per file.

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

`NATSConnector` is the only interface the package declares. It exists so the
connection can be substituted in tests, and nothing else can be.

Five runnable examples ship alongside, one per authentication mode and one per
JetStream pattern. They are the executable form of the documentation rather than
an extra to keep in step.

## Authentication

Three modes, and each needs something different from a consumer.

| Mode           | Needs                                                  |
| -------------- | ------------------------------------------------------ |
| `NoAuth`       | nothing                                                |
| `UserPassAuth` | `Username` and `Password`                              |
| `NKeyAuth`     | `NKeyFile`, the path to an Ed25519 private seed file   |

`AuthType` and `AuthOptions` in `types.go` declare them. A mode that needs a
field and does not get it fails at connect time rather than at construction.

## What happens when the connection drops

Whatever the upstream library does by default.

`Connect` passes exactly three options through: `nats.Name`, and then
`nats.UserInfo` or `nats.Nkey` depending on the mode. It sets no reconnection
options, and it registers no disconnect, reconnect or closed handler. So the
upstream default governs reconnection entirely, and **a consumer is never
notified when a drop or a recovery happens**, because there is no callback to
receive it.

Resilience is not configurable through this wrapper's `Options`. A consumer who
needs different behaviour has to change this package.

The upstream defaults themselves are not restated here. They belong to the NATS
library and change with it, and prose about another project's settings drifts
while continuing to read as authoritative.

## The contract

The exported surface of `pkg/client`: one constructor, 25 `Client` methods, 9
exported types. Everything under `pkg/client/mocks/` is generated and is not part
of it.

What the contract does not promise: no retry or reconnection policy of the
wrapper's own, no insulation from the upstream types above, and **no stability
beyond the commit a consumer pins.** The repository publishes no tags, so a
consumer depends on a commit rather than on a version, and a rename on `main`
reaches them at their next bump.

## What was measured

At `cfe12f6`, 2026-09-30.

| Measurement                    | Value | Command                                                                                                             |
| ------------------------------ | ----: | ------------------------------------------------------------------------------------------------------------------- |
| Go files                       |    33 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                |
| Go files excluding tests       |    20 | `find . -name '*.go' -not -path './.git/*' -not -name '*_test.go' \| wc -l`                                         |
| Non-test files in `pkg/client` |    11 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                                          |
| `Client` methods               |    25 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^func \(c \*Client\) [A-Z]' {} + \| wc -l` |
| Exported types                 |     9 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^type [A-Z]' {} + \| wc -l`        |
| Exported functions             |     1 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^func [A-Z]' {} + \| wc -l`        |
| Interfaces                     |     1 | `find pkg/client -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^type [A-Z][A-Za-z]* interface' {} + \| wc -l` |
| Documentation pages            |     8 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                      |
| README lines                   |    62 | `wc -l README.md`                                                                                                   |
| Runnable examples              |     5 | `ls -d examples/*/ \| wc -l`                                                                                        |

Both exclusions are load-bearing. `docs/node_modules/` holds a vendored
`README.md`, so dropping the path exclusion returns 9 pages. Fourteen `*TestSuite`
types live in test files, so dropping the name exclusion returns 23 exported types
against a real 9.

## Known limitations

**No published tags.** A consumer cannot name a version, only a commit. Nothing
is wrong with the code; what is missing is a way to ask for a known one.

**The upstream-type leak is undocumented.** The design above is deliberate, and
no page states it, so a consumer expecting an abstraction learns otherwise from a
signature.

## Not covered here

How NATS itself works. Streams, consumers, key-value and object stores are
upstream concepts, and this describes what the wrapper does with them.

What each of the 25 methods does. They are the contract; the eight documentation
pages under `docs/` describe their behaviour.

The generated mocks.

Whether this wrapper is the right shape for its one consumer. That is osapi's
question.

______________________________________________________________________

Traced to `specs/001-nats-client-baseline/`, which inventoried the repository at
`cfe12f6`.
