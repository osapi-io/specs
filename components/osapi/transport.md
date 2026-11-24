# The message bus

In osapi, all communication that is not a single HTTP request goes over NATS.
These are all subjects and buckets on one bus:

- the queue that the [job system](job-system.md) describes
- the registration and facts that [agent identity](agent-identity.md) uses
- the [audit trail](audit.md)

**osapi runs the bus itself.** `server.New` in `internal/bus/server/server.go`
starts a NATS server as a goroutine in the process of the controller, through
[nats-server](../nats-server/README.md). It then connects to it through
[nats-client](../nats-client/README.md). The two wrappers are separate
repositories, and neither knows that the other exists. osapi is where they come
together.

Thus there is no broker to install or operate. The cost: the bus stops when the
process that has it stops. `server.New` returns an error if the server does not
start, or if it cannot configure JetStream, and the start command calls
`LogFatal`. Thus a controller that cannot start a bus does not start in a
degraded state.

You can also start the bus alone. `osapi nats start` runs the same function
without a controller. A deployment uses this to separate the bus from the API.

## What lives on it

| Name             | Kind         | Holds                                            |
| ---------------- | ------------ | ------------------------------------------------ |
| `JOBS`           | stream       | the job notifications an agent consumes          |
| `job-queue`      | KV bucket    | job definitions and their status events          |
| `job-responses`  | KV bucket    | the signed result an agent writes back           |
| `agent-registry` | KV bucket    | registrations, the only thing targeting resolves |
| `agent-facts`    | KV bucket    | what an agent gathers on its own schedule        |
| `agent-state`    | KV bucket    | drain flags and timeline events                  |
| `file-objects`   | object store | file bodies too large for a KV value             |
| `AUDIT`          | stream       | the audit entries                                |

The life of a job uses two buckets, not one. This is deliberate. The controller
writes a definition and an agent reads it. The agent writes a response and the
controller reads it. With two buckets, neither side writes where the other side
writes. Their TTL is not separate. [The job system](job-system.md) explains
this.

## Two osapi deployments can share one server

None of the names above is fixed. `job.Init` in `internal/job/subjects.go` takes
a namespace. An empty namespace keeps the default `jobs.query` and
`jobs.modify`. A value goes at the start. Thus `osapi` gives `osapi.jobs.query`.

```go
Init("")      // jobs.query, jobs.modify
Init("osapi") // osapi.jobs.query, osapi.jobs.modify
```

Bucket and stream names use the same namespace in a different way.
`ApplyNamespaceToInfraName` joins with a hyphen, not a dot, because a KV bucket
name cannot contain a dot. Thus the namespace `osapi` changes `job-queue` to
`osapi-job-queue`.

Note that one setting has two mechanisms. A subject uses dots, and a bucket name
cannot. Thus the same namespace has two shapes. A person who adds a third kind
of NATS object must select one.

## Who may connect

osapi runs its own NATS server, or connects to a server that somebody else runs.
You configure authentication on each side separately.

| Side                               | Where                                     | Modes                                   |
| ---------------------------------- | ----------------------------------------- | --------------------------------------- |
| osapi's own server                 | `nats.server.auth`                        | `none`, `user_pass`, `nkey`, `operator` |
| a client: the controller, an agent | `controller.nats.auth`, `agent.nats.auth` | `none`, `user_pass`, `nkey`, `creds`    |

**Operator mode is the decentralized JWT model of NATS**, and it is the correct
model for a fleet. An operator signs accounts. An account signs users. The JWT
of each user has its own permissions and expiry.

Each osapi process is its own user: the setup and heartbeat of the server, the
controller, and each agent. To add a host, give it a credential. The
configuration of the server does not change. The server refuses a connection
without a credential that the account signed.

On the server of osapi, `auth.type: operator` takes two files:

- `resolver_file`: the server half of the operator. It has the JWT of the
  operator, the system account and the JWT of each account, as
  `nsc generate config --mem-resolver` writes it. osapi reads it with the config
  parser of NATS. It starts the server from the options that the parser returns,
  and then sets host, port and JetStream on them. It does not copy the fields
  one by one, because NATS keeps the preloaded account JWTs in a field that
  osapi cannot get to.
- `creds_file`: the user for the setup and heartbeat connections of the server.
  The setup connection makes the streams and buckets. Thus it must authenticate,
  as each other connection does.

A client uses `auth.type: creds` with a `creds_file`, which has the JWT and seed
of a user. When osapi does not run the server, `osapi nats setup` makes the
streams and buckets of osapi with the connection of the controller. It is the
one place that creates a bucket from the config, or changes the settings of one
that exists.

The agent and the controller each connect with their own config, and
`jobclient.Connect` opens the job, registry, facts and state buckets. It binds
to a bucket that exists, and creates one only when it is missing. It never
changes the settings of a bucket that exists. Before osapi-io/osapi#1096, each
connection updated each bucket from its own config. The lab hub sets
`nats.kv.ttl: 1h` and the agents set no TTL, so the maximum age of the job queue
changed at each connection. Each change to one hour removed each job older than
one hour at once.

`nsc`, the NATS tool, makes the operator, the accounts and the users. osapi only
reads the files. [osapi-lab](../osapi-lab/README.md#nats-in-operator-mode) lists
the exact commands, and the Ansible that runs them.

You cannot make a credential narrower than the bucket. An agent needs its own
job subjects. It also needs the JetStream API and the key-value buckets that it
reads and writes. NATS controls key-value access for each bucket, not for each
key. Thus you can limit the NATS permissions of a host to its subjects and those
buckets, and not more.

**Not built yet: osapi gives credentials itself.** Now an operator must learn
`nsc`. osapi can give credentials itself, with commands such as
`osapi nats operator init` and `osapi nats creds add --name agent-web-01`. Then
a user does not need `nsc`. This work waits until the lab runs operator mode
with `nsc`.

## The streams are encrypted on the disk

The embedded server can encrypt each stream and bucket that it keeps in
`store_dir`. The key is a file that the config names:

```yaml
nats:
  server:
    store_dir: /var/lib/osapi/jetstream
    jetstream:
      key_file: /etc/osapi/nats/jetstream.key
```

`server.New` reads the file and sets `JetStreamKey` in the options of the
server. NATS derives a key for each account from it, and encrypts each file
store with ChaCha20-Poly1305, its default cipher. With no `key_file`, the server
does not encrypt, as before.

`osapi nats key create` makes the key, on the NATS host. It reads `key_file`
from the config, writes 32 random bytes as hex to it with mode `0600`, and makes
its directory with mode `0700`. It refuses to write a file that exists, because
a new key in place of the old key makes each stream unreadable.

```bash
osapi nats key create -f /etc/osapi/osapi.yaml
```

Four things can surprise you:

- **A store with no encryption becomes encrypted.** When a server with a key
  starts on a `store_dir` that has plain files, NATS encrypts each block as it
  loads it. You do not delete the store first.
- **Only the accounts that the server loads become encrypted.** NATS keeps each
  account in its own directory under `store_dir`. A directory of an account that
  the server no longer has stays plain. The lab hub had a `$G` directory from
  before it used operator mode, with plain JSON in it, after each other
  directory was encrypted. Remove such a directory yourself.
- **Only file storage is encrypted.** A stream or a bucket with
  `storage: memory` is not on the disk, so the key does not apply to it.
- **The key is the data.** If the key is lost, or a different key is set, NATS
  cannot load the streams, and the setup of osapi fails to create them again.
  The server does not start, and the files stay on the disk. Keep a copy of the
  key apart from the backup of `store_dir`.

**osapi does not rotate the key.** The rotation of NATS is `JetStreamOldKey`:
the server starts with the new key and the old key, and writes the store again
with the new key. In NATS v2.15.3, the store of a durable consumer opens its key
only with the new key. Thus a stream with a durable consumer does not load, and
the `JOBS` stream has durable consumers. A KV bucket rotates, and `JOBS` does
not. [nats-server #8884](https://github.com/nats-io/nats-server/issues/8884)
reports it, and [osapi #1274](https://github.com/osapi-io/osapi/issues/1274)
adds `old_key_file` when NATS fixes it.

The key protects the files from a person who reads the disk or a backup. It does
not protect a value from a NATS user, because the server decrypts each message
for each user that can read the stream. [Secrets](secrets.md) has the design
that also encrypts each secret for its user.

The key is for the embedded server only. A NATS server that osapi does not run
has its own `jetstream { key }` setting, and `osapi nats setup` does not change
it.

## Nothing on the bus is trusted because it arrived

A job and a response both go as a `SignedEnvelope`, in `internal/job/types.go`.
The envelope has an Ed25519 signature over the payload. An agent verifies it
before it acts. The controller verifies it before it records the result.

Publish access to NATS puts a message on a subject. It does not make the message
run. Thus [agent identity](agent-identity.md) can say that only enrollment
changes a key, and that is true.

## What osapi cannot control from here

The two wrapper repositories decide three things. A consumer of either wrapper
cannot change them. This page records them because a person who debugs the bus
looks here, and because osapi is the only consumer of the two wrappers.

**Trace logging is on, and you cannot turn it off.** `Start()` in `nats-server`
calls `SetLogger(wrapper, true, true)` with two literals. Thus each embedded
server runs with debug and trace logging on. Nothing in the configuration of
osapi can change it.

**Startup log messages do not go to the logger of osapi.** The same `Start()`
attaches the logger after the server accepts connections. Thus the server sends
its startup messages to the default logger of NATS. If the bus of a controller
never becomes ready, the handler that osapi gave has no record of the reason.

**osapi never gets a notification when the connection drops.** `nats-client`
sets no reconnection options. It registers no disconnect, reconnect or closed
handler. osapi gives only host, port, auth and a name. The default reconnection
of the upstream library still applies, so the connection recovers after a short
outage. But there is no notification. Thus osapi cannot:

- log a drop
- report a drop on `/health`
- tell a slow request from a bus that went away and came back

To change any of the three, change the wrapper, not this repository.

## Where this connects

[The job system](job-system.md) tells what the bus carries, and why
at-least-once delivery has an effect on all later steps.
[Agent identity](agent-identity.md) tells what the signatures protect.
[Configuration](configuration.md) tells where the namespace, the bucket names,
the auth mode and the key of the store come from.

______________________________________________________________________

Written from `internal/bus/server/server.go`, `internal/cli/commands/natskey/`,
`internal/bus/setup.go`, `cmd/nats_setup.go`, `internal/bus/bus.go`,
`internal/job/subjects.go`, `internal/job/config.go` and
`internal/job/types.go`.
